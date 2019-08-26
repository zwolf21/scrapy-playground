import scrapy


class WebToonItem(scrapy.Item):
    titleId = scrapy.Field()
    weekday = scrapy.Field()
    webtoon_title = scrapy.Field()
    webtoon_thumb_src = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()


class EpisodeItem(scrapy.Item):
    titleId = scrapy.Field()
    no = scrapy.Field()
    episode_title = scrapy.Field()
    episode_thumb_src = scrapy.Field()
    published_date = scrapy.Field()
    rating = scrapy.Field()


class CutItem(scrapy.Item):
    titleId = scrapy.Field()
    no = scrapy.Field()
    cut_seq = scrapy.Field()
    cut_src = scrapy.Field()
