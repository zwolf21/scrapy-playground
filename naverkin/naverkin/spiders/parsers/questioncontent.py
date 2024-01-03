import math
from furl import furl

from naverkin.utils import prettify_content
from naverkin.items import QuestionContentItem
from .shortcuts import gen_slug
from scrapy.utils.url import add_or_replace_parameters


@prettify_content
def _extract_question_author_name(area):
    if author_name := area.xpath(".//span[@class='c-userinfo__author']/text()").get():
        return author_name

@prettify_content
def _extract_question_content(area):
    if elm_content := area.xpath(".//div[@class='c-heading__content']//text()").getall():
        return elm_content

@prettify_content
def _extract_question_pub_date(area):
    if text_date := area.xpath(".//span[text()='작성일']/parent::span/text()").get():
        return text_date.replace('.', '-').strip()

def _extract_comment_count(area):
    if text_count := area.xpath(".//em[contains(@class, '_commentCnt')]/text()").get():
        return int(text_count.strip() or 0)
    return 0

@prettify_content
def _extract_answer_author_name(area):
    title_texts = area.xpath(".//p[@class='title']//text()").getall()
    title_texts = map(lambda s: s.replace(' 님 답변', ''), title_texts)
    title_texts = map(lambda s: s.replace('비공개 답변', '비공개'), title_texts)
    title_texts = map(lambda s: s.replace('작성자가 직접 삭제한 답변입니다', ''), title_texts)
    return title_texts

def _extract_answer_author_uid(area):
    if author_url := area.xpath(".//p[@class='title']//a/@href").get():
        f = furl(author_url)
        return f.args.get('u') or f.args.get('storeId')

@prettify_content
def _extract_answer_content(area):
    # 하위 요소중 일부를 제외하는 xpath식
    content_texts = area.xpath(".//div[contains(@class, 'c-heading-answer__content')]//*[not(contains(@class, 'c-guideline'))]//text()").getall()
    return content_texts

def _extract_answer_pubdate(area):
    if pub_date := area.xpath(".//p[@class='c-heading-answer__content-date']//text()").get():
        return pub_date.replace('.', '-').strip('-')



def _parse_question(area, slug_args):
    answer_no = 0
    args = slug_args + [answer_no]
    return QuestionContentItem(
        slug=gen_slug(*args),
        answer_no=answer_no,
        author_name=_extract_question_author_name(area),
        author_uid = None,
        type='질문',
        content=_extract_question_content(area),
        published=_extract_question_pub_date(area),
        comment_count = _extract_comment_count(area)
    )


def _parse_answers(area, slug_args):
    _, answer_no = area.xpath('./@id').get().split('_')
    args = slug_args + [answer_no]
    return QuestionContentItem(
        slug=gen_slug(*args),
        answer_no=answer_no,
        author_name=_extract_answer_author_name(area),
        author_uid=_extract_answer_author_uid(area),
        type='답변',
        content=_extract_answer_content(area),
        published=_extract_answer_pubdate(area),
        comment_count = _extract_comment_count(area)
    )


def parse_list(response):
    query = furl(response.url).args
    slug_args_base = [query[k] for k in ['d1id', 'dirId', 'docId']]
    area_question = response.xpath(".//div[@class='question-content']")
    areas_answer = response.xpath(".//div[starts-with(@id, 'answer_')]")

    question = _parse_question(area_question, slug_args_base)
    answer_list = [
        _parse_answers(area, slug_args_base) for area in areas_answer
    ]
    answer_list.insert(0, question)
    return answer_list



def compose_comment_requests(response, url_comment_base, questioncontent_list, count_per_page, max_page_count):
    qs = furl(response.url).args
    def _calc_last_page(total_count, count_per_page=count_per_page, page_limit=max_page_count):
        page = math.ceil(total_count/count_per_page)
        return min(page, page_limit)
    
    for qc in questioncontent_list:
        last_page_number = _calc_last_page(qc['comment_count'])

        for n in range(1, last_page_number+1):
            query = {
                'answerNo': qc['answer_no'],
                'page': n,
                'dirId': qs['dirId'],
                'docId': qs['docId']
            }
            cf = furl(url_comment_base)
            cf.args = query
            yield cf.url

    quries = [
         dict(
             answerNo=qc.get('answer_no'),
             page=n,
             dirId=qs.get('dirId'),
             docId=qs.get('docId')
         ) 
         for qc in  questioncontent_list 
         for n in range(1, _calc_last_page(qc['comment_count']))
    ]
    urls = [
        add_or_replace_parameters(url_comment_base, q) for q in quries
    ]
    return urls


