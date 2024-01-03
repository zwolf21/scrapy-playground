from scrapy.crawler import CrawlerProcess
from naverkin.spiders.question import QuestionSpider

import argparse

from naverkin.process import  start_naverkin



def main():
    argparser = argparse.ArgumentParser(
         formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='NaverKin Crawler Test'
     )

    argparser.add_argument('keyword', nargs='*')
    argparser.add_argument('-page', '--page', nargs='?', type=str)

    args = argparser.parse_args()

    if keywords := args.keyword:
        keyword = ' '.join(keywords)
        start_naverkin(keyword, args.page)












if __name__ == "__main__":
    main()


