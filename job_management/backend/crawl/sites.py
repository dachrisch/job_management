import reflex as rx

from job_offer_spider.spider.arbeitsamt import ArbeitsamtSpider
from job_offer_spider.spider.eustartups import EuStartupsSpider
from . import StatsCrawler
from .crawler import CrochetCrawlerRunner
from ..state.sites import SitesState


class EuStartupSitesCrawlerState(rx.State, StatsCrawler):
    running: bool = False

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
        crawler = CrochetCrawlerRunner(EuStartupsSpider)
        stats = crawler.crawl().wait(timeout=600)
        async with self:
            (await self.get_state(SitesState)).load_sites()
            self.running = False
            print(f'Stats: {stats}')
        return self.fire_stats_toast(stats)


class ArbeitsamtSitesCrawlerState(rx.State, StatsCrawler):
    running: bool = False

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
        crawler = CrochetCrawlerRunner(ArbeitsamtSpider)
        stats = crawler.crawl().wait(timeout=600)
        async with self:
            (await self.get_state(SitesState)).load_sites()
            self.running = False
            print(f'Stats: {stats}')
        return self.fire_stats_toast(stats)
