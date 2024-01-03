from naverkin.items import ImageItem


def parse(response):
    return ImageItem(
        src=response.url,
        img=response.body
    )