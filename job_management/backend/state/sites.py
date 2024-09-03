import logging
from datetime import datetime, timedelta
from typing import Any

import reflex as rx
from montydb import ASCENDING, DESCENDING

from job_management.backend.crawl import CrochetCrawlerRunner
from job_management.backend.entity import JobSite, JobOffer
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.spider.findjobs import JobsFromUrlSpider


class SitesState(rx.State):
    num_sites: int = 0
    num_sites_yesterday: int = 0

    _sites: list[JobSite] = []
    _jobs: list[JobOffer] = []
    sort_value: str = 'title'
    sort_reverse: bool = False

    page: int = 0
    page_size: int = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.info = logging.getLogger(self.__class__.__name__).info
        self.debug = logging.getLogger(self.__class__.__name__).debug

    def load_sites(self):
        self.info('Loading sites...')
        self._sites = list(
            map(self.load_job_site, self.db.sites.all(skip=self.page * self.page_size, limit=self.page_size,
                                                      sort_key=self.sort_value.lower(),
                                                      direction=DESCENDING if self.sort_reverse else ASCENDING)))
        self._jobs = list(map(lambda j: JobOffer(**j.to_dict()), self.db.jobs.all()))
        self.num_sites = self.db.sites.count({})
        self.num_sites_yesterday = self.db.sites.count(
            {'added': {'$lt': (datetime.now() - timedelta(days=1)).timestamp()}})
        self.info(f'Loaded [{len(self._sites)}] sites for page [{self.page + 1} of {self.total_pages}]...')

    @rx.var(cache=False)
    def sites(self) -> list[JobSite]:
        return self._sites

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_sites()

    def change_sort_value(self, new_value: str):
        self.sort_value = new_value
        self.load_sites()

    def add_site_to_db(self, form_data: dict):
        site = JobSiteDto.from_dict(form_data)
        self.db.sites.add(site)
        self.load_sites()
        if form_data.get('crawling'):
            return SitesState.start_crawl(site.to_dict())

    @rx.background
    async def delete_site(self, site_dict: dict):
        site = self._find_site(site_dict)
        async with self:
            site.deleting = True
        for site in self.db.sites.filter({'url': {'$eq': site_dict['url']}}):
            self.info(f'Deleting {site}')
            self.db.sites.delete(site)
        delete_many_result = self.db.jobs.collection.delete_many({'site_url': {'$eq': site_dict['url']}})
        async with self:
            self.load_sites()
        async with self:
            site.deleting = False
        return rx.toast.success(f'Deleted [{site_dict["title"]}] and [{delete_many_result.deleted_count}] jobs')

    @rx.background
    async def start_crawl(self, site_dict: dict[str, Any]):
        site = self._find_site(site_dict)

        self.info(f'Starting crawler for [{site}]')

        async with self:
            if site:
                site.crawling = True

        crawler = CrochetCrawlerRunner(JobsFromUrlSpider, site.url)
        stats = crawler.crawl().wait(timeout=600)

        async with self:
            if site:
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

    def load_job_site(self, s: JobSiteDto):
        return JobSite(**(s.to_dict()))

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return self.num_sites // self.page_size + (
            1 if self.num_sites % self.page_size else 0
        )

    @rx.var(cache=True)
    def at_beginning(self) -> bool:
        return self.page * self.page_size - self.page_size < 0

    @rx.var(cache=True)
    def at_end(self) -> bool:
        return self.page * self.page_size + self.page_size > self.num_sites

    def first_page(self):
        self.page = 0
        self.load_sites()

    def prev_page(self):
        if not self.at_beginning:
            self.page -= 1
        self.load_sites()

    def last_page(self):
        self.page = self.num_sites // self.page_size
        self.load_sites()

    def next_page(self):
        if not self.at_end:
            self.page += 1
        self.load_sites()
