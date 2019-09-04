from scrapy.linkextractors import LinkExtractor


def follow_product(response, *args, **kwargs):
    xpath_item_link = "//div[@class='cunit_info']//a[contains(@href, '/item/itemView.ssg')]/@href"
    for x in response.xpath(xpath_item_link):
        link = x.get()
        yield response.follow(link, *args, meta=response.meta)
