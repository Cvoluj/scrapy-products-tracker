import json
import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.project import get_project_settings
from items import ProductItem
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback


class QuillProductsSpider(TaskToMultipleResultsSpider):
    """
    Scrapy spider specifically designed to extract product data from Quill.com.

    This spider leverages RabbitMQ for task management and utilizes custom item pipelines
    for handling product images and sending data to RabbitMQ queues.
    """

    name = "quill_products_spider"
    domain = "www.quill.com"
    start_urls = "https://www.quill.com"
    custom_settings = {
        "ITEM_PIPELINES": {
            'pipelines.SaveImagesPipeline': 200,
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        """
        Initializes the spider and constructs RabbitMQ queue names based on project settings.
        """
        super(QuillProductsSpider, self).__init__(*args, **kwargs)
        self.task_queue_name = (f"{self.project_settings.get('RMQ_DOMAIN_QUEUE_MAP').get(self.domain)}"
                                f"_products_task_queue")
        self.reply_to_queue_name = self.project_settings.get("RMQ_PRODUCT_REPLY_QUEUE")
        self.result_queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")

    def next_request(self, _delivery_tag, msg_body):
        """
        This method retrieves the next request URL and meta data from a RabbitMQ message.

        Args:
            _delivery_tag (str): Delivery tag of the message.
            msg_body (str): Body of the message containing the JSON data.

        Returns:
            scrapy.Request: A Scrapy Request object with the URL, callback, meta data, and error callback.
        """

        data = json.loads(msg_body)
        return scrapy.Request(url=data["url"],
                              callback=self.parse,
                              errback=self.errback,
                              dont_filter=True)

    # def start_requests(self):
    #     urls = ['https://www.quill.com/nescafe-espresso-whole-bean-coffee-medium-roast-3527-oz-6-carton-12338492/cbs/55421487.html']
    #     for i in urls:
    #         yield scrapy.Request(url=i, callback=self.parse)

    @rmq_callback
    def parse(self, response):
        """
        Parses the product page HTML content to extract relevant product information
        and yield a populated ProductItem object.

        Employs XPath expressions to target specific elements on the Quill.com product page.
        Handles potential data absence gracefully by providing default values or checking for empty responses.

        Args:
            response (scrapy.Response): Scrapy response object containing the downloaded product page HTML.

        Yields:
            ProductItem: A populated ProductItem object containing the extracted product information.
        """
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

        item["image_url"] = response.urljoin(response.xpath(
            '//div[contains(@class, "skuImageZoom")]/img/@src').get())
        item["image_file"] = f'{item["url"].split("/")[2].split(".")[1]}_{item["url"].split("/")[-1].split(".")[-2]}.jpg'

        product_card = response.xpath('//div[@class="row no-gutters"]')
        current_price = product_card.xpath(
            './/div[contains(@class, "pricing-wrap")]/div/div/span[contains(@class, "price-size") and contains(text('
            '), "$")]/text()').get()
        if current_price:
            item["current_price"] = current_price.strip().replace("$", "")
            item["currency"] = current_price.strip()[0]
        else:
            item["current_price"] = current_price
            item["currency"] = None

        item["units"] = product_card.xpath(
            './/div[contains(@class, "pricing-wrap")]/div/div[contains(@class, "selling-uom")]/text()').get()

        regular_price = product_card.xpath(
            './/div[contains(@class, "pricing-wrap")]/div/span[contains(@class, "elp-percentage")]/del[contains('
            'text(), "$")]/text()').get()
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
            item["additional_info"] = json.dumps(additional_info)
        else:
            item["additional_info"] = None

        stock = response.xpath(
            '//div[contains(@class, "no-gutters")]/div[contains(@class, "sku-promo-image")]/div[contains(@class, '
            '"promo-flag")]/text()').get(default="No").strip()
        if stock == "Out of stock":
            item["stock"] = 0
            item["is_in_stock"] = False
        else:
            item["stock"] = 1
            item["is_in_stock"] = True

        yield item


    @rmq_errback
    def errback(self, failure):
        """
        This method handles errors encountered during the scraping process.

        Args:
            failure (twisted.internet.defer.Failure): The failure object containing the error details.

        Yields:
            `twisted.internet.defer.Deferred` representing the copied request if the error is a `TunnelError`.
        """

        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
