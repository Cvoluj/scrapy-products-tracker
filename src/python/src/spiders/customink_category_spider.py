import json
import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.project import get_project_settings
from items import ProductItem
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback


class CustominkCategorySpider(TaskToMultipleResultsSpider):
    """
    Scrapy spider designed to extract product URLs from Customink.com category pages using the Algolia API.

    Leverages RabbitMQ for task management and coordination with other spiders.
    """

    name = "customink_category_spider"
    start_urls = "https://www.customink.com"
    domain = "www.customink.com"
    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        """
        Initializes the spider, constructs necessary queue names, and sets up headers for Algolia API calls.
        """

        super(CustominkCategorySpider, self).__init__(*args, **kwargs)
        self.task_queue_name = (f'{self.project_settings.get("RMQ_DOMAIN_QUEUE_MAP").get(self.domain)}'
                                f'_category_task_queue')
        self.result_queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")
        self.reply_to_queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")
        self.headers = {
            "x-algolia-api-key": self.project_settings.get("CUSTOMINK_SPIDER_API_KEY"),
            "x-algolia-application-id": self.project_settings.get("CUSTOMINK_SPIDER_APPLICATION_ID")
        }

    def next_request(self, _delivery_tag, msg_body):
        """
        Retrieves the next request URL from a RabbitMQ message and initiates an API request with appropriate metadata.

        Args:
            _delivery_tag (str): Delivery tag of the message.
            msg_body (str): Message body containing the JSON data.

        Returns:
            scrapy.Request: A Scrapy Request object for the API call.
        """

        data = json.loads(msg_body)
        return scrapy.Request(url=data["url"],
                              callback=self.api_request,
                              meta={"url": data["url"],
                                    "page": 0,
                                    "position": 0,
                                    "session": data["session"]},
                              errback=self.errback,
                              dont_filter=True)

    @rmq_callback
    def api_request(self, response):
        """
        Constructs an Algolia API request to retrieve product information for the given category URL and page number.

        Args:
            response (scrapy.Response): Scrapy response object (used to access meta data from the previous request).

        Yields:
            scrapy.Request: A Scrapy Request object targeting the Algolia API endpoint.
        """

        api_url = 'https://s0rxn4tv6t-dsn.algolia.net/1/indexes/*/queries'
        payload = {
            "requests": [
                {
                    "indexName": "prod_styles",
                    "params": f"clickAnalytics=true&facetFilters=%5B%5B%22sort_by%3Anone%22%5D%5D&facets=%5B%22*%22%5D&filters=status%3A%20active%20OR%20status%3A%20inactive%20AND%20categories.id%3A%20{response.meta['url'].split('/')[-1]}&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=42&maxValuesPerFacet=100&page={response.meta['page']}&query=&tagFilters=&userToken=anonymous-a2866a73-bd83-424f-a295-6bb37a0ef0fb"
                },
                # These parameters are also passed in the browser, but the spider also works without them
                # {
                #     "indexName": "prod_styles",
                #     "params": f"analytics=false&clickAnalytics=false&facets=sort_by&filters=status%3A%20active%20OR%20status%3A%20inactive%20AND%20categories.id%3A%20{response.meta['url'].split('/')[-1]}&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=0&maxValuesPerFacet=100&page={response.meta['page']}&query=&userToken=anonymous-a2866a73-bd83-424f-a295-6bb37a0ef0fb"
                # }
            ]
        }
        yield scrapy.Request(url=api_url,
                             callback=self.parse,
                             body=json.dumps(payload),
                             method='POST',
                             headers=self.headers,
                             errback=self.errback,
                             meta=response.meta,
                             dont_filter=True
                             )

    @rmq_callback
    def parse(self, response):
        """
        Parses the response from the Algolia API and extracts product information.

        This method extracts product URLs and other relevant data from the JSON response received from the Algolia
        API. It iterates through each product hit and populates a `ProductItem` instance with the extracted data,
        including the product URL and its position within the current result set.

        The method also checks for additional pages of results. If more products are available on subsequent pages
        (based on the total hit count (`nbHits`) and the current position (`position`)), it generates a new Scrapy
        Request to fetch the next page using the `api_request` method.

        Args:
            response (scrapy.Response): The Scrapy response object containing the JSON data from the Algolia API.

        Yields:
            ProductItem: A populated `ProductItem` instance for each product extracted from the response.
            scrapy.Request: A new Scrapy Request object to fetch the next page of results (if available).
        """

        item = ProductItem()
        position = response.meta['position']

        resp = json.loads(response.body).get("results")[0].get("hits")

        for i in resp:
            position = position + 1
            item["position"] = position
            item["url"] = self.start_urls + i.get("breadcrumbs")[-1].get("path")
            item["session"] = response.meta['session']

            yield item

        count_hits = json.loads(response.body).get("results")[0].get("nbHits")
        if count_hits - position > 0:
            yield scrapy.Request(url=response.meta["url"],
                                 callback=self.api_request,
                                 meta={"url": response.meta["url"],
                                       "page": response.meta["page"]+1,
                                       "position": position,
                                       "session": response.meta["session"]},
                                 dont_filter=True)

    @rmq_errback
    def errback(self, failure):
        """
        This method handles errors encountered during the scraping process.

        Args:
            failure (twisted.internet.defer.Failure): The failure object containing the error details.

        Yields:
            `twisted.internet.defer.Deferred` representing the copied request if the error is a `TunnelError`.
        """

        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")

