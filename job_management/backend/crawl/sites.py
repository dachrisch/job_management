import reflex as rx

from backend.crawl import StatsCrawler
from backend.crawl.crawler import CrochetCrawlerRunner
from backend.state.sites import SitesState
from spider.arbeitsamt import ArbeitsamtSpider
from spider.eustartups import EuStartupsSpider


class EuStartupSitesCrawlerState(rx.State, StatsCrawler):
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
            (await self.get_state(SitesState)).load_sites()
            self.running = False
            print(f'Stats: {stats}')
        return self.fire_stats_toast(stats)

class ArbeitsamtSitesCrawlerState(rx.State, StatsCrawler):
    running: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
