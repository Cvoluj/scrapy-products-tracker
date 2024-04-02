import json
import re
from typing import Dict, Any

import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http import Request, Response
from scrapy.utils.project import get_project_settings
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToSingleResultSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback
from rmq.extensions import RPCTaskConsumer
from items import ProductItem


class VikingDetailPageSpiderSpider(TaskToSingleResultSpider):
    name = "viking_products_spider"
    domain = "www.viking-direct.co.uk"
    project_settings = get_project_settings()
    custom_settings = {
        "ITEM_PIPELINES": {
            'pipelines.SaveImagesPipeline': 200,
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
            meta={"position": data["position"], 'session': data.get('session')},
            dont_filter=True,
        )

    @rmq_callback
    def parse(self, response: Response) -> Request:
        """Parses the product page and yields a ProductItem with extracted product information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            ProductItem: The extracted item with product details.
        """
        item = ProductItem()
        item['session'] = response.meta.get('session')
        item["url"] = response.url
        item["title"] = response.xpath("//h1[@itemprop='name']/text()").get()
        item["description"] = self.extract_description(response)
        item["brand"] = response.xpath("//a[@itemprop='brand']//text()").get()
        item["image_url"] = self.extract_image_url(response)
        item["image_file"] = f'{item["url"].split("/")[2].split(".")[1]}_{item["url"].split("/")[-1].split("-")[-1]}.jpg'
        item["additional_info"] = self.extract_additional_info(response)
        item["units"] = response.xpath(
            "//div[@class='product-price-panel__price-per']/div//text()"
        ).get()
        item["currency"] = response.xpath("//div/@data-currency-iso-code").get()
        item["is_in_stock"] = self.check_stock_status(response)
        self.extract_pricing_and_id(item, response)
        item["position"] = response.meta.get("position")
        item["session"] = response.meta.get("session")
        yield item

    @staticmethod
    def extract_description(response: Response) -> str:
        description_parts = response.xpath("//div[@itemprop='description']//text()").getall()
        return " ".join([str(part) for part in description_parts]).strip()

    @staticmethod
    def extract_image_url(response: Response) -> str:
        image_url = response.xpath("//img[@itemprop='image']/@src").get().split("?")[0]
        return f"https:{image_url}"

    @staticmethod
    def check_stock_status(response: Response) -> bool:
        out_of_stock = response.xpath("//div[@data-stock-status='outOfStock']").get()
        return not out_of_stock

    @staticmethod
    def extract_additional_info(response: Response) -> dict:
        get_additional_info = response.xpath("//div[@id='contentproductSpecifications']//tr")
        additional_info_dict = {}
        for additional_info in get_additional_info:
            attribute_key = additional_info.xpath("./td[@class='title']/text()").get()
            attribute_info_parts = additional_info.xpath("./td[not(@class)]//text()").getall()
            clean_attribute_info = ", ".join(
                part.strip() for part in attribute_info_parts if part.strip()
            )
            additional_info_dict[attribute_key.strip()] = clean_attribute_info
        return additional_info_dict

    @staticmethod
    def extract_pricing_and_id(item, response: Response) -> None:
        data_dict = {}
        data_string = response.xpath("//script[@type='text/javascript']/text()").get()
        match = re.search(r"\{.*?\}(?=\;)", data_string, re.DOTALL)
        if match:
            json_object_str = match.group(0)
            try:
                data_dict = json.loads(json_object_str)
                item["current_price"] = float(
                    data_dict.get("skuInfo").get("price")[0]["skuPriceinVAT"]
                )
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    @rmq_errback
    def _errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
