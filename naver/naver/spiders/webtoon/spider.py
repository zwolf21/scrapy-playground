# -*- coding: utf-8 -*-
import scrapy
import pynumparser
from furl import furl
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider

from .parsers.webtoon import parse_webtoon
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
            callback=parse_webtoon, follow=True, process_links='process_webtoon_link'
        ),
        Rule(
            LinkExtractor(
                r'/webtoon/list.nhn\?titleId=\d+&weekday=\w+&page=\d+$',
            ),
            callback=parse_episode_list,
            process_links='process_episode_list_link',
            follow=True
        ),
        Rule(
            LinkExtractor(
                r'/webtoon/detail.nhn\?titleId=\d+&no=\d+&weekday=\w+$'
            ),
            callback=parse_episode,
            process_links='process_episode_link',
            follow=True,
        ),
    ]

    def __init__(self, search=None, weekday=None, titleId=None, episode=None, **kwargs):
        super().__init__(**kwargs)
        self.weekday = weekday
        self.search = search
        self.titleId = titleId
        self.episodes = episode
        if episode is not None:
            num_parser = pynumparser.NumberSequence(limits=[1, 9999])
            self.episodes = num_parser(self.episodes)
            self.retrieved_episodes = []

        self.min_page_number = 1

    def process_webtoon_link(self, links):
        return filter_toon_link(links, **self.__dict__)

    def process_episode_list_link(self, links):
        for link in links:
            qs = furl(link.url).args
            page_no = int(qs['page'])
            if page_no > self.min_page_number:
                yield link

    def process_episode_link(self, links):
        for link in links:
            qs = furl(link.url).args
            no = int(qs['no'])
            if self.episodes is None or self.titleId is None:
                yield link
            else:
                if no in self.episodes:
                    self.retrieved_episodes.append(no)
                    yield link

                if set(self.episodes) == set(self.retrieved_episodes):
                    # print(self.episodes)
                    # print(self.retrieved_episodes)
                    raise CloseSpider('선택한 에피소드 스크래핑 완료')
