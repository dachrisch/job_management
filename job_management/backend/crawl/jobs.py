import reflex as rx

from backend.crawl.crawler import CrochetCrawlerRunner
from spider.findjobs import JobsFromDbSpider


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
