import logging
from datetime import datetime, timedelta
from typing import Any

import reflex as rx

from job_management.backend.crawl import CrochetCrawlerRunner
from job_management.backend.entity import JobSite, JobOffer
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.target_website import TargetWebsiteDto
from job_offer_spider.spider.findjobs import JobsFromUrlSpider


class SitesState(rx.State):
    num_sites: int = 0
    num_sites_yesterday: int = 0
    current_site: JobSite = JobSite()

    _sites: list[JobSite] = []
    _jobs: list[JobOffer] = []
    sort_value: str = 'title'
    sort_reverse: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.info = logging.getLogger(self.__class__.__name__).info
        self.debug = logging.getLogger(self.__class__.__name__).debug

    def load_sites(self):
        self.info('Loading sites...')
        self._sites = list(map(self.load_job_site, self.db.sites.all()))
        self._jobs = list(map(lambda j: JobOffer(**j.to_dict()), self.db.jobs.all()))
        self.num_sites = len(self._sites)
        self.info(f'Loaded [{self.num_sites}] sites...')
        self.num_sites_yesterday = len(
            [site for site in self._sites if site.added.date() < (datetime.now().date() - timedelta(days=1))])

    @rx.var(cache=True)
    def sites(self) -> list[JobSite]:
        sites = self._sites
        if self.sort_value:
            sites = sorted(
                self._sites,
                key=lambda s: getattr(s, self.sort_value.lower()),
                reverse=self.sort_reverse
            )
        return sites

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse

    @rx.background
    async def start_crawl(self, site_dict: dict[str, Any]):
        site: JobSite | None = None
        for s in self._sites:
            if s.url == site_dict['url']:
                site = s
                break

        self.info(f'Starting crawler for [{site}]')

        async with self:
            site.crawling = True

        crawler = CrochetCrawlerRunner(JobsFromUrlSpider, site.url)
        stats = crawler.crawl().wait(timeout=60)

        async with self:
            site.crawling = False
            self.load_sites()
        return self.fire_stats_toast(site.url, stats)

    def fire_stats_toast(self, site_url: str, stats: dict[str, Any]):
        if stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{stats.get("item_scraped_count", 0)}] '
                f'items in {stats["elapsed_time_seconds"]} seconds from [{site_url}]')
        else:
            return rx.toast.error(f'Crawling failed: {stats}')

    def update_current_site(self):
        site_url = self.router.page.params.get('site', None)
        if site_url:
            site = next(filter(lambda s: s.url == site_url, self._sites))
            self.current_site = site

    def load_job_site(self, s: TargetWebsiteDto):
        self.debug(f'Loading Job Site [{s}]')
        site_dict = s.to_dict()
        site_dict['num_jobs'] = len([job for job in self._jobs if job.site_url == s.url])
        return JobSite(**site_dict)


class JobsState(rx.State):
    num_jobs: int = 0
    num_jobs_yesterday: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_jobs(self):
        jobs = list(self.db.jobs.all())
        self.num_jobs = len(jobs)
        self.num_jobs_yesterday = len(
            [job for job in jobs if job.added.date() < (datetime.now().date() - timedelta(days=1))])


class JobState(rx.State):
    num_jobs: int = 0
    jobs: list[JobOffer] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_jobs(self):
        site_url = self.router.page.params.get('site')
        self.jobs = list(map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.filter({'site_url': {'$eq': site_url}})))
        self.num_jobs = len(self.jobs)
