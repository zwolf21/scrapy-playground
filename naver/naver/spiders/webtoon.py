import re
from fnmatch import fnmatch
from collections.abc import Iterable
import scrapy
from scrapy.linkextractors import LinkExtractor

from ..utils.urlcuts import parse_query

REGX_WEBTOON = re.compile(
    r'/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w+)$'
)
REGX_EPISODE_LIST = re.compile(
    r'/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w+)&page=(?P<page>\d+)$'
)
REGX_EPISODE = re.compile(
    r'/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w+)$'
)


def parse_csv(values, apply=str):
    '''문자열 인수를 배열화 시켜준다.
    '''
    if isinstance(values, str):
        values = re.sub('/s', '', values)
        if ',' in values:
            results = values.split(',')
        elif '-' in values:
            results = values.split('-')
            s, *_, e = results
            s, e = int(s), int(e)
            results = range(s, e+1)
        else:
            results = [values]
        return list(map(apply, results))
    elif isinstance(values, (Iterable)):
        return list(map(apply, values))

    raise ValueError('values like: 1-10, 1,2,3,4')


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


def filter_toon_link(link, title, search=None, weekday=None, titleId=None, **kwargs):
    '''어떠한 웹툰을 필터링 할것인지 정한다.
    '''
    qs = parse_query(link)
    if titleId is not None:
        return qs.get('titleId') in parse_csv(titleId)
    if search is not None:
        pat_matched = fnmatch(title, search) or re.search(search, title)
    if weekday is not None:
        wk_matched = qs.get('weekday') in parse_csv(weekday)
    return pat_matched and wk_matched


def filter_episode_link(link, episode=None):
    '''연재 차수를 고른다 episode=1-10; episode=1,2,3,4
    '''
    qs = parse_query(link)
    if episode is not None:
        episodes = parse_csv(episode)
        return qs.get('no') in episodes
    return True


class WebtoonSpider(scrapy.Spider):
    name = 'webtoon'
    start_urls = ['https://comic.naver.com/webtoon/weekday.nhn']

    def __init__(self, search=None, weekday=None, titleId=None, episode=None, **kwargs):
        super().__init__(**kwargs)
        self.weekday = weekday
        self.search = search
        self.titleId = titleId
        self.episode = episode

    def parse(self, response):
        links = extract_link(
            response, REGX_WEBTOON,
            queryfields=['titleId', 'weekday'],
            # 해당 attr을 지는 테그로 추출범위를 한정한다.
            restrict_xpaths=".//a[@class='title']"
        )
        # print('self.titleId:', self.titleId)
        for url, text, ctx in links:
            ctx['toon_title'] = text
            if filter_toon_link(url, text, **self.__dict__):
                # 필터링 조건을 통과한 웹툰을 대상으로만 재귀적으로 크롤링 한다.
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
            ctx['episode_title'] = text
            ctx.update(context)
            if filter_episode_link(url, self.episode):
                # 에피소드 리스트 필터링
                yield response.follow(url, self.parse_episode_page, meta={'context': ctx})

    def parse_episode_page(self, response):
        context = response.meta['context']
        print(context)
