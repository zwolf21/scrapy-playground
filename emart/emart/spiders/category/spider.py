# -*- coding: utf-8 -*-
import scrapy

from emart.items import EmartItem

from .parsers.category_large import follow_medium_category
from .parsers.category_medium import follow_small_category
from .parsers.category_small import follow_product_list_page
from .parsers.product_list_page import follow_product_list
from .parsers.product_list import follow_product
from .parsers.product import parse_product, follow_tags
from .parsers.tags import parse_tags


class CategorySpider(scrapy.Spider):
    name = 'category'
    start_urls = ['http://emart.ssg.com']

    def __init__(self, large_category=None, medium_category=None, **kwargs):
        super().__init__(**kwargs)
        self.large_category = large_category
        self.medium_category = medium_category

    def parse(self, response):
        for flw in follow_medium_category(response, self.parse_medium_category, **self.__dict__):
            yield flw

    def parse_medium_category(self, response):
        for flw in follow_small_category(response, self.parse_small_category, **self.__dict__):
            yield flw

    def parse_small_category(self, response):
        for flw in follow_product_list_page(response, self.parse_product_list_page):
            yield flw

    def parse_product_list_page(self, response):
        for flw in follow_product_list(response, self.parse_product_list):
            yield flw

    def parse_product_list(self, response):
        for flw in follow_product(response, self.parse_product):
            yield flw

    def parse_product(self, response):
        parse_product(response)
        for flw in follow_tags(response, self.parse_tags):
            yield flw

    def parse_tags(self, response):
        item = parse_tags(response)
        yield EmartItem(**item)
