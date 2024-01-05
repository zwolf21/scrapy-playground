import sys, importlib, inspect, itertools

from scrapgo.lib import module2dict
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings

if __name__ == '__main__':
    settings = get_project_settings()
    settings_module = importlib.import_module('myreplica.settings')
    settings.update(dict(itertools.takewhile(lambda i: i[0] != '__builtins__', inspect.getmembers(settings_module))))
    
    execute(['myreplica', 'runspider', 'myreplica/myreplica/spiders/replica.py', '-o', 'replica.jsonl'], settings=settings)


