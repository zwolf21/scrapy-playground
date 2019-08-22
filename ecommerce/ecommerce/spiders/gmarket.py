import re
import scrapy
from scrapy.linkextractors import LinkExtractor

from ..items import EcommerceItem


class GmarketSpider(scrapy.Spider):
    name = 'gmarket'
    allowed_domains = ['corners.gmarket.co.kr']
    start_urls = [
        'http://corners.gmarket.co.kr/Bestsellers/',
    ]

    def parse(self, response):
        context = dict(
            main_category_name='All',
            sub_category_name='All',
            viewType='G',
            groupCode='G00'
        )
        for item in _parse_item_list(response, context):
            yield item
        regx = re.compile(
            r'/Bestsellers\?viewType=(?P<viewType>.+)&groupCode=(?P<groupCode>.+)'
        )
        link_extractor = LinkExtractor(regx)
        for lnk in link_extractor.extract_links(response):
            m = regx.search(lnk.url).group
            context = dict(
                main_category_name=lnk.text,
                viewType=m('viewType'),
                groupCode=m('groupCode')
            )
            yield response.follow(lnk.url, self.parse_main_category, meta={'context': context})

    def parse_main_category(self, response):
        context = response.meta['context']
        for item in _parse_item_list(response):
            yield item
        regx = re.compile(
            r'/Bestsellers\?viewType=(?P<viewType>.+)&groupCode=(?P<groupCode>.+)&subGroupCode=(?P<subGroupCode>.+)'
        )
        link_extractor = LinkExtractor(regx)
        for lnk in link_extractor.extract_links(response):
            m = regx.search(lnk.url).group
            context['sub_category_name'] = lnk.text
            context['subGroupCode'] = m('subGroupCode')
            yield response.follow(lnk.url, self.parse_sub_category, meta={'context': context})

    def parse_sub_category(self, response):
        for item in _parse_item_list(response):
            yield item


def _parse_price(value):
    return int(re.sub(r'[원월,]', '', value).strip())


def _parse_item_list(response, context=None):
    context = context or response.meta['context']
    xpath_item_list = "//div[@class='best-list']//li[@id]"
    for item in response.xpath(xpath_item_list):
        item_name = item.xpath(".//a[@class='itemname']/text()").get()
        o_price = item.xpath(".//div[@class='o-price']//span/text()").get()
        s_price = item.xpath(".//div[@class='s-price']//span/text()").get()
        sale = item.xpath(".//div[@class='s-price']//em/text()").get()
        price = s_price or o_price or '0'
        sale = sale or '0%'
        item = dict(
            title=item_name,
            price=_parse_price(price),
            sale=sale
        )
        item.update(context)
        yield EcommerceItem(**item)
