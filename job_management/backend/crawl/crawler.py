from functools import partial
from typing import Any, Type

import crochet
from scrapy import Spider
from scrapy.crawler import CrawlerRunner
from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import get_project_settings


class CrochetCrawlerRunner:
    def __init__(self, spider_class: Type[Spider], *crawler_args):
        self.spider_class = spider_class
        self.crawler = CrawlerRunner(get_project_settings())
        self.crawler.settings.set('SPIDER_DAYS_OFFSET', 0)
        self.crawler_args = crawler_args

    @crochet.run_in_reactor
    def crawl(self):
        d = self.crawler.crawl(self.spider_class, *self.crawler_args)
        stats = set(self.crawler.crawlers).pop().stats
        d.addCallback(partial(self.finished, stats))
        return d

    def finished(self, stats: StatsCollector, what) -> dict[str, Any]:
        return stats.get_stats()


