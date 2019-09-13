import scrapy


class EmartItem(scrapy.Item):
    ctg_lg = scrapy.Field()
    ctg_md = scrapy.Field()
    ctg_sm = scrapy.Field()
    ctg_xm = scrapy.Field()
    brand_name = scrapy.Field()
    item_code = scrapy.Field()
    item_name = scrapy.Field()
    img_src = scrapy.Field()
    comment_count = scrapy.Field()
    female_count = scrapy.Field()
    male_count = scrapy.Field()
    age10 = scrapy.Field()
    age20 = scrapy.Field()
    age30 = scrapy.Field()
    age40 = scrapy.Field()
    age50 = scrapy.Field()
    tags = scrapy.Field()
