import re

import scrapy

from ..items import EmartItem


class CategorySpider(scrapy.Spider):
    name = 'category'
    start_urls = ['http://emart.ssg.com']

    def __init__(self, large_category=None, medium_category=None, small_category=None, xmall_category=None, page_size=100, **kwargs):
        super().__init__(**kwargs)
        self.large_category = large_category
        self.medium_category = medium_category
        self.small_category = small_category
        self.xmall_category = xmall_category
        self.page_size = page_size

    def parse(self, response):
        xpath_category_lg = "//ul[@class='em_lnb_lst']//li"
        for elm in response.xpath(xpath_category_lg):
            ctg_code = elm.xpath("./@data-ctg-code").get()
            ctg_name = elm.xpath('./a/text()').get()
            link = f"/category/main.ssg?dispCtgId={ctg_code}"
            if self.large_category:
                if not re.search(self.large_category, ctg_name):
                    continue
            ctx = dict(ctg_lg=ctg_name)
            yield response.follow(link, self.follow_medium, meta={'context': ctx})

    def follow_medium(self, response):
        context = response.meta['context']
        xpath_category_md = "//ul[contains(@class, 'cmflt_ctlist_high')]//a"
        for elm in response.xpath(xpath_category_md):
            mctg_name = elm.xpath("./text()").get()
            mctg_code = elm.xpath("./@data-ilparam-value").get()
            link = f"/category/main.ssg?dispCtgId={mctg_code}"
            if self.medium_category:
                if not re.search(self.medium_category, mctg_name):
                    continue
            ctx = dict(ctg_md=mctg_name)
            ctx.update(context)
            yield response.follow(link, self.follow_small, meta={'context': ctx})

    def follow_small(self, response):
        context = response.meta['context']
        xpath_category_sm = "//div[@id='category_filter']//a"
        for elm in response.xpath(xpath_category_sm):
            sctg_name = elm.xpath("./text()").get()
            sctg_code = elm.xpath("./@data-ilparam-value").get()
            link = f"/category/main.ssg?dispCtgId={sctg_code}"
            if self.small_category:
                if not re.search(self.small_category, sctg_name):
                    continue
            ctx = dict(ctg_sm=sctg_name)
            ctx.update(context)
            yield response.follow(link, self.follow_xmall, meta={'context': ctx})

    def follow_xmall(self, response):
        context = response.meta['context']
        # 하위카테고리를 더 가진 경우: 한번더 진입하여 페이지네이션
        xpath_category_xm = "//ul[contains(@class, 'cmflt_ctlist_last')]//a"
        for elm in response.xpath(xpath_category_xm):
            xctg_name = elm.xpath("./text()").get()
            xctg_code = elm.xpath("./@data-ilparam-value").get()
            link = f"/category/main.ssg?dispCtgId={xctg_code}"
            if self.xmall_category:
                if not re.search(self.xmall_category, xctg_name):
                    continue
            ctx = dict(ctg_xm=xctg_name)
            ctx.update(context)
            yield response.follow(link, self.paginate_item_list, meta={'context': ctx})

        # 하위 카테고리가 더 이상 없는경우: 바로 페이지네이션
        context['ctg_xm'] = ''
        return self.paginate_item_list(response)

    def paginate_item_list(self, response):
        def _get_item_count(response):
            xpath_total_count = "//div[@id='item_count']//em/text()"
            for x in response.xpath(xpath_total_count):
                count = x.get()
                if count:
                    count = count.replace(',', '')
                    return int(count.strip())

        total_item_count = _get_item_count(response)
        last_page = total_item_count // self.page_size + 1
        for npage in range(1, last_page+1):
            link = f"{response.url}&pageSize={self.page_size}&page={npage}"
            yield response.follow(link, self.follow_item_list, meta=response.meta)

    def follow_item_list(self, response):
        xpath_item_detail = "//div[@id='area_itemlist']//a[@data-info]"
        for elm in response.xpath(xpath_item_detail):
            item_code = elm.xpath("./@data-info").get()
            link = f"http://emart.ssg.com/item/itemView.ssg?itemId={item_code}"
            yield response.follow(link, self.parse_item, meta=response.meta)

    def parse_item(self, response):
        context = response.meta['context']

        item_code = response.qs['itemId']
        brand_name = ''
        item_name = ''
        img_src = ''
        comment_count = 0
        female_count = 0
        male_count = 0

        xpath_item = response.xpath("//div[@class='cdtl_col_rgt']")

        for elm in xpath_item.xpath(".//a[contains(@href, '/disp/brandShop.ssg')]/text()"):
            brand_name = elm.get()
            brand_name = brand_name.replace('#', '').strip()

        for elm in xpath_item.xpath(".//h2[@class='cdtl_info_tit']/text()"):
            item_name = elm.get()

        for elm in response.xpath("//img[@id='mainImg']/@src"):
            img_src = elm.get()

        for elm in response.xpath("//div[@class='cdtl_sec_titarea']//span[@class='count']//em/text()"):
            count = elm.get()
            count = count.replace(',', '').strip()
            comment_count = int(count)

        for elm in response.xpath("//div[@class='cdtl_grp_sex']//li[contains(@class, 'cdtl_female')]//span[@class='cdtl_grp_prgrss_per']/text()"):
            female_ratio = elm.get()
            female_ratio = female_ratio.replace('%', '').strip()
            female_ratio = int(female_ratio) / 100
            female_count = int(comment_count * female_ratio)
            male_count = comment_count - female_count

        def _parse_age_pct(response):
            xpath = "//div[@class='cdtl_grp_age']//li"
            ret = {}
            for x in response.xpath(xpath):
                age_level = x.xpath(
                    ".//span[@class='cdtl_grp_prgrss_cnt']//text()").get()
                age_pct = x.xpath(
                    ".//span[@class='cdtl_grp_prgrss_per']//text()").get()
                if age_level:
                    age_level = re.sub('[대이상\s]', '', age_level)
                    age_level = f"age{age_level}"
                    ret[age_level] = int(age_pct) / 100
            return ret

        ctx = dict(
            brand_name=brand_name,
            item_code=item_code,
            item_name=item_name,
            img_src=img_src,
            comment_count=comment_count,
            female_count=female_count,
            male_count=male_count,
            **_parse_age_pct(response)
        )
        ctx.update(context)

        link = f"/pitem/ajaxSrchRcmdTag.ssg?itemId={item_code}"
        yield response.follow(link, self.parse_tag, meta={'context': ctx})

    def parse_tag(self, response):
        context = response.meta['context']

        def _parse_tags(response):
            xpath = "//div[@class='recomm_hash_row']"
            tag_list = []
            for x in response.xpath(xpath):
                tag_group = x.xpath(
                    ".//div[@class='tit']//strong/text()").get()
                if tag_group and '연관태그' in tag_group:
                    for t in x.xpath(".//div[@class='recomm_lst v2']//li/a/text()"):
                        tag = t.get()
                        if tag:
                            tag = tag.replace('#', '')
                            tag_list.append(tag)
                    break
            return ','.join(tag_list)
        ctx = dict(
            tags=_parse_tags(response)
        )
        ctx.update(context)
        yield EmartItem(**ctx)
