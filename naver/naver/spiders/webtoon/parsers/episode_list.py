def parse_episode_list(response):
    yield dict(response.qs)
