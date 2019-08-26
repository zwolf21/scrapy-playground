import furl
from scrapy.linkextractors import LinkExtractor

from ..items import WebToonItem


def _extract_thumbnail_src(response, titleId, **kwargs):
    contain = f"https://shared-comic.pstatic.net/thumb/webtoon/{titleId}/thumbnail/"
    for thumb in response.xpath(f"//img[contains(@src, '{contain}')]/@src"):
        return thumb.get()


def parse_webtoon_list(response):
    extractor = LinkExtractor(
        r'/webtoon/list.nhn\?titleId=\d+&weekday=\w+$',
        restrict_xpaths=".//a[@class='title']"
    )

    links = extractor.extract_links(response)
    for lnk in links:
        q = furl.furl(lnk.url).args
        item = WebToonItem(
            webtoon_title=lnk.text,
            webtoon_thumb_src=_extract_thumbnail_src(
                response, q['titleId']),
            **q
        )
        context = {
            'webtoon': item
        }
        yield lnk, context
