# Emart Scrap

---

> ## Useage

1. basic crawling
   ```bash
   # running at path /emart
   scrapy crawl category
   ```
1. category options

- -o : output to file
  ```bash
  scrapy crawl category -o emart_items.csv
  ```
- -a: category scoping
  - 카테고리의 텍스트에 정규 표현식을 적용하여 사이트의 크롤링 범위를 제한한다.
  - 상위 카테고리 부터 점차 좁은 카테고리를 지정하는 방식으로 사용하여야 의미가 있다.
  - large_category
  - medium_category
  - small_category
  - xmall_category
  ```bash
  scrapy crawl category -a large_category="라면|과자" -a medium_category="스낵" -a small_category="옥수수" -a xmall_category="쌀과자" -o emart_items.csv
  ```
