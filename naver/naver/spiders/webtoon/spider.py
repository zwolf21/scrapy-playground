# -*- coding: utf-8 -*-
import scrapy

from .parsers.kwargs import parse_number_range_exp
from .parsers.webtoon_list import parse_webtoon_list
from .parsers.webtoon import parse_webtoon, follow_episode_list_page
from .parsers.episode_list import parse_episode_list, follow_episode
from .parsers.episode import parse_episode


class WebtoonSpider(scrapy.Spider):
    name = 'webtoon'
    start_urls = ['https://comic.naver.com/webtoon/weekday.nhn']

    def __init__(self, titleId=None, weekday=None, no=None, search=None, **kwargs):
        super().__init__(**kwargs)
        self.titleId = titleId
        self.weekday = weekday
        self.no = parse_number_range_exp(no)
        self.search = search

    def parse(self,  response):
        print('*'*200)
        for link, meta in parse_webtoon_list(response):
            yield response.follow(link, self.parse_webtoon, meta=meta)

    def parse_webtoon(self, response):
        # for webtoon in parse_webtoon(response):
        #     yield webtoon
        for flw in follow_episode_list_page(response, self.parse_episode_list):
            yield flw

    def parse_episode_list(self, response):
        # for episode in parse_episode_list(response):
        #     yield episode
        for flw in follow_episode(response, self.parse_episode):
            yield flw

    def parse_episode(self, response):
        for cut in parse_episode(response):
            yield cut
