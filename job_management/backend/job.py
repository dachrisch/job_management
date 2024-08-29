import reflex as rx

from job_management.backend.entity import JobOffer, JobSite
from job_offer_spider.db.job_offer import JobOfferDb


class JobState(rx.State):
    num_jobs: int = 0
    jobs: list[JobOffer] = []
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_jobs(self):
        site_url = self.router.page.params.get('site')
        self.jobs = list(map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.filter({'site_url': {'$eq': site_url}})))
        self.num_jobs = len(self.jobs)

    def update_current_site(self):
        site_url = self.router.page.params.get('site', None)
        if site_url:
            sites = map(lambda s: JobSite(**s.to_dict()), self.db.sites.filter({'url': {'$eq': site_url}}))
            self.current_site = next(sites)
