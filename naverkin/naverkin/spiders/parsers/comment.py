from furl import furl

from naverkin.utils import prettify_content
from naverkin.items import CommentItem
from .shortcuts import gen_slug





def parse_list(response):
    previous_url  = response.request.headers.get('Referer', None)
    preqs = furl(previous_url).args
    slug_args_base = [preqs[k] for k in ['d1id', 'dirId', 'docId']]
    res = response.json()
    qs = furl(response.url).args
    if data := res.get('result'):
        for comment in data['commentList']:
            pub_date_time = comment.get("writeTime")
            pub_date_time = pub_date_time.replace('.', '-', 2).replace('.', '')
            slug_args = slug_args_base + [qs['answerNo'], comment['commentNo']]
            comment_item = CommentItem(
                slug = gen_slug(*slug_args),
                author_uid=comment.get('u'),
                author_name=comment.get('viewId'),
                content=comment['contents'],
                published=pub_date_time,
            )
            yield comment_item
