import reflex as rx
from more_itertools import first

from job_management.backend.entity.cv import CvData
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.cv import CvDto


class CvService:
    def __init__(self, db: JobManagementDb):
        self.cvs = db.cvs

    def load_cv(self):
        cv_data = first(self.cvs.all(), None)
        if cv_data:
            return CvData(**cv_data.to_dict())

    async def store(self, cv_file: rx.UploadFile):
        cv_data = (await cv_file.read()).decode('utf-8')
        self.cvs.add(CvDto(title=cv_file.filename, text=cv_data))
