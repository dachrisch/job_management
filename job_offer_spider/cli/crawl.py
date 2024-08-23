from rich.console import Console
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from job_offer_spider.cli.progress import SitesScannedProgressThread
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.spider.eustartups import EuStartupsSpider
from job_offer_spider.spider.findjobs import FindJobsSpider


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

    def jobs(self, days_offset: int = 7):
        pt = SitesScannedProgressThread(days_offset)
        process = CrawlerProcess(get_project_settings())
        process.settings.set('SPIDER_DAYS_OFFSET', days_offset)
        process.crawl(FindJobsSpider)
        pt.start()
        process.start()
        pt.join(timeout=1)


