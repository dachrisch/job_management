import logging

import reflex as rx

from job_management.backend.service.locator import Locator


class JobsStatisticsState(rx.State):
    num_jobs: int = 0
    num_jobs_yesterday: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jobs_service = Locator.job_offer_service
        self.info = logging.getLogger(self.__class__.__name__).info

    def load_jobs_statistic(self):
        self.num_jobs = self.jobs_service.count_jobs()
        self.num_jobs_yesterday = self.jobs_service.count_jobs(days_from_now=1)
