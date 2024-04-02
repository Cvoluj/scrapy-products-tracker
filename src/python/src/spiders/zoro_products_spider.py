import json
from typing import Dict, Any

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
    custom_settings = {"ITEM_PIPELINES": {get_import_full_name(ItemProducerPipeline): 310}}
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue_name = (
            f"{self.project_settings.get('RMQ_DOMAIN_QUEUE_MAP').get(self.domain)}"
            f"_products_task_queue"
        )
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
        return Request(
            data["url"],
            callback=self.parse_product,
            errback=self._errback,
            meta={"position": data.get("position"), "session": data.get("session")},
            dont_filter=True,
        )

    @rmq_callback
    def parse_product(self, response: Response) -> ProductItem:
        """Parses the product page and yields a ProductItem with extracted product information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            ProductItem: The extracted item with product details.
        """
        item = ProductItem()
        product_data = self.extract_product_data(response)
        self.fill_basic_info(item, product_data, response)
        self.fill_pricing_info(item, response)
        self.fill_stock_info(item, product_data)
        self.fill_brand_info(item, product_data)
        self.fill_image_info(item, product_data)
        self.fill_currency_and_units_info(item, product_data, response)
        self.fill_additional_info(item, response)
        item["position"] = response.meta["position"]

        yield item

    def extract_product_data(self, response: Response) -> dict:
        """Extract product data from the page script."""
        return json.loads(response.xpath("//script[@data-za='product-microdata']/text()").get())

    def fill_basic_info(self, item, product_data, response):
        """Fill basic information of the product."""
        item["url"] = response.url
        item["title"] = product_data.get("name")
        item["description"] = product_data.get("description")

    def fill_pricing_info(self, item, response):
        """Extract and fill pricing information."""
        current_price = response.xpath("//div[@data-za='product-price']//div/text()").get()
        if current_price:
            item["current_price"] = float(current_price.strip().replace(",", ""))
        regular_price = response.xpath("//div[@class='strikethrough-price']/text()").get()
        if regular_price:
            item["regular_price"] = float(regular_price.strip().replace("$", "").replace(",", ""))

    def fill_stock_info(self, item, product_data):
        """Determine the stock status."""
        item["is_in_stock"] = True
        in_stock = product_data.get("offers", {}).get("availability")
        if in_stock == "http://schema.org/OutOfStock":
            item["is_in_stock"] = False

    def fill_brand_info(self, item, product_data):
        """Fill in the brand information."""
        item["brand"] = product_data.get("brand", {}).get("name")

    def fill_image_info(self, item, product_data):
        """Extract and fill image URL."""
        images = product_data.get("image", [])
        if images:
            item["image_url"] = images[0].get("contentUrl")

    def fill_currency_and_units_info(self, item, product_data, response):
        """Fill currency and units information."""
        item["currency"] = product_data.get("offers").get("priceCurrency")
        units = response.xpath("//div[@class='price']//span//text()").getall()
        if len(units) == 2:
            item["units"] = units[-1]

    def fill_additional_info(self, item, response):
        """Extract and fill additional information about the product."""
        attributes = response.xpath("//table//tbody//text()").getall()
        if attributes:
            clean_attributes = [attr.strip() for attr in attributes if attr.strip()]
            item["additional_info"] = {
                clean_attributes[i]: clean_attributes[i + 1]
                for i in range(0, len(clean_attributes), 2)
            }

    @rmq_errback
    def _errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
