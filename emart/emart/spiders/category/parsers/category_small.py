import re
import fnmatch

import furl
from scrapy.linkextractors import LinkExtractor


def follow_product_list_page(response, *args, **kwargs):
    xpath_xmall = "//div[@class='cmflt_filbox_cts']//a[@data-ilparam-value]"
    ctx = response.meta['context']
    for x in response.xpath(xpath_xmall):
        small_category_code = x.xpath("./@data-ilparam-value").get()
        small_category_name = x.xpath("./text()").get()
        link = f"/category/main.ssg?dispCtgId={small_category_code}&pageSize=100"
        context = dict(
            ctg_small=small_category_name
        )
        context.update(ctx)
        yield response.follow(link, *args, meta={'context': context})
