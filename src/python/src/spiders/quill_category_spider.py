import json
import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from items import ProductItem
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback
from scrapy.utils.project import get_project_settings


class QuillCategorySpider(TaskToMultipleResultsSpider):
    """
    Scrapy spider dedicated to extracting product URLs from category pages on Quill.com.

    Leverages RabbitMQ for task management and coordination with other spiders.
    """

    name = "quill_category_spider"
    domain = "www.quill.com"
    start_urls = "https://www.quill.com"
    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        """
        Initializes the spider and constructs RabbitMQ queue names based on project settings.
        """

        super(QuillCategorySpider, self).__init__(*args, **kwargs)
        self.task_queue_name = (f'{self.project_settings.get("RMQ_DOMAIN_QUEUE_MAP").get(self.domain)}'
                                f'_category_task_queue')
        self.result_queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")
        self.reply_to_queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")

    def next_request(self, _delivery_tag, msg_body):
        """
        This method retrieves the next request URL and meta data from a RabbitMQ message.

        Args:
            _delivery_tag (str): Delivery tag of the message.
            msg_body (str): Body of the message containing the JSON data.

        Returns:
            scrapy.Request: A Scrapy Request object with the URL, callback, meta data, and error callback.
        """

        data = json.loads(msg_body)
        return scrapy.Request(url=data["url"],
                              callback=self.parse,
                              meta={'position': 0, "session": data["session"]},
                              errback=self.errback,
                              dont_filter=True)


    @rmq_callback
    def parse(self, response):
        """
        This method parses the product listing page and extracts product URLs.

        Args:
            response (scrapy.Response): The response object from the Scrapy request.

        Yields:
            ProductItem: A populated ProductItem object with extracted data.
            scrapy.Request: A Scrapy Request object to follow the next page link (if available).
        """

        item = ProductItem()
        position = response.meta['position']
        product_list = response.xpath(
            '//div[contains(@class, "gridView") and contains(@class, "search-product-card-wrap")]')

        for product in product_list:
            position = position + 1
            item["position"] = position

            product_link = product.xpath(
                './/span[contains(@class, "search-product-name-wrap")]/a[contains(@class, "blue-hover-link")]/@href').get()
            item["url"] = response.urljoin(product_link)
            item["session"] = response.meta['session']

            yield item

        next_page = response.xpath(
            '//div[contains(@class, "text-primary")]/a[contains(@class, "next")]/@href').get()
        if next_page is not None:
            yield scrapy.Request(url=response.urljoin(next_page),
                                 callback=self.parse,
                                 meta={'position': position, 'session': response.meta['session']},
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
