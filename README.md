# Scrapy PlayGround

---

> ## 스크래피 how to

1. genspider 명령시 자주 사용하는 옵션

   - -t crawl: 재귀적 탐색을 하는 스파이더의 템플릿을 생성해준다.
     ```bash
     scrapy genspider -t crawl webtoon comic.naver.com/webtoon/weekday.nhn
     ```

1. crawl 명령시 자주 사용하는 옵션

   - -a key=value: 명령행 인자를 스파이더 생성자 변수로 넘겨줄 수 있다
   - 스파이더의 크롤링을 제어하는데 유용함

     ```bash
     scrapy crawl webtoon -a search=외모지상* -a episode=1-100
     ```

     ```python
     class WebtoonSpider(scrapy.Spider):
          name = 'webtoon'
          start_urls = ['https://comic.naver.com/webtoon/weekday.nhn']

          def __init__(self, search=None, **kwargs):
               super().__init__(**kwargs)
               self.search = search

          def parse(self, response):
               if self.seach in response.url:
                    pass
     ```

1) Cache 정책설정
   - settings.py 에서 On/Off
     ```python
     # settings.py
     HTTPCACHE_ENABLED = True
     ```
1) Post로 요청 하는 방법

   - login form Post 후 해당 로그인 계정의 session 을 유지 한채로 크롤링 하는법?

1) Request Header 에 User-agent 지정 하기

   - ex) 특정 사이트의 경우 특정 브라우저 Agent 이외에 접근은 허용 안함

1) Loging : Level 별로 로그 출력 다이렉션 하는 방법
   - Warning 이상은 txt파일로?
   - Debug 는 화면으로?

---

> ## 스크래피 self.QnA | self.Ans

1. spider 의 parser 메소드에서 링크를 재귀적으로 호출시 Request Header override 하는 방법?

1. 재귀적 link 요청시 url 중복 Request 발생시 정책?

   - skipp or allow?

1. 스크래핑 도중 요청 실패시 정책?

   - Retry after 10, 100, 1000 second?
     - 너무 자주, 빠르게 요청을 하다보면 서버에서 일정시간 블록 당할경우 발생
     - 일정시간이후 재 요청 기능구현은 어떻게?
   - 요청 Delay를 스파이더별, 전역적으로 지정하는 방법이 있는지?

1. 스크래피 모듈을 다른 파이썬 App에서 임포트 하는 형식으로 사용하는 방법?

   - 장고, Celery 에서 크롤링을 스케쥴 할시 task형식으로 spider를 실행 해야할 필요성
   - 아니면 환경 변수 지정후 subprocess open 함수로 scrapy crawl gmarket 을 그냥 실행 하는 형식으로 스크래피에 접근하는게 나을까?

1. Item과 spider N:N 인데 pipeline은 하나인데 여러 pipeline 을 사용하는 방법?
   - spider 별로 pipeline 구분
     ```python
     # ecommerce/pipelines.py
     class EcommercePipeline(object):
         def process_item(self, item, spider):
             # spider 변수를 받으므로 spider 별로 처리 가능할듯
             if spider.name == 'gmarket':
                 pass
             return item
     ```

---

> ## 스크래피 Cook, Trouble shot

1. pagination crawling techique

   - page number 범위를 지정하는 방법
     1. 게시판을 크롤링 하기전에 총 몇페이지 까지 있는걸 탐색하는 scout_parser 필요성?
     1. 게시판의 맨뒤 페이지(첫 글) 부터 긁어 와야하는경우
   - pagination 중 중단 하는 방법
     1. 게시판의 첫 페이지부터 크롤링을 시작하여 특정 경우가 되면 크롤링을 중지
        - ex) DB에 존재하는 데이터가 크롤 되면 크롤링을 중지

1. 재귀적 link 탐색시 상대경로를 우아하게 사용하는 방법들

   - 지양해야할 방법
     - domain 문자열을 + 연산으로 합쳐서 절대 경로를 만드는법(최악)
     - urljoin 으로 domain 을 join 하여 절대경로를 만드는법(차선)
   - 추천하는 방법

     1. response 객체의 follow 객체를 이용하여 callback
        - 상대 경로로 추출된 링크를 넘겨도 알아서 작동
        - 주의사항: yield response.follow 이후의 코드는 실행되지 않는듯
     1. LinkExtractor 모듈 이용
        - 애초에 절대 경로 링크가 추출됨
        - 링크를 가진 테그의 속성 정보들까지 추출 가능 - text, fragmets..

     ```python
     # spiders/gmarket.py
     import scrapy
     from scrapy.linkextractors import LinkExtractor

     class GmarketSpider(scrapy.Spider):

        def parser(self, response):
            # 다음과 같은 패턴을 가지고 있는 링크를 모두 추출한다.
            link_extractor = LinkExtractor(
                r'/Bestsellers\?viewType=(?P<viewType>.+)&groupCode=(?P<groupCode>.+)'
            )
            for lnk in link_extractor.extract_links(response):
                link = lnk.url
                label = lnk.text # 링크를 포함하는 태그의 text element 까지 추출할 수 있음
                yield scrapy.Request(link, self.next_parser...)
                # or
                yield response.follow(link, self.next_parser...) # link 가 상대 경로라도 작동
     ```
