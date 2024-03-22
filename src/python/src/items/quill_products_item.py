import scrapy
from rmq.items import RMQItem


class QuillProductsItem(RMQItem):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    brand = scrapy.Field()
    product_page_url = scrapy.Field()
    current_price = scrapy.Field()
    regular_price = scrapy.Field()
    additional_info = scrapy.Field()

    # delete and generate in the database
    stock = scrapy.Field()
    in_stock = scrapy.Field()
