import scrapy


class ReplicaSpider(scrapy.Spider):
    name = "replica"
    allowed_domains = ["www.myreplica.ru"]
    start_urls = ["https://www.myreplica.ru"]

    def parse(self, response):
        pass
