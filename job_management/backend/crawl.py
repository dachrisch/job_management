from functools import partial
from typing import Any, Type

import crochet
import reflex as rx
from scrapy import Spider
from scrapy.crawler import CrawlerRunner
from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import get_project_settings

from job_offer_spider.spider.eustartups import EuStartupsSpider
from job_offer_spider.spider.findjobs import JobsFromDbSpider


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


class StatsCrawler:
    def fire_stats_toast(self, stats: dict[str, Any]):
        if stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{stats["item_scraped_count"]}] '
                f'items in {stats["elapsed_time_seconds"]} seconds')
        else:
            return rx.toast.error(f'Crawling failed: {stats}')


class SitesCrawlerState(rx.State, StatsCrawler):
    running: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
        crawler = CrochetCrawlerRunner(EuStartupsSpider)
        stats = crawler.crawl().wait(timeout=600)
        async with self:
            self.running = False
            print(f'Stats: {stats}')
        return self.fire_stats_toast(stats)


class JobsCrawlerState(rx.State):
    running: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
        crawler = CrochetCrawlerRunner(JobsFromDbSpider)
        stats = crawler.crawl().wait(timeout=600)
        async with self:
            self.running = False
            print(f'Stats: {stats}')
        return self.fire_stats_toast(stats)
