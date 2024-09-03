import os

import reflex as rx
from more_itertools import first

from job_offer_spider.db.collection import CollectionHandler
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.cv import CvDto


class CvService:
    def __init__(self, cvs: CollectionHandler[CvDto]):
        self.cvs = cvs

    def load_cv(self):
        cv_data = first(self.cvs.all(), None)
        if cv_data:
            return CvData(**cv_data.to_dict())

    async def store(self, cv_file: rx.UploadFile):
        cv_data = (await cv_file.read()).decode('utf-8')
        self.cvs.add(CvDto(title=cv_file.filename, text=cv_data))


class CvData(rx.Base):
    title: str = None
    text: str = None


class CvState(rx.State):
    load_cv_data_open: bool = False
    cv_data: CvData = None
    has_cv_data: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cv_service = CvService(JobManagementDb().cvs)

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


class OptionsState(rx.State):
    openai_key: str = os.getenv('OPENAI_API_KEY')
    openai_key_dialog_open: bool = False

    def toggle_openai_key_dialog_open(self):
        self.openai_key_dialog_open = not self.openai_key_dialog_open

    def new_openai_key(self, form_data: dict):
        openai_key = form_data.get('openai_api_key')
        print(form_data)
        if openai_key:
            self.openai_key = openai_key
        self.toggle_openai_key_dialog_open()
