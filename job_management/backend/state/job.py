import logging
from typing import Any

import reflex as rx
from more_itertools import first

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_management.backend.service.locator import Locator
from job_management.backend.state.pagination import PaginationState


class JobPaginationState(rx.State,PaginationState):
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
        await (await self.get_state(JobState)).load_jobs()


class JobState(rx.State):
    jobs: list[JobOffer] = []
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sites_jobs_service = Locator.jobs_sites_with_jobs_service
        self.info = logging.getLogger(self.__class__.__name__).info

    async def load_jobs(self):
        paging_state = (await self.get_state(JobPaginationState))
        if self.current_site.url:
            self.jobs = self.sites_jobs_service.jobs_for_site(self.current_site)
        else:
            self.jobs = self.sites_jobs_service.load_jobs(paging_state.page, paging_state.page_size)
        paging_state.total_items = self.sites_jobs_service.count_jobs()
        self.info(f'loaded [{len(self.jobs)}] jobs for [{self.current_site}]')

    def update_current_site(self):
        site_url = self.router.page.params.get('site', '')
        if site_url:
            self.current_site = self.sites_jobs_service.site_for_url(site_url)
        else:
            self.current_site = JobSite()

    def hide_job(self, job_dict: dict[str, Any]):
        job_offer = JobOffer(**job_dict)
        self.sites_jobs_service.hide_job(job_offer)
        self.load_jobs()

    def show_job(self, job_dict: dict[str, Any]):
        job_offer = JobOffer(**job_dict)
        self.sites_jobs_service.show_job(job_offer)
        self.load_jobs()

    def add_job(self, form_dict: dict[str, Any]):
        job_offer = JobOffer(site_url=self.current_site.url, title=form_dict['job_title'], url=form_dict['job_url'])
        self.sites_jobs_service.add_job(job_offer)
        self.load_jobs()
