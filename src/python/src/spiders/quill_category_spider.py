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
    name = "quill_category_spider"
    domain = "www.quill.com"
    start_urls = "https://www.quill.com"
    custom_settings = {"ITEM_PIPELINES": {get_import_full_name(ItemProducerPipeline): 310}}
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super(QuillCategorySpider, self).__init__(*args, **kwargs)
        self.task_queue_name = (f'{self.project_settings.get("RMQ_DOMAIN_QUEUE_MAP").get(self.domain)}'
                                f'_category_task_queue')
        self.result_queue_name = self.project_settings.get("RMQ_CATEGORY_RESULT_QUEUE")
        self.reply_to_queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")

    def next_request(self, _delivery_tag, msg_body):
        data = json.loads(msg_body)
        return scrapy.Request(data["url"],
                              callback=self.parse,
                              meta={'position': 0},
                              errback=self.errback,
                              dont_filter=True)

    # def start_requests(self):
    #     urls = ['https://www.quill.com/whole-bean-coffee/cbk/53110.html']
    #     for i in urls:
    #         yield scrapy.Request(url=i, callback=self.parse, meta={'position': 0}, errback=self.errback)

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

            yield item

        next_page = response.xpath(
            '//div[contains(@class, "text-primary")]/a[contains(@class, "next")]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse, meta={'position': position})

    @rmq_errback
    def errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
