import json
from urllib.parse import unquote, urlparse
import scrapy
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.project import get_project_settings
from items import ProductItem
from rmq.pipelines import ItemProducerPipeline
from rmq.spiders import TaskToMultipleResultsSpider
from rmq.utils import get_import_full_name
from rmq.utils.decorators import rmq_callback, rmq_errback


class CustominkProductsSpider(TaskToMultipleResultsSpider):
    name = "customink_products_spider"
    domain = "www.customink.com"
    start_urls = "https://www.customink.com"
    custom_settings = {
        "ITEM_PIPELINES": {
            'pipelines.SaveImagesPipeline': 200,
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }
    project_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super(CustominkProductsSpider, self).__init__(*args, **kwargs)
        self.task_queue_name = (f"{self.project_settings.get('RMQ_DOMAIN_QUEUE_MAP').get(self.domain)}"
                                f"_products_task_queue")
        self.reply_to_queue_name = self.project_settings.get("RMQ_PRODUCT_REPLY_QUEUE")
        self.result_queue_name = self.project_settings.get("RMQ_PRODUCT_RESULT_QUEUE")

    def next_request(self, _delivery_tag, msg_body):
        data = json.loads(msg_body)
        return scrapy.Request(url=data["url"],
                              callback=self.parse,
                              errback=self.errback,
                              dont_filter=True)

    # def start_requests(self):
    #     urls = ['https://www.customink.com/products/kids/kids-hats/rabbit-skins-baby-rib-hat/1125900']
    #     for i in urls:
    #         yield scrapy.Request(url=i, callback=self.parse)

    @rmq_callback
    def parse(self, response):
        # pc-Style-jsonld

        item = ProductItem()

        item["url"] = response.url

        data_json = json.loads(response.xpath('//script[@id="pc-Style-jsonld"]/text()').get())

        item["title"] = data_json.get("name")
        item["description"] = data_json.get("description")
        item["brand"] = data_json.get("brand", {}).get("name")
        item["image_url"] = urlparse(unquote(data_json.get("image"))).path.lstrip('/')

        item["image_file"] = f'{item["url"].split("/")[2].split(".")[1]}_{item["url"].split("/")[-1].split(".")[0]}.jpg'

        try:
            item["current_price"] = float(data_json.get("offers").get("price")) / float(data_json.get("offers").get("eligibleQuantity").get("value"))
        except:
            item["current_price"] = 0

        item["regular_price"] = item["current_price"]

        item["additional_info"] = json.dumps({
            "category": data_json.get("category", {}).get("name", "No"),
            "rating_value": data_json.get("aggregateRating", {}).get("ratingValue", "No"),
            "rating_count": data_json.get("aggregateRating", {}).get("ratingCount", "No"),
        })
        stock = data_json.get("offers", {}).get("availability")
        if stock == "http://schema.org/InStock":
            item["stock"] = 1
            item["is_in_stock"] = True
        else:
            item["stock"] = 0
            item["is_in_stock"] = False

        yield item


    @rmq_errback
    def errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")
