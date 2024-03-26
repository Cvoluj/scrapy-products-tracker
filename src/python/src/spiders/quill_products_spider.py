import json

import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError

from items import ProductItem
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback
from scrapy.utils.project import get_project_settings


class QuillProductsSpider(TaskToMultipleResultsSpider):
    name = "quill_products_spider"
    start_urls = "https://www.quill.com"
    custom_settings = {"ITEM_PIPELINES": {get_import_full_name(ItemProducerPipeline): 310}}
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super(QuillProductsSpider, self).__init__(*args, **kwargs)
        self.task_queue_name = "quill_task_product"
        self.result_queue_name = "products_result_queue"
        self.reply_to_queue_name = self.project_settings.get("PRODUCTS_REPLY_QUEUE")

    def next_request(self, _delivery_tag, msg_body):
        data = json.loads(msg_body)
        return scrapy.Request(data["url"],
                              callback=self.parse,
                              errback=self.errback,
                              dont_filter=True)

    @rmq_callback
    def parse(self, response):
        item = ProductItem()

        item["url"] = response.url
        item["title"] = response.xpath(
            '//div[@id="SkuMainContentDiv"]/h1[contains(@class, "m-sku-title")]/text()').get()
        item["description"] = response.xpath(
            '//div[@id="skuDescription"]/div[contains(@class, "qOverflow")]/div/span/text()').get()
        brand = response.xpath(
            '//div[span/text()="Brand"]/following-sibling::div[1]/text()').get()
        if brand:
            item["brand"] = brand.strip()
        else:
            item["brand"] = brand

        # item["img"] = 'https:' + response.xpath('//div[contains(@class, "skuImageZoom")]/img/@src').get()
        item["image_url"] = 'https:' + response.xpath('//div[contains(@class, "skuImageZoom")]/img/@src').get()

        current_price = response.xpath(
            '//div[@class="row no-gutters"]//div[contains(@class, "pricing-wrap")]/div/div/span'
            '[contains(@class, "price-size") and contains(text(), "$")]/text()').get()
        if current_price:
            item["current_price"] = current_price.strip().replace("$", "")
        else:
            item["current_price"] = current_price

        regular_price = response.xpath(
            '//div[@class="row no-gutters"]//div[contains(@class, "pricing-wrap")]/div/span'
            '[contains(@class, "elp-percentage")]/del[contains(text(), "$")]/text()').get()
        if regular_price:
            item["regular_price"] = regular_price.strip().replace("$", "")
        else:
            item["regular_price"] = item["current_price"]

        additional_info = {}
        additional_info_keys = response.xpath(
            '//div[contains(@class, "skuSpecification")]/div/div/span/text()').getall()

        if additional_info_keys:
            for element in additional_info_keys:
                additional_info[element.strip()] = response.xpath(
                    f'//div[span/text()="{element}"]/following-sibling::div[1]/text()').get(default="No").strip()
            item["additional_info"] = additional_info
        else:
            item["additional_info"] = None

        # delete and generate in the database
        item["stock"] = 1
        item["is_in_stock"] = True

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
