import json
from typing import Dict, Any

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http import Request, Response

from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToSingleResultSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback
from rmq.extensions import RPCTaskConsumer
from items import ProductItem


class ZoroDetailPageSpider(TaskToSingleResultSpider):
    name = "zoro_products_spider"
    domain = "www.zoro.com"
    custom_settings = {
        "ITEM_PIPELINES": {
            'pipelines.SaveImagesPipeline': 200,
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue_name = (f"{self.project_settings.get('RMQ_DOMAIN_QUEUE_MAP').get(self.domain)}"
                                f"_products_task_queue")
        self.reply_to_queue_name = self.project_settings.get("RMQ_PRODUCT_REPLY_QUEUE")
        self.result_queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")
        self.completion_strategy = RPCTaskConsumer.CompletionStrategies.REQUESTS_BASED

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
        return scrapy.Request(data["url"], callback=self.parse_product, dont_filter=True)

    @rmq_callback
    def parse_product(self, response: Response) -> ProductItem:
        """Parses the product page and yields a ProductItem with extracted product information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            ProductItem: The extracted item with product details.
        """
        item = ProductItem()
        product_data = json.loads(
            response.xpath("//script[@data-za='product-microdata']/text()").get()
        )
        item["url"] = response.url
        item["title"] = product_data.get("name")
        item["description"] = product_data.get("description")

        current_price = product_data.get("offers").get("price")
        if current_price:
            item["current_price"] = current_price

        regular_price = response.xpath("//div[@class='strikethrough-price']/text()").get()
        if regular_price:
            item["regular_price"] = float(regular_price.strip().replace("$", ""))
        item["in_stock"] = True
        in_stock = product_data.get("offers").get("availability")
        if in_stock == "http://schema.org/OutOfStock":
            item["in_stock"] = False
        item["brand"] = product_data.get("brand").get("name")
        if len(product_data.get("image")) >= 1:
            item["image_url"] = product_data.get("image")[0].get("contentUrl")
        item["image_file"] = f'{item["url"].split("/")[2].split(".")[1]}_{item["url"].split("/")[-2]}.jpg'
        attributes = response.xpath("//table//tbody//text()").getall()
        if attributes:
            clean_attributes = [item.strip() for item in attributes if item.strip()]
            item["additional_info"] = {
                clean_attributes[i]: clean_attributes[i + 1]
                for i in range(0, len(clean_attributes), 2)
            }

        yield item

    @rmq_errback
    def _errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
