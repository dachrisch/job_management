import logging
from datetime import datetime

from more_itertools import one

from job_management.backend.entity import JobOffer, JobSite
from job_offer_spider.db.job_management import JobManagementDb


class JobOfferService:

    def __init__(self, db: JobManagementDb):
        self.jobs = db.jobs
        self.jobs_body = db.jobs_body
        self.jobs_analyze = db.jobs_analyze
        self.log = logging.getLogger(f'{__name__}')

    def jobs_for_site(self, site: JobSite) -> list[JobOffer]:
        return list(
            map(lambda s: JobOffer(**s.to_dict()), self.jobs.filter({'site_url': {'$eq': site.url}}, sort_key='seen')))

    def job_from_url(self, job_url:str):
        return one(
                map(lambda s: JobOffer(**s.to_dict()), self.jobs.filter({'url': {'$eq': job_url}})))

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


