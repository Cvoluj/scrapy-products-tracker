import json
from typing import Dict, Any

from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.project import get_project_settings
from scrapy.http import Request, Response, JsonRequest, FormRequest
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToSingleResultSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback
from rmq.extensions import RPCTaskConsumer
from items import ProductItem


class ZoroCategorySpider(TaskToSingleResultSpider):
    name = "zoro_category_spider"
    domain = "www.zoro.com"
    custom_settings = {"ITEM_PIPELINES": {get_import_full_name(ItemProducerPipeline): 310}}
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue_name = (
            f"{self.project_settings.get('RMQ_DOMAIN_QUEUE_MAP').get(self.domain)}"
            f"_category_task_queue"
        )

        self.reply_to_queue_name = self.project_settings.get("RMQ_CATEGORY_REPLY_QUEUE")
        self.result_queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")
        self.completion_strategy = RPCTaskConsumer.CompletionStrategies.REQUESTS_BASED
        self.headers = {
            "apikey": self.project_settings.get("ZORO_SPIDER_API_KEY"),
        }

        self.api_base_url = "https://api.prod.zoro.com"
        self.pagination_size = 36
        self.zoro_url = "https://www.zoro.com"
        self.img_url_base = "https://www.zoro.com/static/cms/product/prev/"
        self.search_url = f"{self.api_base_url}/discover/v2/search"
        self.category_url = f"{self.api_base_url}/catalog/v1/catalog/category"
        self.availability_url = f"{self.api_base_url}/scm/v1/inventory/availability"
        self.start = 0

    def next_request(self, _delivery_tag: str, msg_body: str) -> FormRequest:
        """
        Creates the next request to process based on the message body received.

        Args:
            _delivery_tag (str): The delivery tag of the message.
            msg_body (str): The body of the message containing URL and data.

        Returns:
            FormRequest: The next request to be processed by the spider.
        """

        data: Dict[str, Any] = json.loads(msg_body)
        category_url = data["url"]
        category_id = category_url.split("/")[-2]
        return FormRequest(
            url=self.category_url,
            method="GET",
            formdata={"codes": category_id},
            headers=self.headers,
            callback=self.parse_category_pages,
            errback=self._errback,
            meta={"category_id": category_id, "session": data.get("session")},
            dont_filter=True,
        )

    @rmq_callback
    def parse_category_pages(self, response: Response) -> JsonRequest:
        """Parses the category page and yields a Scrapy Request.

        Args:
            response (Response): The response object used to extract data.

        Yields:
           JsonRequest: A Scrapy Request object.
        """
        codes = [
            parent["code"] for item in response.json()["items"] for parent in item["allParents"]
        ]
        category_id = response.meta["category_id"]
        value = f"{'/'.join(codes)}/{category_id}"
        json_data = self.generate_json_data(self.start, category_id, value)
        yield JsonRequest(
            url=self.search_url,
            data=json_data,
            headers=self.headers,
            callback=self.parse_products,
            meta={
                "start": self.start,
                "value": value,
                "category_id": category_id,
                "session": response.meta.get('session')
            },
            dont_filter=True,
        )

    @rmq_callback
    def parse_products(self, response: Response) -> JsonRequest:
        """Parses the category page and yields a Scrapy Request.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            JsonRequest: A Scrapy Request object.
        """
        data = response.json()
        products = data.get("records", [])
        product_ids = [product["id"] for product in products]
        request_data = [
            {"zoroNo": product_id} for product_id in product_ids if product_id.startswith("G")
        ]
        start_position = response.meta.get("start", 0)
        yield JsonRequest(
            url=self.availability_url,
            data=request_data,
            headers=self.headers,
            callback=self.parse_availability,
            meta={
                "products": products, 
                "start_position": start_position, 
                "session": response.meta.get('session')
            },
            dont_filter=True,
        )

        total_products = data.get("facets", [{}])[0].get("refinements", [{}])[0].get("count")

        if response.meta.get("start", 0) == 0:
            pages_needed = (total_products + self.pagination_size - 1) // self.pagination_size
            for page_number in range(1, pages_needed):
                start = page_number * self.pagination_size
                json_data = self.generate_json_data(
                    start,
                    response.meta["category_id"],
                    response.meta["value"],
                )

                yield JsonRequest(
                    url=self.search_url,
                    data=json_data,
                    headers=self.headers,
                    callback=self.parse_products,
                    meta={
                        "start": start,
                        "value": response.meta["value"],
                        "category_id": response.meta["category_id"],
                        "session": response.meta.get('session')
                    },
                    dont_filter=True,
                )

    @rmq_callback
    def parse_availability(self, response: Response) -> ProductItem:
        """Parses the category page and yields a Scrapy Request.

        Args:
            response (Response): The response object used to extract data.

        Yields:
            ProductItem: The extracted item with product details.
        """

        availability_info = response.json().get("payload")
        availability_dict = {
            item["zoroNo"]: item["availabilityStatus"] for item in availability_info
        }

        products = response.meta["products"]
        start_position = response.meta["start_position"]
        
        for i, product in enumerate(products):
            detail_info = product["variants"][0]
            item = ProductItem()
            item['session'] = response.meta.get('session')
            item["is_in_stock"] = True
            if availability_dict.get(product["id"]) == "Out of Stock":
                item["is_in_stock"] = False
            item["regular_price"] = detail_info.get("originalPrice")
            item["title"] = detail_info["title"]
            item["description"] = detail_info["description"]
            item["brand"] = product["brand"]
            if detail_info["image"] != "ZKAIyMrw_.JPG":
                item["image_url"] = f"{self.img_url_base}{detail_info['image']}"
            item["url"] = f"{self.zoro_url}{detail_info['slug']}"
            item["current_price"] = detail_info["price"]
            item["additional_info"] = detail_info["attributes"]
            item["position"] = start_position + i + 1
            item["currency"] = "USD"
            item["units"] = detail_info["priceUnit"]
            item["session"] = response.meta["session"]
            yield item

    def generate_json_data(self, start: int, category_id: str, value: str) -> dict:
        """Generates and returns a JSON structure for data requests with pagination and category filtering.

        Args:
            start: The starting index for pagination.
            category_id: The ID for the category to filter by.
            value: The value to match within the specified category.

        Returns:
            A dict representing the JSON structure for the request, including pagination info,
            the type of page being requested, and the filtering criteria based on the provided category.
        """
        return {
            "pagination": {"start": start, "pageSize": self.pagination_size},
            "pageType": "category",
            "query": "",
            "facets": [
                {
                    "name": "category",
                    "type": "category",
                    "refinements": [
                        {
                            "code": category_id,
                            "value": value,
                            "selected": True,
                        }
                    ],
                }
            ],
        }

    @rmq_errback
    def _errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
