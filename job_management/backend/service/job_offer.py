import logging
import sys
from datetime import datetime, timedelta

import requests
from more_itertools import one
from pydantic.v1 import ValidationError

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_offer_spider.db.collection import CollectionHandler, ASCENDING, DESCENDING
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.cover_letter import JobOfferCoverLetterDto
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto, JobOfferAnalyzeDto, JobOfferApplicationDto


class JobOfferService:
    jobs: CollectionHandler[JobOfferDto]
    jobs_body: CollectionHandler[JobOfferBodyDto]
    jobs_analyze: CollectionHandler[JobOfferAnalyzeDto]
    jobs_application: CollectionHandler[JobOfferApplicationDto]
    cover_letter_docs: CollectionHandler[JobOfferCoverLetterDto]

    def __init__(self, db: JobManagementDb):
        self.jobs = db.jobs
        self.jobs_body = db.jobs_body
        self.jobs_analyze = db.jobs_analyze
        self.jobs_application = db.jobs_application
        self.cover_letter_docs = db.cover_letter_docs
        self.log = logging.getLogger(__name__)

    def load_jobs(self, page: int, page_size: int, sort_key: str, sort_reverse: bool = False):
        return list(
            map(self.dto_to_job, self.jobs.all(skip=page * page_size, limit=page_size, sort_key=sort_key.lower(),
                                               direction=DESCENDING if sort_reverse else ASCENDING)))

    def jobs_for_site(self, site: JobSite) -> list[JobOffer]:
        return list(
            map(self.dto_to_job, self.jobs.filter({'site_url': {'$eq': site.url}}, sort_key='seen')))

    def job_from_url(self, job_url: str):
        return one(
            map(self.dto_to_job, self.jobs.filter({'url': {'$eq': job_url}})))

    def dto_to_job(self, job_dto: JobOfferDto):
        try:
            return JobOffer(**job_dto.to_dict())
        except ValidationError as e:
            self.log.error(f'Could not load JobOffer from {job_dto}', e)
            raise

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

    def count_jobs_total_for_site(self, site: JobSite):
        return self.jobs.count(
            {'site_url': {'$eq': site.url}}
        )

    def count_jobs(self, days_from_now: int = sys.maxsize) -> int:
        condition = {}
        if days_from_now is not sys.maxsize:
            condition = {'added': {'$lt': (datetime.now() - timedelta(days=days_from_now)).timestamp()}}
        return self.jobs.count(condition)

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
        self.jobs_application.delete_many({'url': {'$in': jobs_url}})
        self.cover_letter_docs.delete_many({'url': {'$in': jobs_url}})

    def add_job(self, job: JobOffer):
        job_body_response = requests.get(job.url)
        job_body_response.raise_for_status()
        job_offer_body_dto = JobOfferBodyDto(url=job.url, body=job_body_response.text)
        job_offer_dto = JobOfferDto.from_dict(job.dict())
        self.jobs.add(job_offer_dto)
        self.jobs_body.add(job_offer_body_dto)
