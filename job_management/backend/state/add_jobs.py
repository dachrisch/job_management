from typing import Any

import reflex as rx

from job_management.backend.service.site import SitesJobsOfferService
from job_management.backend.state.sites import SitesState
from job_offer_spider.db.job_management import JobManagementDb


class AddJobsState(rx.State):
    loading: bool = False
    is_dialog_open:bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobManagementDb()
        self.site_service = SitesJobsOfferService(self.db)

    @rx.background
    async def add_jobs_to_db(self, form_dict: dict[str, Any]):
        async with self:
            self.loading = True
        urls = form_dict['job_urls'].split('\n')
        self.site_service.add_jobs_from(urls)
        async with self:
            await (await self.get_state(SitesState)).load_sites()
            self.loading = False

    def toggle_dialog_open(self):
        self.is_dialog_open=not self.is_dialog_open