import logging
from datetime import datetime, timedelta

import reflex as rx

from job_offer_spider.db.job_management import JobManagementDb


class JobsStatisticsState(rx.State):
    num_jobs: int = 0
    num_jobs_yesterday: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobManagementDb()
        self.info = logging.getLogger(self.__class__.__name__).info

    def load_jobs_statistic(self):
        self.num_jobs = self.db.jobs.count({})
        self.num_jobs_yesterday = self.db.jobs.count(
            {'added': {'$lt': (datetime.now() - timedelta(days=1)).timestamp()}})
