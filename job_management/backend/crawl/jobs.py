import reflex as rx

from job_offer_spider.spider.findjobs import JobsFromDbSpider
from .crawler import CrochetCrawlerRunner


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
