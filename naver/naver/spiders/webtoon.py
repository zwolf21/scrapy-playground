import re

import scrapy
from scrapy.linkextractors import LinkExtractor

REGX_WEBTOON = re.compile(
    r'/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w+)$'
)
REGX_EPISODE_LIST = re.compile(
    r'/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w+)&page=(?P<page>\d+)$'
)
REGX_EPISODE = re.compile(
    r'/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w+)$'
)


def extract_link(response, regx, queryfields=None, **kwargs):
    regx = re.compile(regx)
    extractor = LinkExtractor(regx, **kwargs)
    links = []
    for link in extractor.extract_links(response):
        url = link.url
        text = link.text
        context = {}
        g = regx.search(url)
        if g and queryfields:
            m = g.group
            for field in queryfields:
                context[field] = m(field)
        links.append([url, text, context])
    return links


class WebtoonSpider(scrapy.Spider):
    name = 'webtoon'
    start_urls = ['https://comic.naver.com/webtoon/weekday.nhn']

    def parse(self, response):
        links = extract_link(
            response, REGX_WEBTOON,
            queryfields=['titleId', 'weekday'],
            restrict_xpaths=".//a[@class='title']"
        )
        for url, text, ctx in links:
            ctx['toon_title'] = text
            yield response.follow(url, self.gen_episode_page_link, meta={'context': ctx})

    def gen_episode_page_link(self, response):
        def calc_last_page(response):
            links = extract_link(
                response, REGX_EPISODE,
                queryfields=['no']
            )
            episode_nolist = set([int(ctx['no']) for url, text, ctx in links])
            latest_no = max(episode_nolist)
            episode_count = len(episode_nolist)
            last_page = latest_no // episode_count
            if latest_no > episode_count:
                last_page += 1
            return range(1, last_page+1)

        for page in calc_last_page(response):
            url = f"{response.url}&page={page}"
            yield response.follow(url, self.parse_episode_list_page, meta=response.meta)

    def parse_episode_list_page(self, response):
        context = response.meta['context']
        links = extract_link(
            response, REGX_EPISODE,
            queryfields=['no'],
            restrict_xpaths=".//a[contains(@onclick, 'lst.title')]"
        )
        for url, text, ctx in links:
            context['episode_title'] = text
            context.update(ctx)
            yield response.follow(url, self.parse_episode_page, meta={'context': context})

    def parse_episode_page(self, response):
        context = response.meta['context']
        print(context)
