# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EcommerceItem(scrapy.Item):
    main_category_name = scrapy.Field()
    sub_category_name = scrapy.Field()
    viewType = scrapy.Field()
    groupCode = scrapy.Field()
    subGroupCode = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    sale = scrapy.Field()
