import reflex as rx

from job_management.backend.entity import JobOffer, JobOfferAnalyze
from job_management.backend.service.application import JobApplicationService
from job_offer_spider.db.job_offer import JobOfferDb


class ApplicationState(rx.State):
    job_offer: JobOffer = JobOffer()
    analyzed_job_offer: JobOfferAnalyze = JobOfferAnalyze()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()
        self.application_service = JobApplicationService(self.db)

    def load_current_job_offer(self):
        job_url = self.router.page.params.get('job', '')
        if job_url:
            self.job_offer = self.application_service.job_from_url(job_url)
            self.analyzed_job_offer = self.application_service.job_analysis(self.job_offer)
            self.job_offer.is_analyzed = self.analyzed_job_offer is not None

    @rx.background
    async def analyze_job(self):
        async with self:
            self.job_offer.is_analyzing = True

        self.application_service.analyze_job(self.job_offer)

        async with self:
            self.load_current_job_offer()
            self.job_offer.is_analyzed = True
            self.job_offer.is_analyzing = False
