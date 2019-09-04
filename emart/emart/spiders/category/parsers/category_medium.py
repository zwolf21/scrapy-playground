import re
import fnmatch

import furl
from scrapy.linkextractors import LinkExtractor


def filter_medium_category(text, medium_category, **kwargs):
    if medium_category:
        return re.search(medium_category, text)
    return True


def follow_small_category(response, *args, **kwargs):
    xpath_small = "//div[@class='cmfltExpContent']//a[@data-ilparam-value]"
    ctx = response.meta['context']
    for x in response.xpath(xpath_small):
        medium_category_code = x.xpath('./@data-ilparam-value').get()
        medium_category_name = x.xpath('./text()').get()
        link = f"/category/main.ssg?dispCtgId={medium_category_code}"
        if filter_medium_category(medium_category_name, **kwargs):
            context = dict(
                ctg_medium=medium_category_name
            )
            context.update(ctx)
            yield response.follow(link, *args, meta={'context': context})
