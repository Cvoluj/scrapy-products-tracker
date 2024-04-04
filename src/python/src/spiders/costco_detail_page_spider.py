import json
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


class CostcoDetailPageSpider(TaskToSingleResultSpider):
    name = "costco_products_spider"
    domain = "www.costco.com"
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
        self.headers = {"accept": "application/json"}

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
            headers=self.headers,
            meta={
                "position": data["position"],
                "session": data.get("session"),
                "delivery_tag": _delivery_tag,
            },
            dont_filter=True,
        )

    @rmq_callback
    def parse(self, response: Response) -> Request:
        """Parses the product page and yields a Scrapy Request object with extracted product information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            FormRequest: A Scrapy Request object for the next page.
        """
        item = ProductItem()
        item["session"] = response.meta.get("session")
        item["url"] = response.url
        title = response.xpath("//h1[@itemprop='name']/text()").get()
        if title is None:
            return
        item["title"] = title
        description = response.xpath("//div[@itemprop='description']/text()").get()
        if description:
            item["description"] = description.strip()
        item["brand"] = response.xpath("//div[@itemprop='brand']/text()").get()
        item["image_url"] = response.xpath("//img[@id='initialProductImage']/@src").get()
        item["image_file"] = f'{item["url"].split("/")[2].split(".")[1]}_{item["url"].split("/")[-1].split(".")[-2]}.jpg'
        item["position"] = response.meta["position"]
        attributes = response.xpath(
            "//h3[contains(text(), 'Specifications')]/following-sibling::div//text()"
        ).getall()
        if attributes:
            clean_attributes = [item.strip() for item in attributes if item.strip()]
            item["additional_info"] = {
                clean_attributes[i]: clean_attributes[i + 1]
                for i in range(0, len(clean_attributes), 2)
            }

        product_id = response.xpath("//input[@name='productBeanId']/@value").get()
        params = {
            "productId": product_id,
            "WH": "1250-3pl,1321-wm,1455-3pl,283-wm,561-wm,653-dz,725-wm,731-wm,758-wm,759-wm,847_0-cor,847_0-cwt,847_0-edi,847_0-ehs,847_0-membership,847_0-mpt,847_0-spc,847_0-wm,847_1-edi,847_d-fis,847_lg_n1f-edi,847_NA-cor,847_NA-pharmacy,847_NA-wm,847_ss_u362-edi,847_wp_r458-edi,951-wm,952-wm,9847-wcs,115-bd",
        }
        yield scrapy.FormRequest(
            url="https://www.costco.com/AjaxGetInventoryDetail",
            formdata=params,
            callback=self.parse_stock,
            errback=self._errback,
            cookies={
                "invCheckPostalCode": "97123",
            },
            headers=self.headers,
            meta={
                "item": item,
                "product_id": product_id,
                "session": response.meta.get("session"),
                "delivery_tag": response.meta.get("delivery_tag"),
            },
            dont_filter=True,
        )

    @rmq_callback
    def parse_stock(self, response: Response) -> Request:
        """Parses the stock information and yields a Scrapy Request object with extracted stock information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            FormRequest: A Scrapy Request object for the next page.
        """
        item = response.meta["item"]
        try:
            data = response.json()
            if data:
                item["is_in_stock"] = data.get("invAvailable")
        except json.JSONDecodeError:
            self.logger.info(f"Can't parse stock data: no valid JSON response")

        params = {"productId": response.meta["product_id"]}
        yield scrapy.FormRequest(
            url="https://www.costco.com/AjaxGetContractPrice",
            formdata=params,
            callback=self.parse_price,
            errback=self._errback,
            headers=self.headers,
            meta={
                "item": item,
                "session": response.meta.get("session"),
                "delivery_tag": response.meta.get("delivery_tag"),
            },
            dont_filter=True,
        )

    @rmq_callback
    def parse_price(self, response: Response) -> ProductItem:
        """Parses the price information and yields a ProductItem with extracted product information.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            ProductItem: The extracted item with product details.
        """
        item = response.meta["item"]
        item["session"] = response.meta.get("session")
        item["currency"] = "USD"
        try:
            data = response.json()
            if data:
                regular_price = data.get("finalOnlinePrice")
                discount = data.get("discount")
                item["regular_price"] = regular_price
                item["current_price"] = regular_price - discount
        except json.JSONDecodeError:
            self.logger.info(f"Can't parse price data: no valid JSON response")

        yield item

    @rmq_errback
    def _errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
