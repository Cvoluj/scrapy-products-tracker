import json
from typing import Dict, Any

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http import Request, Response
from furl import furl

from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToSingleResultSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback
from rmq.extensions import RPCTaskConsumer
from items import ProductItem


class VikingCategorySpider(TaskToSingleResultSpider):
    name = "viking_category_spider"
    domain_url = "https://www.viking-direct.co.uk/"
    project_settings = get_project_settings()

    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completion_strategy = RPCTaskConsumer.CompletionStrategies.REQUESTS_BASED
        self.task_queue_name = (
            f"{self.project_settings.get('RMQ_DOMAIN_QUEUE_MAP').get(self.domain)}"
            f"_products_task_queue"
        )
        self.reply_to_queue_name = self.project_settings.get("RMQ_PRODUCT_REPLY_QUEUE")
        self.result_queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")

    def next_request(self, _delivery_tag: str, msg_body: str) -> Request:
        """
        Creates the next request to process based on the message body received.

        Args:
            _delivery_tag (str): The delivery tag of the message.
            msg_body (str): The body of the message containing URL and data.

        Returns:
            Request: The next request to be processed by the spider.
        """

        data: Dict[str, Any] = json.loads(msg_body)
        return scrapy.Request(
            url=data["url"],
            callback=self.parse,
            errback=self._errback,
            meta={"total_products": 0},
            dont_filter=True,
        )

    @rmq_callback
    def parse(self, response: Response) -> Request:
        """Parses the category page and yields a ProductItem with extracted product information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            ProductItem: The extracted item with product details.
            Request: A Scrapy Request object for the next page, if any.
        """
        f = furl(response.url)
        if "page" not in f.args:
            f.args["page"] = 0
        item = ProductItem()
        products = response.xpath("//ol[@id='productList']//li")
        for product in products:
            item["url"] = (
                self.domain_url
                + product.xpath(".//a[@class='product-lister-item__name']/@href").get()
            )
            item["product_id"] = f"viking_{product.xpath('//div/@data-legacy-sku').get()}"
            total_products = response.meta["total_products"]
            item["position"] = total_products + 1
            yield item
            response.meta["total_products"] = total_products + 1
        if products:
            f.args["page"] = int(f.args["page"]) + 1
            next_page_url = f.url
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta=response.meta,
                dont_filter=True,
            )

    @rmq_errback
    def _errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
