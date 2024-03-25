import scrapy

from rmq.items import RMQItem


class ProductItem(RMQItem):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    brand = scrapy.Field()
    image_url = scrapy.Field()
    additional_info = scrapy.Field()

    regular_price = scrapy.Field()
    current_price = scrapy.Field()
    is_in_stock = scrapy.Field()
    stock = scrapy.Field()
    position = scrapy.Field()
