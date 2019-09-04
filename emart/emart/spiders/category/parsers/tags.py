def _parse_tags(response):
    xpath = "//div[@class='recomm_hash_row']"
    tag_list = []
    for x in response.xpath(xpath):
        tag_group = x.xpath(".//div[@class='tit']//strong/text()").get()
        if tag_group and '연관태그' in tag_group:
            for t in x.xpath(".//div[@class='recomm_lst v2']//li/a/text()"):
                tag = t.get()
                if tag:
                    tag = tag.replace('#', '')
                    tag_list.append(tag)
            break
    return ','.join(tag_list)


def parse_tags(response):
    ctx = response.meta['context']
    context = dict(
        tags=_parse_tags(response)
    )
    context.update(ctx)
    return context
