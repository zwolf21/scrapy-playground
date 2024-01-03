from furl import furl

from naverkin.utils import prettify_content
from naverkin.items import QuestionInfoItem
from .shortcuts import gen_slug



@prettify_content
def _extract_question_title(area):
    if elm_title := area.xpath(".//div[@class='title']//text()").get():
        return elm_title

@prettify_content
def _extract_question_content(area):
    if elm_content := area.xpath(".//div[@class='c-heading__content']//text()").getall():
        return elm_content


@prettify_content
def _extract_question_pub_date(area):
    if text_date := area.xpath(".//span[text()='작성일']/parent::span/text()").get():
        return text_date.replace('.', '-').strip()



def parse(response, search_keywords=None):
    area = response.xpath(".//div[@class='question-content']")
    qs = furl(response.url).args
    item = QuestionInfoItem(
        slug = gen_slug(*[qs[key] for key in ['d1id', 'dirId', 'docId']]),
        url = response.url,
        search_keywords = search_keywords,
        title = _extract_question_title(area) 
    )
    return item




    