import logging
from typing import Any

import reflex as rx

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_management.backend.service.locator import Locator
from job_management.backend.service.sites_with_jobs import JobSitesWithJobsService
from job_offer_spider.db.job_management import JobManagementDb


class JobState(rx.State):
    jobs: list[JobOffer] = []
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sites_jobs_service = Locator.jobs_sites_with_jobs_service
        self.info = logging.getLogger(self.__class__.__name__).info

    def load_jobs(self):
        self.jobs = self.sites_jobs_service.jobs_for_site(self.current_site)
        self.info(f'loaded [{len(self.jobs)}] jobs for [{self.current_site}]')

    def update_current_site(self):
        site_url = self.router.page.params.get('site', '')
        if site_url:
            self.current_site = self.sites_jobs_service.site_for_url(site_url)

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
