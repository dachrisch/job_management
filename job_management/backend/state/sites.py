import logging
from typing import Any

import reflex as rx
from more_itertools import first

from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.spider.findjobs import JobsFromUrlSpider
from .pagination import PaginationState
from .statistics import JobsStatisticsState
from ..crawl.crawler import CrochetCrawlerRunner
from ..entity.site import JobSite
from ..service.locator import Locator


class SitesPaginationState(rx.State, PaginationState):
    total_items: int = 0
    page: int = 0
    page_size: int = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return self.total_items // self.page_size + (
            1 if self.total_items % self.page_size else 0
        )

    @rx.var(cache=True)
    def at_beginning(self) -> bool:
        return self.page * self.page_size - self.page_size < 0

    @rx.var(cache=True)
    def at_end(self) -> bool:
        return self.page * self.page_size + self.page_size > self.total_items

    async def first_page(self):
        self.page = 0
        await self.refresh()

    async def prev_page(self):
        if not self.at_beginning:
            self.page -= 1
        await self.refresh()

    async def last_page(self):
        self.page = self.total_items // self.page_size
        await self.refresh()

    async def next_page(self):
        if not self.at_end:
            self.page += 1
        await self.refresh()

    async def refresh(self):
        await (await self.get_state(SitesState)).load_sites()


class SitesState(rx.State):
    num_sites_yesterday: int = 0

    _sites: list[JobSite] = []
    sort_value: str = first(JobSite.sortable_fields())[0]
    sort_reverse: bool = False

    @property
    def log(self) -> logging.Logger:
        return logging.getLogger(__name__)

    async def load_sites(self):
        paging_state = (await self.get_state(SitesPaginationState))

        self.log.info(f'Loading sites for page [{paging_state.page + 1}]...')
        self._sites = Locator.job_sites_service.load_sites(paging_state.page, paging_state.page_size, self.sort_value,
                                                           self.sort_reverse)
        paging_state.total_items = Locator.job_sites_service.count_sites()
        self.num_sites_yesterday = Locator.job_sites_service.count_sites(days_from_now=1)
        (await self.get_state(JobsStatisticsState)).load_jobs_statistic()
        self.log.info(
            f'Loaded [{len(self._sites)}] sites for page [{paging_state.page + 1} of {paging_state.total_pages}]...')

    @rx.var(cache=False)
    def sites(self) -> list[JobSite]:
        return self._sites

    async def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        await self.load_sites()

    async def change_sort_value(self, new_value: str):
        self.sort_value = new_value
        await self.load_sites()

    async def add_site_to_db(self, form_data: dict):
        site = JobSiteDto.from_dict(form_data)
        Locator.job_sites_service.add_site(site)
        await self.load_sites()
        if form_data.get('crawling'):
            return SitesState.start_crawl(site.to_dict())

    @rx.background
    async def delete_site(self, site_dict: dict):
        site = self._find_site(site_dict)
        async with self:
            site.status.deleting = True

        Locator.jobs_sites_with_jobs_service.delete(site)

        async with self:
            site.status.deleting = False
            await self.load_sites()
        return rx.toast.success(f'Deleted [{site_dict["title"]}]')

    @rx.background
    async def start_crawl(self, site_dict: dict[str, Any]):
        site = self._find_site(site_dict)

        self.log.info(f'Starting crawler for [{site}]')

        async with self:
            if site:
                site.status.crawling = True

        crawler = CrochetCrawlerRunner(JobsFromUrlSpider, site.url)
        stats = crawler.crawl().wait(timeout=600)

        async with self:
            if site:
                site.status.crawling = False
            await self.load_sites()
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

    @rx.background
    async def clear_jobs(self, site_dict: dict[str, Any]):
        site = self._find_site(site_dict)
        self.log.info(f'Deleting jobs from [{site}]')
        async with self:
            site.status.clearing = True

        Locator.jobs_sites_with_jobs_service.clear_jobs(site)

        async with self:
            await self.load_sites()
            site.status.clearing = False
