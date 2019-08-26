import re
from scrapy.linkextractors import LinkExtractor


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


def extract_thumbnail_src(response, contains, titleId, no):
    contain = f"https://shared-comic.pstatic.net/thumb/webtoon/{titleId}/{no}/"
    for thumb in response.xpath(f"//img[contains(@src, '{contain}')]/@src"):
        return thumb.get()
