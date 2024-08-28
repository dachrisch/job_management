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

    _sites: list[JobSite] = []
    _jobs: list[JobOffer] = []
    sort_value: str = 'title'
    sort_reverse: bool = False

    deleting: bool = False

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

    def add_site_to_db(self, form_data: dict):
        site = TargetWebsiteDto.from_dict(form_data)
        self.db.sites.add(site)
        self.load_sites()
        if form_data['crawling']:
            print('run')
            return SitesState.start_crawl(site.to_dict())

    @rx.background
    async def delete_site(self, site_dict: dict):
        async with self:
            self.deleting = True
        for site in self.db.sites.filter({'url': {'$eq': site_dict['url']}}):
            self.info(f'Deleting {site}')
            self.db.sites.delete(site)
        delete_many_result = self.db.jobs.collection.delete_many({'site_url': {'$eq': site_dict['url']}})
        async with self:
            self.load_sites()
        async with self:
            self.deleting = False
        return rx.toast.success(f'Deleted [{site_dict["title"]}] and [{delete_many_result.deleted_count}] jobs')

    @rx.background
    async def start_crawl(self, site_dict: dict[str, Any]):
        site = self._find_site(site_dict)

        self.info(f'Starting crawler for [{site}]')

        async with self:
            site.crawling = True

        crawler = CrochetCrawlerRunner(JobsFromUrlSpider, site.url)
        stats = crawler.crawl().wait(timeout=60)

        async with self:
            site.crawling = False
            self.load_sites()
        return self.fire_stats_toast(site.url, stats)

    def _find_site(self, site_dict: dict[str, Any]) -> JobSite | None:
        site: JobSite | None = None
        for s in self._sites:
            if s.url == site_dict['url']:
                site = s
                break
        return site

    def fire_stats_toast(self, site_url: str, stats: dict[str, Any]):
        if stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{stats.get("item_scraped_count", 0)}] '
                f'items in {stats["elapsed_time_seconds"]} seconds from [{site_url}]')
        else:
            return rx.toast.error(f'Crawling failed: {stats}')

    def load_job_site(self, s: TargetWebsiteDto):
        site_dict = s.to_dict()
        site_dict['num_jobs'] = len([job for job in self._jobs if job.site_url == s.url])
        return JobSite(**site_dict)


class JobsState(rx.State):
    num_jobs: int = 0
    num_jobs_yesterday: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.info = logging.getLogger(self.__class__.__name__).info

    def load_jobs(self):
        self.info('Loading Jobs')
        jobs = list(self.db.jobs.all())
        self.num_jobs = len(jobs)
        self.num_jobs_yesterday = len(
            [job for job in jobs if job.added.date() < (datetime.now().date() - timedelta(days=1))])
        self.info(f'Loaded [{self.num_jobs}] Jobs')


class JobState(rx.State):
    num_jobs: int = 0
    jobs: list[JobOffer] = []
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_jobs(self):
        site_url = self.router.page.params.get('site')
        self.jobs = list(map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.filter({'site_url': {'$eq': site_url}})))
        self.num_jobs = len(self.jobs)

    def update_current_site(self):
        site_url = self.router.page.params.get('site', None)
        if site_url:
            sites = map(lambda s: JobSite(**s.to_dict()), self.db.sites.filter({'url': {'$eq': site_url}}))
            self.current_site = next(sites)

