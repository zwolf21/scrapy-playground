import re
import fnmatch

import furl
from scrapy.linkextractors import LinkExtractor


def filter_large_category(text, large_category, **kwargs):
    if large_category:
        return re.search(large_category, text)
    return True


def follow_medium_category(response, *args, **kwargs):
    xpath_medium = "//li[@class='emlnb_top_mn']"
    for x in response.xpath(xpath_medium):
        large_category_code = x.xpath('./@data-ctg-code').get()
        large_category_name = x.xpath('./a/text()').get()
        link = f"/category/main.ssg?dispCtgId={large_category_code}"
        if filter_large_category(large_category_name, **kwargs):
            context = dict(
                ctg_large=large_category_name
            )
            yield response.follow(link, *args, meta={'context': context})
