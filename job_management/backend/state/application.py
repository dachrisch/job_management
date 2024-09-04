from typing import Optional

import reflex as rx

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.offer_analyzed import JobOfferAnalyze
from job_management.backend.entity.offer_application import JobOfferApplication
from job_management.backend.service.application import JobApplicationService
from job_offer_spider.db.job_management import JobManagementDb


class ApplicationState(rx.State):
    job_offer: JobOffer = JobOffer()
    job_offer_analyzed: Optional[JobOfferAnalyze] = None
    job_offer_application: Optional[JobOfferApplication] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobManagementDb()
        self.application_service = JobApplicationService(self.db)

    def load_current_job_offer(self):
        job_url = self.router.page.params.get('job', '')
        if job_url:
            self.job_offer = self.application_service.job_from_url(job_url)
            self.job_offer_analyzed = self.application_service.load_job_analysis(self.job_offer)
            self.job_offer_application = self.application_service.load_job_application(self.job_offer)

    def set_openai_api_key(self, openai_api_key: str):
        self.application_service.openai_api_key = openai_api_key

    @rx.background
    async def analyze_job(self):
        async with self:
            self.job_offer.state.is_analyzing = True

        self.application_service.analyze_job(self.job_offer)

        async with self:
            self.load_current_job_offer()
            self.job_offer.state.is_analyzing = False

    @rx.background
    async def compose_application(self):
        async with self:
            self.job_offer.state.is_composing = True

        self.application_service.compose_application(self.job_offer)

        async with self:
            self.load_current_job_offer()
            self.job_offer.state.is_composing = False

    async def store_in_google_doc(self):
        async with self:
            self.job_offer.state.is_storing = True

        self.application_service.store_application_in_google_docs(self.job_offer)

        async with self:
            self.load_current_job_offer()
            self.job_offer.state.is_storing = False
