from typing import Any

import reflex as rx

from job_management.backend.service.locator import Locator
from job_management.backend.state.sites import SitesState


class AddJobsState(rx.State):
    loading: bool = False
    is_dialog_open: bool = False

    @rx.background
    async def add_jobs_to_db(self, form_dict: dict[str, Any]):
        site_service = Locator().jobs_sites_with_jobs_service
        async with self:
            self.loading = True

        urls = form_dict['job_urls'].split('\n')
        sites_and_jobs = site_service.add_jobs_from(urls)

        for error in sites_and_jobs.errors:
            yield rx.toast.error(title=error.url, description=str(error.reason))

        for job in sites_and_jobs.all_jobs:
            yield rx.toast.success(title=job.title, description=str(job.url))

        async with self:
            await (await self.get_state(SitesState)).load_sites()
            self.loading = False

    def toggle_dialog_open(self):
        self.is_dialog_open = not self.is_dialog_open
