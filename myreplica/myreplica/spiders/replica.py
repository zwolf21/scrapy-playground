from typing import Iterable
import scrapy
from scrapy.http import Request, Response
from scrapy.utils.project import get_project_settings

from scrapgo.lib import fjoin, get_logger, npaginator, find_json, try2datetime, fbasename, fexists, clear4pathname, parse_number
import listorm, diselect

from ..utils import extract_size, synk_images_by_records, get_resource_path



class ReplicaSpider(scrapy.Spider):
    name = "replica"

    def start_requests(self) -> Iterable[Request]:
        yield scrapy.Request('https://www.myreplica.ru', self.parse_home, meta={'dont_cache': True})
    
    def parse_home(self, response: Response, page=None, url_list=None):
        xp_total_count = response.xpath('//*[@class="woocommerce-result-count"]/text()').get()
        xp_product_list = response.xpath('//*[@class="woocommerce-loop-product__title"]')
        total_count = parse_number(xp_total_count)
        page_size = len(xp_product_list)

        url_list = url_list or  []
        for url in response.xpath('//*[@class="woocommerce-loop-product__title"]/a/@href').getall():
            # yield scrapy.Request(
            #     url, self.parse_product
            # )
            url_list.append(url)

        for page in npaginator(page_size, total_count):
            yield scrapy.Request(
                f'https://www.myreplica.ru/page/{page}/',
                self.parse_home,
                meta={'dont_cache': True},
                priority=1,
                cb_kwargs={'page': page, 'url_list': url_list}
            )

        print('url_list', len(url_list))

    
    def parse_page(self, response: Response):
        pass

    def parse_product(self, response: Response):
        json_content = response.soup.select_one('script[type="application/ld+json"]').get_text(strip=True)
        description = response.soup.select_one('#tab-description').get_text('\n', strip=True)
        product = {
            'product_url': response.url,
            'product_id': '',
            'product_name': '',
            'brand_name': '',
            'description': description,
            'size': extract_size(description),
            'price': '',
            'published': '',
        }

        image_urls = [
            a['href'] for a in response.soup.select('.thumbnails a[href]' )
        ]

        if data:=find_json(json_content, many=False):
            for dataset in data['@graph']:
                if data_type := dataset.get('@type'):
                    if data_type == 'Product':
                        diquery = {
                            ('offers', 'url'): ('product_id', lambda url: fbasename(url.strip('/'))),
                            ('name', ):('product_name', lambda name: clear4pathname(name.replace('- MyReplica', '').strip())),
                            ('brand', 'name'): ('brand_name', str.upper),
                            # ('description', ): 'description',
                            ('offers', 'price'): 'price',
                        }
                        for row in diselect.diselect(dataset, diquery):
                            product.update(row)
                            break

                    if data_type == 'ItemPage':
                        date = try2datetime(dataset['datePublished'])
                        product['published'] = str(date)

        yield product

