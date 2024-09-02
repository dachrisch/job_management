from datetime import datetime
from typing import override

from more_itertools import one

from job_management.backend.entity import JobOffer, JobSite
from job_offer_spider.db.job_offer import CollectionHandler, JobOfferDb
from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.target_website import TargetWebsiteDto


class JobOfferService:

    def __init__(self, jobs: CollectionHandler[JobOfferDto]):
        self.jobs = jobs

    def jobs_for_site(self, site: JobSite) -> list[JobOffer]:
        return list(
            map(lambda s: JobOffer(**s.to_dict()), self.jobs.filter({'site_url': {'$eq': site.url}}, sort_key='seen')))

    def count_jobs_unseen_for_site(self, site: JobSite):
        return self.jobs.count(
            {'$and': [
                {'site_url': {'$eq': site.url}},
                {'$or' : [
                    {'seen' : {'$exists': False}},
                    {'seen' : {'$eq': None}}
                ]}
            ]}
        )

    def hide_job(self, job: JobOffer):
        self.jobs.update_one({'url': {'$eq': job.url}}, {'$set': {'seen': datetime.now().timestamp()}})


class JobSitesService:
    def __init__(self, sites: CollectionHandler[TargetWebsiteDto]):
        self.sites = sites

    def site_for_url(self, site_url: str) -> JobSite:
        return one(map(lambda s: JobSite(**s.to_dict()), self.sites.filter({'url': {'$eq': site_url}})))

    def update_jobs_unseen(self, site: JobSite, num_jobs: int):
        self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'num_jobs_unseen': num_jobs}})


class SitesJobsOfferService(JobOfferService, JobSitesService):
    def __init__(self, db: JobOfferDb):
        JobOfferService.__init__(self, db.jobs)
        JobSitesService.__init__(self, db.sites)

    @override
    def hide_job(self, job: JobOffer):
        super().hide_job(job)
        site = self.site_for_url(job.site_url)
        unseen_jobs = self.count_jobs_unseen_for_site(site)
        self.update_jobs_unseen(site, unseen_jobs)
