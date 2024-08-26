from datetime import datetime

import reflex as rx

from job_offer_spider.db.job_offer import JobOfferDb


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    last_scanned: datetime = None


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''


class SiteState(rx.State):
    num_sites: int = 0
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_sites(self):
        self.num_sites = len(self.sites)

    @rx.var(cache=True)
    def sites(self) -> list[JobSite]:
        return list(map(lambda s: JobSite(**s.to_dict()), self.db.sites.all()))

    def update_current_site(self):
        site_url = self.router.page.params.get('site', None)
        if site_url:
            site = next(filter(lambda s: s.url == site_url, self.sites))
            self.current_site = site


class JobsState(rx.State):
    num_jobs: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_jobs(self):
        self.num_jobs = len(self.jobs)

    @rx.var(cache=True)
    def jobs(self) -> list[JobOffer]:
        return list(map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.all()))
