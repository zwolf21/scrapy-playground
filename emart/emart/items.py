# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EmartItem(scrapy.Item):
    ctg_large = scrapy.Field()
    ctg_medium = scrapy.Field()
    ctg_small = scrapy.Field()
    img_src = scrapy.Field()
    link = scrapy.Field()
    itemId = scrapy.Field()
    itemName = scrapy.Field()
    pkgPrice = scrapy.Field()
    pkgAmount = scrapy.Field()
    amountUnit = scrapy.Field()
    currencyUnit = scrapy.Field()
    commentCount = scrapy.Field()
    femaleRatio = scrapy.Field()
    maleRatio = scrapy.Field()
    age10 = scrapy.Field()
    age20 = scrapy.Field()
    age30 = scrapy.Field()
    age40 = scrapy.Field()
    age50 = scrapy.Field()
    tags = scrapy.Field()
