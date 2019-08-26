import re
import furl
from scrapy.linkextractors import LinkExtractor

from ..items import CutItem

REGX_CUT_SRC = r'https://image-comic.pstatic.net/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$'


def parse_episode(response):
    tid = response.qs['titleId']
    no = response.qs['no']
    xpath = f".//img[contains(@src, 'https://image-comic.pstatic.net/webtoon/{tid}/{no}')]/@src"

    for seq, x in enumerate(response.xpath(xpath), 1):
        yield CutItem(
            titleId=tid,
            no=no,
            cut_seq=seq,
            cut_src=x.get()
        )
