from __future__ import annotations

from typing import override
from urllib.parse import urlparse, urlunparse

import requests
from requests import HTTPError, RequestException

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_management.backend.entity.sites_and_jobs import SitesAndJobs, ParseError
from job_management.backend.service.job_offer import JobOfferService
from job_management.backend.service.site import JobSitesService
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto
from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.loader.job_offer_loader import JobOfferItemLoader


class JobSitesWithJobsService(JobOfferService, JobSitesService):
    def __init__(self, db: JobManagementDb):
        JobOfferService.__init__(self, db)
        JobSitesService.__init__(self, db)

    @override
    def hide_job(self, job: JobOffer):
        super().hide_job(job)
        self.update_unseen_for_job_site(job)

    @override
    def show_job(self, job: JobOffer):
        super().show_job(job)
        self.update_unseen_for_job_site(job)

    def update_unseen_for_job_site(self, job: JobOffer):
        site = self.site_for_url(job.site_url)
        unseen_jobs = self.count_jobs_unseen_for_site(site)
        self.update_jobs_statistics(site, unseen=unseen_jobs)

    def update_statistic_for_job_site(self, site: JobSite):
        unseen_jobs = self.count_jobs_unseen_for_site(site)
        total_jobs = self.count_jobs_total_for_site(site)
        self.update_jobs_statistics(site, total=total_jobs, unseen=unseen_jobs)

    def clear_jobs(self, site: JobSite):
        self.clear_jobs_for_site(site)
        self.update_jobs_statistics(site, total=0, unseen=0)

    def delete(self, site: JobSite):
        self.clear_jobs_for_site(site)
        self.sites.delete_many({'url': {'$eq': site.url}})

    @override
    def add_job(self, job: JobOffer):
        super().add_job(job)
        site = self.site_for_url(job.site_url)
        self.update_statistic_for_job_site(site)

    def parse_sites_and_jobs(self, urls: list[str]) -> SitesAndJobs:
        sites_and_jobs = SitesAndJobs()
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
            except (HTTPError, RequestException) as e:
                self.log.warning(f'Fetching [{url}] produced error. Skipping', exc_info=e)
                sites_and_jobs.add_error(url, e)
                continue
            page_url = urlparse(url, 'https')
            site_title = page_url.netloc.capitalize()
            site_url = urlunparse((page_url.scheme, page_url.netloc, '', '', '', ''))
            item_loader = JobOfferItemLoader.from_requests(response).populate(site_url)
            if item_loader.is_valid():
                job_offer = JobOfferDto.from_dict(item_loader.load())
                sites_and_jobs.add(JobSiteDto(title=site_title, url=site_url),
                                   job_offer,
                                   JobOfferBodyDto(url=job_offer.url, body=response.text))
            else:
                sites_and_jobs.add_error(url, Exception('Could not load job offer from url'))

        self.log.info(f'Parsed {sites_and_jobs.num_sites} sites and {sites_and_jobs.num_jobs} jobs')
        return sites_and_jobs

    def add_jobs_from(self, urls: list[str]) -> SitesAndJobs:
        sites_and_jobs = self.parse_sites_and_jobs(urls)
        for site in sites_and_jobs.sites:
            if not self.sites.contains(site):
                self.sites.add(site)
            for job in sites_and_jobs.jobs[site.url]:
                if not self.jobs.contains(job):
                    self.jobs.add(job)
                if not self.jobs_body.contains(sites_and_jobs.jobs_body[job.url]):
                    self.jobs_body.add(sites_and_jobs.jobs_body[job.url])
            self.update_statistic_for_job_site(JobSite(**site.to_dict()))
        return sites_and_jobs
