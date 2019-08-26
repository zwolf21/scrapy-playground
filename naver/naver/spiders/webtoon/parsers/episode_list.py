import furl
from scrapy.linkextractors import LinkExtractor

from ..items import EpisodeItem


def parse_episode_list(response):
    xpath_row = "//table[@class='viewList']//tr"
    for element in response.xpath(xpath_row):
        link = element.xpath(
            "./td/a[contains(@href, '/webtoon/detail.nhn') and contains(@onclick, 'lst.title')]/@href").get()
        if not link:
            continue

        thumbnail = element.xpath(
            "./td/a/img[contains(@src, 'https://shared-comic.pstatic.net/thumb/webtoon')]/@src"
        ).get()
        title = element.xpath("./td[@class='title']/a/text()").get()
        rating = element.xpath(
            "./td/div[@class='rating_type']//strong/text()"
        ).get()
        published = element.xpath("./td[@class='num']/text()").get()
        published = published.replace('.', '-')

        qs = furl.furl(link).args
        yield EpisodeItem(
            titleId=qs['titleId'],
            no=qs['no'],
            episode_title=title,
            episode_thumb_src=thumbnail,
            published_date=published,
            rating=rating
        )


def follow_episode(response, *args, **kwargs):
    extractor = LinkExtractor(
        r'/webtoon/detail.nhn\?titleId=\d+&no=\d+&weekday=\w+$',
        restrict_xpaths=".//a[contains(@onclick, 'lst.title')]"
    )
    for link in extractor.extract_links(response):
        yield response.follow(link.url, *args, **kwargs)
