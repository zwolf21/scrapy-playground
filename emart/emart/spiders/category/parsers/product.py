import re


def _parse_itemName(response):
    xpath = "//div[@id='content']//h2[@class='cdtl_info_tit']/text()"
    name = response.xpath(xpath).get()
    return name or ""


def _parse_itemPrice(response):
    xpath = "//div[@id='content']//em[@class='ssg_price']//text()"
    price = response.xpath(xpath).get()
    if price:
        price = price.replace(',', '')
        return price
    return ""


def _parse_currencyUnit(response):
    xpath = "//div[@id='content']//span[@class='ssg_tx']//text()"
    for x in response.xpath(xpath):
        return x.get()
    return ""

#content > div > div.cdtl_row_top > div.cdtl_col_rgt > div.cdtl_info_wrap > div.cdtl_optprice_wrap > p


def _parse_perPriceInfo(response):
    xpath = "//div[@id='content']//p[@class='cdtl_txt_info hide_gl']/text()"
    regx = re.compile(
        r'\((?P<unit>.+) 당 \:\s*(?P<price>.+)원, 총 용량 \: (?P<amount>.+)\)')

    for x in response.xpath(xpath):
        info = x.get() or ""
        m = regx.search(info)
        if m:
            g = m.group
            return g('unit'), g('price'), g('amount')
    return "", "", ""


def _parse_img_src(response):
    xpath = "//img[@id='mainImg']/@src"
    src = response.xpath(xpath).get()
    return src or ""


def _parse_commentCount(response):
    xpath = "//div[@class='cdtl_sec_titarea']//span[@class='count']//em/text()"
    for x in response.xpath(xpath):
        count = x.get() or "0"
        count = count.replace(',', '')
        return int(count)


def _parse_sex_pct(response):
    xpath = "//div[@class='cdtl_grp_sex']"
    for x in response.xpath(xpath):
        female = x.xpath(
            ".//li[contains(@class, 'cdtl_female')]//span[@class='cdtl_grp_prgrss_per']/text()").get()
        if female:
            ratio_female = int(female)/100
            return ratio_female, 1-ratio_female
    return 0, 0


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


def parse_product(response):
    ctx = response.meta['context']

    amountUnit, _, pkgAmount = _parse_perPriceInfo(response)
    ratio_femail, ratio_mail = _parse_sex_pct(response)
    age_pct = _parse_age_pct(response)
    context = dict(
        itemId=response.qs['itemId'],
        itemName=_parse_itemName(response),
        img_src=_parse_img_src(response),
        link=response.url,
        pkgPrice=_parse_itemPrice(response),
        currencyUnit=_parse_currencyUnit(response),
        amountUnit=amountUnit,
        pkgAmount=pkgAmount,
        commentCount=_parse_commentCount(response),
        femailRatio=ratio_femail,
        mailRatio=ratio_mail,
        **age_pct
    )
    context.update(ctx)
    response.meta['context'] = context


def follow_tags(response, *args, **kwargs):
    itemId = response.qs['itemId']
    link = f"/pitem/ajaxSrchRcmdTag.ssg?itemId={itemId}"
    yield response.follow(link, *args, meta=response.meta)
