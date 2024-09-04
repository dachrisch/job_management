import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import reflex as rx
from googleapiclient.discovery import build
from more_itertools import first

from job_management.backend.api.credentials_helper import GoogleCredentialsHandler
from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.offer_analyzed import JobOfferAnalyze
from job_management.backend.entity.offer_application import JobOfferApplication
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.cover_letter import JobOfferCoverLetterDto


@dataclass
class JobApplicationCoverLetter:
    url: str
    title: str
    company_name: str
    cover_body: str
    date: datetime = datetime.now()

    @classmethod
    def from_analyze(cls, job_offer_analyzed: JobOfferAnalyze, job_offer_application: JobOfferApplication):
        return cls(url=job_offer_analyzed.url, title=job_offer_analyzed.title,
                   company_name=job_offer_analyzed.company_name,
                   cover_body=job_offer_application.text)


class JobApplicationCoverLetterDoc(rx.Base):
    url: str
    document_id: str
    name: str


class JobApplicationStorageService:
    google_credentials_json: dict[str, Any] = {}
    template_id: str = "1CVawnjkR2eMJ6pqHlu8su3zvmrIdesfR78DNAUhKubE"

    def __init__(self, db: JobManagementDb, ):
        self.jobs = db.jobs
        self.cover_letter_docs = db.cover_letter_docs
        self.log = logging.getLogger(f'{__name__}')
        self.credentials_handler = GoogleCredentialsHandler.from_token()

    def load_cover_letter_doc(self, job_offer: JobOffer):
        return first(map(lambda a: JobApplicationCoverLetterDoc(**a.to_dict()),
                         self.cover_letter_docs.filter({'url': {'$eq': job_offer.url}})), None)

    def store_application_in_google_docs(self, job_offer_cover_letter: JobApplicationCoverLetter):
        job_application_cover_letter_doc = self.copy_replace_doc(self.template_id, job_offer_cover_letter)

        self.cover_letter_docs.add(job_application_cover_letter_doc)
        self.jobs.update_one({'url': job_offer_cover_letter.url}, {'$set': {'state.stored': True}})

    def copy_replace_doc(self, template_id: str,
                         job_offer_cover_letter: JobApplicationCoverLetter) -> JobOfferCoverLetterDto:
        credentials = self.credentials_handler.ensure_logged_in().credentials

        docs_service = build("docs", "v1", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)
        cover_letter_file = drive_service.files().copy(fileId=template_id, body={
            'name': f'Anschreiben - {job_offer_cover_letter.company_name}'}).execute()

        requests = [
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{date}}',
                        'matchCase': 'true'
                    },
                    'replaceText': str(job_offer_cover_letter.date.strftime("%d.%m.%Y")),
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{company_name}}',
                        'matchCase': 'true'
                    },
                    'replaceText': job_offer_cover_letter.company_name,
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{role_title}}',
                        'matchCase': 'true'
                    },
                    'replaceText': job_offer_cover_letter.title,
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{cover_body}}',
                        'matchCase': 'true'
                    },
                    'replaceText': job_offer_cover_letter.cover_body,
                }
            }

        ]

        response = docs_service.documents().batchUpdate(
            documentId=cover_letter_file.get('id'), body={'requests': requests}).execute()
        return JobOfferCoverLetterDto(url=job_offer_cover_letter.url,
                                      document_id=cover_letter_file.get('id'),
                                      name=cover_letter_file.get('name'))
