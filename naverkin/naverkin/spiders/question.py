import scrapy, furl
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..utils import parse_page_range_expression
from .parsers import questioninfo, questioncontent, comment, image


DEFAULT_PAGE_RANGE = '1-100'
MAX_COMMENT_PAGE_COUNT = 100
COMMENT_COUNT_PER_PAGE = 100






class QuestionSpider(CrawlSpider):
    name = 'naverkin'
    root = 'https://kin.naver.com/search/list.naver'
    base_comment_url = 'https://kin.naver.com/ajax/detail/commentListAjax.nhn'

    rules = [
        Rule(
            LinkExtractor(r'^https://kin.naver.com/qna/detail.naver\?d1id=(?P<d1id>\d+).+$'),
            callback='parse_question', follow=True
        ),
        # Rule(
        #     LinkExtractor(
        #         r'^https://kin-phinf.pstatic.net/.+$', tags=('span', ), attrs=('data-image-src',),
        #         deny_extensions=[] # jpg와 같은 이미지를 받기 위해한 필터 해제 
        #     ),
        #     callback='parse_image', follow=True
        # )
    ]

    def __init__(self, keyword, period=None, page=None, **kwargs):
        '''period: 검색 기한 범위 ex) 1m(1달) 1y(1년) 2020.01.01|2020.01.02....
        '''
        super().__init__(keyword, **kwargs)
        self.keyword = keyword
        self.period = period
        self.page_range = parse_page_range_expression(page or DEFAULT_PAGE_RANGE)


    def start_requests(self):
        def _gen_request(page):
            u = furl.furl(self.root)
            u.args = dict(query=self.keyword, page=page)
            if prd := self.period: u.args.update(dict(period=prd))
            return u.url            

        return map(scrapy.Request, map(_gen_request, self.page_range))

    def parse_question(self, response):
        question_info = questioninfo.parse(response, self.keyword)
        question_content_list = questioncontent.parse_list(response)

        
        yield question_info

        for item in question_content_list:
            yield item

        comment_urls = questioncontent.compose_comment_requests(
            response, self.base_comment_url, question_content_list,
            COMMENT_COUNT_PER_PAGE, MAX_COMMENT_PAGE_COUNT
        )
        for url in comment_urls:
            yield response.follow(url, self.parse_comment)
        

    def parse_comment(self, response):
        yield from comment.parse_list(response)
            
    # def parse_image(self, response):
    #     yield image.parse(response)
            
            