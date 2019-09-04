import re
import fnmatch

import furl
from scrapy.linkextractors import LinkExtractor


def _get_item_count(response):
    xpath_total_count = "//div[@id='item_count']//em/text()"
    for x in response.xpath(xpath_total_count):
        count = x.get()
        if count:
            count = count.replace(',', '')
            return int(count.strip())


def follow_product_list(response, *args, **kwargs):
    total_item_count = _get_item_count(response)
    pageSize = 100
    last_page = total_item_count // pageSize + 1
    for page_number in range(1, last_page+1):
        link = f"{response.url}&page={page_number}"
        yield response.follow(link, *args, meta=response.meta)
