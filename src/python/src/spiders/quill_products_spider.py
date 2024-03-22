import datetime
import json
import re

import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError
from datetime import datetime

from items import QuillProductsItem
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils.decorators import rmq_callback, rmq_errback


class QuillProductsSpider(TaskToMultipleResultsSpider):
    name = "quill_products_spider"
    start_urls = "https://www.quill.com"
    custom_settings = {"ITEM_PIPELINES": {'rmq.pipelines.item_producer_pipeline.ItemProducerPipeline': 310, }}

    def __init__(self, *args, **kwargs):
        super(QuillProductsSpider, self).__init__(*args, **kwargs)
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
        urls = ['https://www.quill.com/samsung-t7-shield-2tb-usb-32-external-solid-state-drive-mu-pe2t0s-am/cbs/55454570.html']
        for i in urls:
            yield scrapy.Request(url=i, callback=self.parse)

    @rmq_callback
    def parse(self, response):
        item = QuillProductsItem()

        item["url"] = response.url
        item["title"] = response.xpath(
            '//div[@id="SkuMainContentDiv"]/h1[contains(@class, "m-sku-title")]/text()').get()
        item["description"] = response.xpath(
            '//div[@id="skuDescription"]/div[contains(@class, "qOverflow")]/div/span/text()').get()
        item["brand"] = response.xpath(
            '//div[span/text()="Brand"]/following-sibling::div[1]/text()').get().strip()

        # item["img"] = 'https:' + response.xpath('//div[contains(@class, "skuImageZoom")]/img/@src').get()
        item["product_page_url"] = 'https:' + response.xpath('//div[contains(@class, "skuImageZoom")]/img/@src').get()

        item["current_price"] = response.xpath(
            '//div[@class="row no-gutters"]//div[contains(@class, "pricing-wrap")]/div/div/span[contains(@class, "price-size") and contains(text(), "$")]/text()').get()
        regular_price = response.xpath(
            '//div[@class="row no-gutters"]//div[contains(@class, "pricing-wrap")]/div/span[contains(@class, "elp-percentage")]/del[contains(text(), "$")]/text()').get()
        if regular_price:
            item["regular_price"] = regular_price
        else:
            item["regular_price"] = item["current_price"]


        additional_info = {}
        additional_info_keys = response.xpath(
            '//div[contains(@class, "skuSpecification")]/div/div/span/text()').getall()

        if additional_info_keys:
            for element in additional_info_keys:
                additional_info[element.strip()] = response.xpath(
                    f'//div[span/text()="{element}"]/following-sibling::div[1]/text()').get().strip()
            item["additional_info"] = additional_info
        else:
            item["additional_info"] = None

        item["stock"] = True
        item["in_stock"] = True

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
