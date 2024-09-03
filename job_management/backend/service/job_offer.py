import logging
from datetime import datetime
from typing import override, Optional

from more_itertools import one

from job_management.backend.entity import JobOffer, JobSite
from job_offer_spider.db.job_offer import JobOfferDb


class JobOfferService:

    def __init__(self, db: JobOfferDb):
        self.jobs = db.jobs
        self.jobs_body = db.jobs_body
        self.jobs_analyze = db.jobs_analyze
        self.log = logging.getLogger(f'{__name__}')

    def jobs_for_site(self, site: JobSite) -> list[JobOffer]:
        return list(
            map(lambda s: JobOffer(**s.to_dict()), self.jobs.filter({'site_url': {'$eq': site.url}}, sort_key='seen')))

    def count_jobs_unseen_for_site(self, site: JobSite):
        return self.jobs.count(
            {'$and': [
                {'site_url': {'$eq': site.url}},
                {'$or': [
                    {'seen': {'$exists': False}},
                    {'seen': {'$eq': None}}
                ]}
            ]}
        )

    def hide_job(self, job: JobOffer):
        self.jobs.update_one({'url': {'$eq': job.url}}, {'$set': {'seen': datetime.now().timestamp()}})

    def show_job(self, job: JobOffer):
        self.jobs.update_one({'url': {'$eq': job.url}}, {'$unset': {'seen': ''}})

    def clear_jobs_for_site(self, site: JobSite):
        jobs_url = list(map(lambda s: s.url, self.jobs.filter({'site_url': {'$eq': site.url}})))
        self.log.debug(f'clearing jobs for [{site}]: deleting [{len(jobs_url)}] jobs')
        delete_result = self.jobs.delete_many({'url': {'$in': jobs_url}})
        assert delete_result.deleted_count == len(jobs_url)
        self.jobs_body.delete_many({'url': {'$in': jobs_url}})
        self.jobs_analyze.delete_many({'url': {'$in': jobs_url}})


class JobSitesService:
    def __init__(self, db: JobOfferDb):
        self.sites = db.sites

    def site_for_url(self, site_url: str) -> JobSite:
        return one(map(lambda s: JobSite(**s.to_dict()), self.sites.filter({'url': {'$eq': site_url}})))

    def update_jobs_statistics(self, site: JobSite, total: Optional[int] = None, unseen: Optional[int] = None):
        if total is not None:
            self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'jobs.total': total}})
        if unseen is not None:
            self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'jobs.unseen': unseen}})


class SitesJobsOfferService(JobOfferService, JobSitesService):
    def __init__(self, db: JobOfferDb):
        JobOfferService.__init__(self, db)
        JobSitesService.__init__(self, db)

    @override
    def hide_job(self, job: JobOffer):
        super().hide_job(job)
        self.update_unseen_for_job(job)

    @override
    def show_job(self, job: JobOffer):
        super().show_job(job)
        self.update_unseen_for_job(job)

    def update_unseen_for_job(self, job):
        site = self.site_for_url(job.site_url)
        unseen_jobs = self.count_jobs_unseen_for_site(site)
        self.update_jobs_statistics(site, unseen=unseen_jobs)

    def clear_jobs(self, site: JobSite):
        self.clear_jobs_for_site(site)
        self.update_jobs_statistics(site, total=0, unseen=0)

    def delete(self, site: JobSite):
        self.clear_jobs_for_site(site)
        self.sites.delete_many({'url': {'$eq': site.url}})
