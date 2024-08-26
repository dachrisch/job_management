import sys
from datetime import datetime

import crochet
import reflex as rx
from scrapy import signals
from scrapy.crawler import  CrawlerRunner
from scrapy.utils.project import get_project_settings

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.target_website import TargetWebsiteDto
from job_offer_spider.spider.findjobs import FindJobsSpider


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    num_jobs: int = 0
    last_scanned: datetime = None


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''


class JobsCrawlerState(rx.State):
    running: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawler = CrawlerRunner(get_project_settings())
        self.crawler.settings.set('SPIDER_DAYS_OFFSET', 0)

    @rx.background
    async def start_crawling(self):
        async with self:
            self.running = True
            print('Running crawler')
        self.crawl().wait(timeout=60)
        async with self:
            self.running = False
            print('Finished crawler')

    @crochet.run_in_reactor
    def crawl(self):
        d = self.crawler.crawl(FindJobsSpider)
        d.addCallback(self.finished)
        return d

    def finished(self, what):
        print(f'Finished crawler: {what}')

class SiteState(rx.State):
    num_sites: int = 0
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_sites(self):
        # noinspection PyTypeChecker
        self.num_sites = len(self.sites)

    @rx.var(cache=False)
    def sites(self) -> list[JobSite]:
        return list(map(self.load_job_site, self.db.sites.all()))

    def update_current_site(self):
        site_url = self.router.page.params.get('site', None)
        if site_url:
            # noinspection PyTypeChecker
            site = next(filter(lambda s: s.url == site_url, self.sites))
            self.current_site = site

    def load_job_site(self, s: TargetWebsiteDto):
        site_dict = s.to_dict()
        site_dict['num_jobs'] = self.db.jobs.count({'site_url': {'$eq': s.url}})
        return JobSite(**site_dict)


class JobsState(rx.State):
    num_jobs: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.site_url = self.router.page.params.get('site')

    def load_jobs(self):
        # noinspection PyTypeChecker
        self.num_jobs = len(self.jobs)

    @rx.var()
    def jobs(self) -> list[JobOffer]:
        site_url = self.router.page.params.get('site')
        return list(map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.filter({'site_url': {'$eq': site_url}})))
