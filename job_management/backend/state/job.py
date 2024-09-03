import logging
from typing import Any

import reflex as rx

from job_management.backend.entity import JobOffer, JobSite
from job_management.backend.service.job_offer import JobOfferService
from job_management.backend.service.site import JobSitesService, SitesJobsOfferService
from job_offer_spider.db.job_offer import JobOfferDb


class JobState(rx.State):
    jobs: list[JobOffer] = []
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sites_jobs_service = SitesJobsOfferService(JobOfferDb())
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
