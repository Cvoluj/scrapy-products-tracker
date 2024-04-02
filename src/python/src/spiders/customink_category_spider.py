import json

import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.project import get_project_settings

from items import ProductItem
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback


class CustominkCategorySpider(TaskToMultipleResultsSpider):
    name = "customink_category_spider"
    start_urls = "https://www.customink.com"
    domain = "www.customink.com"
    custom_settings = {"ITEM_PIPELINES": {get_import_full_name(ItemProducerPipeline): 310}}
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super(CustominkCategorySpider, self).__init__(*args, **kwargs)
        self.task_queue_name = (f'{self.project_settings.get("RMQ_DOMAIN_QUEUE_MAP").get(self.domain)}'
                                f'_category_task_queue')
        self.result_queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")
        self.reply_to_queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")

        self.headers = {
            "x-algolia-api-key": "536d13eb752f1c8946764f0810a8ec4f",
            "x-algolia-application-id": "S0RXN4TV6T"
        }

    def next_request(self, _delivery_tag, msg_body):
        data = json.loads(msg_body)
        return scrapy.Request(url=data["url"],
                              callback=self.api_request,
                              meta={"url": data["url"], "page": 0, "position": 0, 'session': data.get('session')},
                              errback=self.errback,
                              dont_filter=True)

    # def start_requests(self):
    #     urls = [
    #         'https://www.customink.com/products/polos/screen-printed-polos/157',
    #         'https://www.customink.com/products/kids/kids-hats/116',
    #     ]
    #     for i in urls:
    #         yield scrapy.Request(url=i, callback=self.api_request,
    #                              meta={"url": i, "page": 0, "position": 0})

    def api_request(self, response):

        api_url = 'https://s0rxn4tv6t-dsn.algolia.net/1/indexes/*/queries'
        payload = {
            "requests": [
                {
                    "indexName": "prod_styles",
                    "params": f"clickAnalytics=true&facetFilters=%5B%5B%22sort_by%3Anone%22%5D%5D&facets=%5B%22*%22%5D&filters=status%3A%20active%20OR%20status%3A%20inactive%20AND%20categories.id%3A%20{response.meta['url'].split('/')[-1]}&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=42&maxValuesPerFacet=100&page={response.meta['page']}&query=&tagFilters=&userToken=anonymous-a2866a73-bd83-424f-a295-6bb37a0ef0fb"
                },
                # {
                #     "indexName": "prod_styles",
                #     "params": "analytics=false&clickAnalytics=false&facets=sort_by&filters=status%3A%20active%20OR%20status%3A%20inactive%20AND%20categories.id%3A%20157&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=0&maxValuesPerFacet=100&page=0&query=&userToken=anonymous-a2866a73-bd83-424f-a295-6bb37a0ef0fb"
                # }
            ]
        }
        yield scrapy.Request(url=api_url,
                             callback=self.parse,
                             body=json.dumps(payload),
                             method='POST',
                             headers=self.headers,
                             errback=self.errback,
                             meta=response.meta
                             )

    @rmq_callback
    def parse(self, response):
        item = ProductItem()
        position = response.meta['position']

        resp = json.loads(response.body).get("results")[0].get("hits")
        default_quantity = json.loads(response.body).get("results")[0].get("userData")[0].get("defaultQuoteQty")

        for i in resp:
            position = position + 1
            item['session'] = response.meta.get('session')
            item["position"] = position
            # item["title"] = i.get("name")
            # print(i.get("name"))

            item["url"] = self.start_urls + i.get("breadcrumbs")[-1].get("path")

            item["current_price"] = 0
            for j in i.get("default_unit_prices")[:-1]:
                if j.get("quantity") == default_quantity:
                    item["current_price"] = j.get("price")
                    break

            item["regular_price"] = item["current_price"]

            # delete and generate in the database
            item["stock"] = 1
            item["is_in_stock"] = True
            # item["delivery_tag"] = 1

            yield item

        count_hits = json.loads(response.body).get("results")[0].get("nbHits")
        if count_hits - position > 0:
            yield scrapy.Request(url=response.meta["url"],
                                 callback=self.api_request,
                                 meta={"url": response.meta["url"], "page": response.meta["page"]+1, "position": position, 'session': response.meta.get('session')},
                                 dont_filter=True)


    @rmq_errback
    def errback(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                self.logger.warning("404 Not Found. Changing status in queue")
        elif failure.check(TunnelError):
            response = failure.value.response
            if response.status == 429:
                self.logger.info("429 TunnelError. Copy request")
                yield failure.request.copy()
        self.logger.warning(f"IN ERRBACK: {repr(failure)}")

