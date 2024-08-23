import time
from datetime import datetime, timedelta
from json import JSONDecodeError
from threading import Thread

import fire
from rich import box
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.spider.eustartups import EuStartupsSpider
from job_offer_spider.spider.findjobs import FindJobsSpider


class SitesScannedProgressThread(Thread):
    def __init__(self, days_offset:int):
        super().__init__()
        self.days_offset = days_offset
        console = Console()
        self._l = console.print

    def run(self):
        now = datetime.now()
        timestamp_threshold = (now - timedelta(days=self.days_offset)).timestamp()
        sites_to_scan = JobOfferDb().sites.count(
            {'$or': [{'last_scanned': {'$eq': None}}, {'last_scanned': {'$lt': timestamp_threshold}}]})
        with Progress() as p:
            task = p.add_task(f'Crawling [{sites_to_scan}] sites for job offers', total=sites_to_scan)
            while not p.finished:
                completed = JobOfferDb().sites.count({'last_scanned': {'$gt': now.timestamp()}})
                p.update(task, completed=completed)
                time.sleep(1)

        self._l(f'Found {JobOfferDb().jobs.size} jobs')


class JobsDbCli:
    def __init__(self):
        self._db = JobOfferDb()
        console = Console()
        self._l = console.print
        self._spinner = console.status

    def print(self):
        table = Table(title='Job Offers', show_edge=False, highlight=True, box=box.HORIZONTALS)
        table.add_column('Title', style='yellow')
        table.add_column('Link', style='bright_blue')
        with self._spinner('retrieving jobs'):
            for job in self._db.jobs.all():
                table.add_row(job.title, job.url)
            self._l(table)


class CrawlCli:
    def __init__(self):
        console = Console()
        self._spinner = console.status
        self._l = console.print
        self._db = JobOfferDb()

    def all(self):
        self.sites(False)
        self.jobs()

    def sites(self, stop=True):
        with self._spinner(f'Crawling sites from {EuStartupsSpider.sitemap_urls}...'):
            process = CrawlerProcess(get_project_settings())
            process.crawl(EuStartupsSpider)
            process.start(stop_after_crawl=stop)
        self._l(f'Found {self._db.sites.size} websites')

    def jobs(self, days_offset:int=7):
        pt = SitesScannedProgressThread(days_offset)
        process = CrawlerProcess(get_project_settings())
        process.settings.set('SPIDER_DAYS_OFFSET', days_offset)
        process.crawl(FindJobsSpider)
        pt.start()
        process.start()
        pt.join(timeout=1)


class JobOfferCli:
    def __init__(self):
        self.jobs = JobsDbCli()
        self.crawl = CrawlCli()


if __name__ == '__main__':
    fire.Fire(JobOfferCli)
