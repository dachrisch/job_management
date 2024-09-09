import reflex as rx
from more_itertools import first

from job_management.backend.entity.cv import CvData
from job_management.backend.service.locator import Locator


class CvState(rx.State):
    load_cv_data_open: bool = False
    cv_data: CvData = None
    has_cv_data: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cv_service = Locator.cv_service

    def toggle_load_cv_data_open(self):
        self.load_cv_data_open = not self.load_cv_data_open

    async def new_cv_data(self, cv_files: list[rx.UploadFile]):
        cv_file = first(cv_files, None)
        if cv_file:
            await self.cv_service.store(cv_file)
        self.toggle_load_cv_data_open()
        self.load_cv()

    def load_cv(self):
        self.cv_data = self.cv_service.load_cv()
        self.has_cv_data = self.cv_data is not None
