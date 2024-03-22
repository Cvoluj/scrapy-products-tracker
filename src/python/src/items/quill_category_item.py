import scrapy
from rmq.items import RMQItem


class QuillCategoryItem(RMQItem):
    url = scrapy.Field()
    position = scrapy.Field()
    current_price = scrapy.Field()
    regular_price = scrapy.Field()

    # delete and generate in the database
    stock = scrapy.Field()
    in_stock = scrapy.Field()

