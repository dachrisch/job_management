import reflex as rx

from job_management.backend.service.locator import Locator


class JobsStatisticsState(rx.State):
    num_jobs: int = 0
    num_jobs_yesterday: int = 0

    def load_jobs_statistic(self):
        self.num_jobs = Locator.job_offer_service.count_jobs()
        self.num_jobs_yesterday = Locator.job_offer_service.count_jobs(days_from_now=1)
