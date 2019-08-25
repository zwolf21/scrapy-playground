import re
from fnmatch import fnmatch

from .shortcuts import parse_csv
from naver.utils.urlcuts import parse_query


def filter_toon_link(links, search=None, weekday=None, titleId=None, **kwargs):
    '''어떠한 웹툰을 필터링 할것인지 정한다.
    '''
    for link in links:
        url = link.url
        title = link.text
        qs = parse_query(url)
        pat_matched, wk_matched = True, True
        if titleId is not None:
            if qs.get('titleId') in parse_csv(titleId):
                yield link
        if search is not None:
            pat_matched = fnmatch(title, search) or re.search(search, title)
        if weekday is not None:
            wk_matched = qs.get('weekday') in parse_csv(weekday)
        if pat_matched and wk_matched:
            yield link


def filter_episode_link(links, episode=None, **kwargs):
    '''연재 차수를 고른다 episode=1-10; episode=1,2,3,4
    '''
    for link in links:
        qs = parse_query(link.url)
        if episode is not None:
            episodes = parse_csv(episode)
            if qs.get('no') in episodes:
                yield link
            continue
        yield link
