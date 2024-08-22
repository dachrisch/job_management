import fire
from rich import box
from rich.console import Console
from rich.table import Table
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import asyncioreactor
from twisted.internet import defer

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.spiders.eustartups import EuStartupsSpider
from job_offer_spider.spiders.findjobs import FindjobsSpider


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
                table.add_row(job['title'], job['url'])
            self._l(table)


class CrawlCli:
    def __init__(self):
        settings = get_project_settings()
        configure_logging(settings)
        self._runner = CrawlerRunner(settings)
        console = Console()
        self._spinner = console.status
        self._l = console.print
        self._db = JobOfferDb()

    def scan(self):
        asyncioreactor.install()
        from twisted.internet import reactor
        @defer.inlineCallbacks
        def crawl():
            with self._spinner('Crawling sites...'):
                yield self._runner.crawl(EuStartupsSpider)
                self._l(f'Found {self._db.sites.size} websites')
            with self._spinner('Finding job offers...'):
                yield self._runner.crawl(FindjobsSpider)
                self._l(f'Found {self._db.jobs.size} jobs')
            # noinspection PyUnresolvedReferences
            reactor.stop()

        crawl()
        # noinspection PyUnresolvedReferences
        reactor.run()


class JobOfferCli:
    def __init__(self):
        self.jobs = JobsDbCli()
        self.crawl = CrawlCli()


if __name__ == '__main__':
    fire.Fire(JobOfferCli)
