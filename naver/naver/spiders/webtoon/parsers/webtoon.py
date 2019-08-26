import furl
from scrapy.linkextractors import LinkExtractor

from ..items import EpisodeItem

link_extractor = LinkExtractor(
    r'/webtoon/detail.nhn\?titleId=\d+&no=\d+&weekday=\w+$',
    restrict_xpaths=".//a[contains(@onclick, 'lst.title')]"
)


def _extract_description(response):
    xpath = "//div[@class='comicinfo']/div[@class='detail']/p/text()"
    return '\n'.join([desc.get() for desc in response.xpath(xpath)])


def _extract_thumbnail_src(response, titleId, no, **kwargs):
    contain = f"https://shared-comic.pstatic.net/thumb/webtoon/{titleId}/{no}/"
    for thumb in response.xpath(f"//img[contains(@src, '{contain}')]/@src"):
        return thumb.get()


def _extract_author(response):
    xpath = ".//span[@class='wrt_nm']/text()"
    return response.xpath(xpath).get().strip()


def _calc_episode_page_range(response):
    episode_nolist = []
    for lnk in link_extractor.extract_links(response):
        qs = furl.furl(lnk.url).args
        episode_nolist.append(int(qs['no']))
    latest_no = max(episode_nolist)
    episode_count = len(episode_nolist)
    last_page = latest_no // episode_count
    if latest_no > episode_count:
        last_page += 1
    return range(1, last_page+1)


def parse_webtoon(response):
    webtoon = response.meta['webtoon']
    webtoon['description'] = _extract_description(response)
    webtoon['author'] = _extract_author(response)
    yield webtoon


def follow_episode_list_page(response, *args, **kwargs):
    for page in _calc_episode_page_range(response):
        yield response.follow(f"{response.url}&page={page}", *args, **kwargs)
