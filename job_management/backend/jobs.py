import logging
from datetime import datetime, timedelta

import reflex as rx

from job_offer_spider.db.job_offer import JobOfferDb


class JobsState(rx.State):
    num_jobs: int = 0
    num_jobs_yesterday: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.info = logging.getLogger(self.__class__.__name__).info

    def load_jobs(self):
        self.info('Loading Jobs')
        jobs = list(self.db.jobs.all())
        self.num_jobs = len(jobs)
        self.num_jobs_yesterday = len(
            [job for job in jobs if job.added.date() < (datetime.now().date() - timedelta(days=1))])
        self.info(f'Loaded [{self.num_jobs}] Jobs')
