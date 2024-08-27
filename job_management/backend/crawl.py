import asyncio
from functools import partial
from typing import Any, Type

import crochet
import reflex as rx
from scrapy import Spider
from scrapy.crawler import CrawlerRunner
from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import get_project_settings

from job_offer_spider.spider.eustartups import EuStartupsSpider
from job_offer_spider.spider.findjobs import JobFromDbSpider


class CrochetCrawlerRunner:
    def __init__(self, spider_class: Type[Spider]):
        self.spider_class = spider_class
        self.crawler = CrawlerRunner(get_project_settings())
        self.crawler.settings.set('SPIDER_DAYS_OFFSET', 0)

    @crochet.run_in_reactor
    def crawl(self, site_url:str):
        d = self.crawler.crawl(self.spider_class, site_url)
        stats = set(self.crawler.crawlers).pop().stats
        d.addCallback(partial(self.finished, stats))
        return d

    def finished(self, stats: StatsCollector, what) -> dict[str, Any]:
        return stats.get_stats()


class CrawlerStatsState(rx.State):
    running: bool = False
    last_run_stats: dict[str, Any] = {}

    def fire_stats_toast(self):
        if self.last_run_stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{self.last_run_stats["item_scraped_count"]}] '
                f'items in {self.last_run_stats["elapsed_time_seconds"]} seconds')
        else:
            return rx.toast.error(f'Crawling failed: {self.last_run_stats}')

class JobsCrawlerState(rx.State):
    def check(self, value):
        print(value)

    def is_running(self, site):
        print(f'Running: {site}')
        return False

class JobsCrawlerButton(rx.ComponentState):
    running: bool = False
    last_run_stats: dict[str, Any] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawler = CrochetCrawlerRunner(JobFromDbSpider)

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
        stats = self.crawler.crawl().wait(timeout=60)
        async with self:
            self.running = False
            print(f'Stats: {stats}')
            self.last_run_stats = stats
        return self.fire_stats_toast()

    def fire_stats_toast(self):
        if self.last_run_stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{self.last_run_stats["item_scraped_count"]}] '
                f'items in {self.last_run_stats["elapsed_time_seconds"]} seconds')
        else:
            return rx.toast.error(f'Crawling failed: {self.last_run_stats}')

    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        site_url = props.get('site_url')
        return rx.button(
            rx.icon("play", size=22),
            title=site_url,
            loading=cls.running,
            on_click=cls.start_crawling,
            size="2",
            variant="solid",
            **props
        )


class SitesCrawlerState(CrawlerStatsState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawler = CrochetCrawlerRunner(EuStartupsSpider)

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
        stats = self.crawler.crawl().wait(timeout=60)
        async with self:
            self.running = False
            print(f'Stats: {stats}')
            self.last_run_stats = stats
        return self.fire_stats_toast()

