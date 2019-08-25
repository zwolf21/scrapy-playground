def parse_episode(response):
    yield dict(response.qs)
