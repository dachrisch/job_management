import asyncio
from typing import Any

import reflex as rx
from scrapy.statscollectors import StatsCollector

from job_management.backend.crawl import CrochetCrawlerRunner
from job_management.backend.entity import JobSite, JobOffer
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.target_website import TargetWebsiteDto
from job_offer_spider.spider.findjobs import  JobFromUrlSpider


class SiteState(rx.State):
    num_sites: int = 0
    current_site: JobSite = JobSite()

    running: dict[str, bool] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.crawler = CrochetCrawlerRunner(JobFromUrlSpider)

    def load_sites(self):
        # noinspection PyTypeChecker
        self.num_sites = len(self.sites)
        # noinspection PyTypeChecker
        self.running = {site.url: False for site in self.sites}

    @rx.background
    async def set_running(self, site_url_and_state: tuple[str, bool]):
        site_url, _ = site_url_and_state
        async with self:
            self.running[site_url] = True
            print(self.running)

        stats = self.crawler.crawl(site_url).wait(timeout=60)

        async with self:
            self.running[site_url] = False
            print(self.running)
        return self.fire_stats_toast(site_url, stats)

    def fire_stats_toast(self, site_url:str, stats: dict[str,Any]):
        if stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{stats.get("item_scraped_count", 0)}] '
                f'items in {stats["elapsed_time_seconds"]} seconds from [{site_url}]')
        else:
            return rx.toast.error(f'Crawling failed: {stats}')


    def site_from_url(self, site_url:str):
        print(site_url)
        return list(filter(lambda s:s.url==site_url, self.sites))[0]

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
