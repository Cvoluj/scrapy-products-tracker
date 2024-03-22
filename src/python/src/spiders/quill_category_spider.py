import datetime
import json
import re

import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError
from datetime import datetime

from items import QuillCategoryItem
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils.decorators import rmq_callback, rmq_errback


class QuillCategorySpider(TaskToMultipleResultsSpider):
    name = "quill_category_spider"
    start_urls = "https://www.quill.com"
    custom_settings = {"ITEM_PIPELINES": {'rmq.pipelines.item_producer_pipeline.ItemProducerPipeline': 310, }}

    def __init__(self, *args, **kwargs):
        super(QuillCategorySpider, self).__init__(*args, **kwargs)
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
        urls = ['https://www.quill.com/disinfectant-wipes/cbl/27739.html',
                # 'https://www.quill.com/external-hard-drives/cbk/116139.html',
                # 'https://www.quill.com/sandisk-sdssdrc-032g-g26-solid-state-drive/cbk/98183.html',
                ]
        for i in urls:
            yield scrapy.Request(url=i, meta={'position': 0}, callback=self.parse)

    @rmq_callback
    def parse(self, response):
        item = QuillCategoryItem()
        position = response.meta['position']

        product_list = response.xpath(
            '//div[contains(@class, "gridView") and contains(@class, "search-product-card-wrap")]')

        for product in product_list:
            position = position + 1
            item["position"] = position

            product_link = product.xpath(
                './/span[contains(@class, "search-product-name-wrap")]/a[contains(@class, "blue-hover-link")]/@href').get()
            item["url"] = response.urljoin(product_link)

            current_price = product.xpath(
                './/div[contains(@class, "price-break")]/div[contains(@class, "pricing-wrap")][1]/div/div[contains(@class, "savings-highlight-wrap")]/span[contains(@class, "price-size")]/text()').get()
            if current_price:
                item["current_price"] = current_price.strip().replace("$", "")
            else:
                item["current_price"] = current_price

            regular_price = product.xpath(
                './/span[contains(@class, "elp-percentage")]/del/text()').get()
            if regular_price:
                item["regular_price"] = regular_price.strip().replace("$", "")
            else:
                item["regular_price"] = item["current_price"]

            # delete and generate in the database
            item["stock"] = 1
            item["in_stock"] = True
            item["delivery_tag"] = 1

            yield item

        next_page = response.xpath(
            '//div[contains(@class, "text-primary")]/a[contains(@class, "next")]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse, meta={'position': position})


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
