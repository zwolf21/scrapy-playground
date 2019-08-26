import re
import fnmatch

import furl
from scrapy.linkextractors import LinkExtractor

from ..items import WebToonItem


def filter_follow_link(link, titleId=None, weekday=None, search=None, **kwargs):
    url = link.url
    title = link.text
    qs = furl.furl(link).args
    if titleId is not None:
        return qs['titleId'] == titleId
    pattern_match = True
    weekday_match = True
    if search is not None:
        pattern_match = fnmatch.fnmatch(
            title, search) or re.search(search, title)
    if weekday is not None:
        weekday_match = qs['weekday'] in weekday
    return pattern_match and weekday_match


def follow_webtoon(response, *args, **kwargs):
    extractor = LinkExtractor(
        r'/webtoon/list.nhn\?titleId=\d+&weekday=\w+$',
        restrict_xpaths=".//a[@class='title']"
    )
    links = extractor.extract_links(response)
    for lnk in links:
        if filter_follow_link(lnk, **kwargs):
            yield response.follow(lnk.url, *args)
