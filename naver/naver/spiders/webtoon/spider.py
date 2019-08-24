# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from .parsers.webtoon_list import parse_webtoon_list
from .parsers.episode_list import parse_episode_list
from .parsers.episode import parse_episode
from .filters import filter_toon_link, filter_episode_link


class WebtoonSpider(CrawlSpider):
    name = 'webtoon'
    start_urls = ['https://comic.naver.com/webtoon/weekday.nhn']

    rules = [
        Rule(
            LinkExtractor(r'https://comic.naver.com/webtoon/weekday.nhn$'),
            callback=parse_webtoon_list, follow=True
        ),
        Rule(
            LinkExtractor(
                r'/webtoon/list.nhn\?titleId=\d+&weekday=\w+$',
                restrict_xpaths=(".//a[@class='title']")
            ),
            callback=parse_episode_list, follow=True, process_links='process_episode_list_link'
        ),
        Rule(
            LinkExtractor(
                r'/webtoon/list.nhn\?titleId=\d+&weekday=\w+&page=\d+$',
            ),
            callback=parse_episode_list, follow=True
        ),
        Rule(
            LinkExtractor(
                r'/webtoon/detail.nhn\?titleId=\d+&no=\d+&weekday=\w+$'
            ),
            callback=parse_episode,
            process_links='procecss_episode_link',
            follow=True,
        ),
    ]

    def __init__(self, search=None, weekday=None, titleId=None, episode=None, **kwargs):
        super().__init__(**kwargs)
        self.weekday = weekday
        self.search = search
        self.titleId = titleId
        self.episode = episode

    def process_episode_list_link(self, links):
        return filter_toon_link(links, **self.__dict__)

    def procecss_episode_link(self, links):
        return filter_episode_link(links, **self.__dict__)
