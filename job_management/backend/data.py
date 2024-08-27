import reflex as rx

from job_management.backend.entity import JobSite, JobOffer
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.target_website import TargetWebsiteDto


class SiteState(rx.State):
    num_sites: int = 0
    current_site: JobSite = JobSite()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_sites(self):
        # noinspection PyTypeChecker
        self.num_sites = len(self.sites)

    @rx.var(cache=False)
    def sites(self) -> list[JobSite]:
        return list(map(self.load_job_site, self.db.sites.all()))

    def update_current_site(self):
        site_url = self.router.page.params.get('site', None)
        if site_url:
            # noinspection PyTypeChecker
            site = next(filter(lambda s: s.url == site_url, self.sites))
            self.current_site = site

    def load_job_site(self, s: TargetWebsiteDto):
        site_dict = s.to_dict()
        site_dict['num_jobs'] = self.db.jobs.count({'site_url': {'$eq': s.url}})
        return JobSite(**site_dict)


class JobsState(rx.State):
    num_jobs: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.site_url = self.router.page.params.get('site')

    def load_jobs(self):
        # noinspection PyTypeChecker
        self.num_jobs = len(self.jobs)

    @rx.var()
    def jobs(self) -> list[JobOffer]:
        site_url = self.router.page.params.get('site')
        return list(map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.filter({'site_url': {'$eq': site_url}})))
