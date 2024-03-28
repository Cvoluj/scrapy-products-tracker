import datetime
import json
import re
from urllib.parse import unquote, urlparse

import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError
from datetime import datetime

from items import ProductItem
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils.decorators import rmq_callback, rmq_errback


class CustominkProductsSpider(TaskToMultipleResultsSpider):
    name = "customink_products_spider"
    start_urls = "https://www.customink.com"
    custom_settings = {"ITEM_PIPELINES": {'rmq.pipelines.item_producer_pipeline.ItemProducerPipeline': 310, }}

    def __init__(self, *args, **kwargs):
        super(CustominkProductsSpider, self).__init__(*args, **kwargs)
        self.task_queue_name = f"{self.name}_task_queue"
        self.result_queue_name = f"{self.name}_result_queue"
        # self.reply_queue_name = f"{self.name}_reply_queue"

    # def next_request(self, _delivery_tag, msg_body):
    #     data = json.loads(msg_body)
    #     return scrapy.Request(data["url"],
    #                           callback=self.parse,
    #                           meta={'delivery_tag': _delivery_tag},
    #                           errback=self.errback)

    def start_requests(self):
        urls = ['https://www.customink.com/products/kids/kids-hats/rabbit-skins-baby-rib-hat/1125900']
        for i in urls:
            yield scrapy.Request(url=i, callback=self.parse)

    @rmq_callback
    def parse(self, response):
        item = ProductItem()

        item["url"] = response.url

        data_json = json.loads(response.xpath('//script[@id="pc-Style-jsonld"]/text()').get())

        item["title"] = data_json.get("name")
        item["description"] = data_json.get("description")
        item["brand"] = data_json.get("brand").get("name")
        item["image_url"] = urlparse(unquote(data_json.get("image"))).path.lstrip('/')

        # item["img"] = item["image_url"]

        item["current_price"] = float(data_json.get("offers").get("price")) / float(data_json.get("offers").get("eligibleQuantity").get("value"))

        item["regular_price"] = item["current_price"]

        item["additional_info"] = {
            "category": data_json.get("category").get("name"),
            "rating_value": data_json.get("aggregateRating", {}).get("ratingValue", "No"),
            "rating_count": data_json.get("aggregateRating", {}).get("ratingCount", "No"),
        }

        # delete and generate in the database
        item["stock"] = 1
        item["is_in_stock"] = True
        item["delivery_tag"] = 1

        yield item


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
