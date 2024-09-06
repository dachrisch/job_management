from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, override, Iterable
from urllib.parse import urlparse, urlunparse

import requests
from more_itertools import one
from requests import HTTPError

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_management.backend.service.job_offer import JobOfferService
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.loader.job_offer_loader import JobOfferItemLoader


class JobSitesService:
    def __init__(self, db: JobManagementDb):
        self.sites = db.sites

    def site_for_url(self, site_url: str) -> JobSite:
        return one(map(lambda s: JobSite(**s.to_dict()), self.sites.filter({'url': {'$eq': site_url}})))

    def update_jobs_statistics(self, site: JobSite, total: Optional[int] = None, unseen: Optional[int] = None):
        if total is not None:
            self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'jobs.total': total}}, expect_modified=False)
        if unseen is not None:
            self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'jobs.unseen': unseen}}, expect_modified=False)


class SitesJobsOfferService(JobOfferService, JobSitesService):
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

    def update_statistic_for_job_site(self, job: JobOffer):
        site = self.site_for_url(job.site_url)
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
        self.update_statistic_for_job_site(job)

    def parse_sites_and_jobs(self, urls: list[str]) -> SitesAndJobs:
        sites_and_jobs = SitesAndJobs()
        for url in urls:
            response = requests.get(url)
            try:
                response.raise_for_status()
            except HTTPError as e:
                self.log.warning(f'Fetching [{url}] produced error. Skipping', exc_info=e)
                continue
            page_url = urlparse(url, 'https')
            site_title = page_url.netloc.capitalize()
            site_url = urlunparse((page_url.scheme, page_url.netloc, '', '', '', ''))
            item_loader = JobOfferItemLoader.from_requests(response).populate(site_url)
            if item_loader.is_valid():
                sites_and_jobs.add(JobSite(title=site_title, url=site_url),JobOffer(**JobOfferDto.from_dict(item_loader.load()).to_dict()))
        return sites_and_jobs

    def add_jobs_from(self, urls: list[str]):
        sites_and_jobs = self.parse_sites_and_jobs(urls)
        for site in sites_and_jobs.sites:
            self.sites.add(JobSiteDto.from_dict(site.dict()))
            for job in sites_and_jobs.jobs[site.url]:
                self.jobs.add(JobOfferDto.from_dict(job.dict()))


@dataclass
class SitesAndJobs:

    sites: list[JobSite] = field(default_factory=lambda: [])
    jobs: dict[str, list[JobOffer]] = field(default_factory=lambda: {})

    def add(self, site:JobSite, offer:JobOffer):
        self.sites.append(site)
        if site.url not in self.jobs:
            self.jobs[site.url] =[]

        self.jobs[site.url].append(offer)