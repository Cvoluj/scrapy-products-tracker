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


class QuillCategorySpider(TaskToMultipleResultsSpider):
    name = "quill_category_spider"
    start_urls = "https://www.quill.com"
    custom_settings = {"ITEM_PIPELINES": {get_import_full_name(ItemProducerPipeline): 310}}
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super(QuillCategorySpider, self).__init__(*args, **kwargs)
        self.task_queue_name = "quill_task_category"
        self.result_queue_name = "products_result_queue"
        self.reply_to_queue_name = self.project_settings.get("CATEGORY_REPLY_QUEUE")

    def next_request(self, _delivery_tag, msg_body):
        data = json.loads(msg_body)
        return scrapy.Request(data["url"],
                              callback=self.parse,
                              meta={'position': 0},
                              errback=self.errback,
                              dont_filter=True)

    @rmq_callback
    def parse(self, response):
        item = ProductItem()
        position = response.meta['position']

        product_list = response.xpath(
            '//div[contains(@class, "gridView") and contains(@class, "search-product-card-wrap")]')

        for product in product_list:
            position = position + 1
            item["position"] = position

            product_link = product.xpath(
                './/span[contains(@class, "search-product-name-wrap")]'
                '/a[contains(@class, "blue-hover-link")]/@href').get()
            item["url"] = response.urljoin(product_link)

            current_price = product.xpath(
                './/div[contains(@class, "price-break")]/div[contains(@class, "pricing-wrap")][1]/div/div[contains'
                '(@class, "savings-highlight-wrap")]/span[contains(@class, "price-size")]/text()').get()
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
            item["is_in_stock"] = True

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
