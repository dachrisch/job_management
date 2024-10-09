import logging
from functools import lru_cache

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from openai._utils import asyncify

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.storage import JobApplicationCoverLetter, JobApplicationCoverLetterDoc
from job_management.backend.service.google import GoogleCredentialsService
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.cover_letter import JobOfferCoverLetterDto


class JobApplicationStorageService:
    template_id: str = "1CVawnjkR2eMJ6pqHlu8su3zvmrIdesfR78DNAUhKubE"

    def __init__(self, db: JobManagementDb, credentials_service: GoogleCredentialsService):
        self.jobs = db.jobs
        self.cover_letter_docs = db.cover_letter_docs
        self.credentials_service:GoogleCredentialsService = credentials_service
        self.log = logging.getLogger(f'{__name__}')

    def load_cover_letter_docs(self, job_offer: JobOffer) -> list[JobApplicationCoverLetterDoc]:
        return list(map(lambda a: JobApplicationCoverLetterDoc(**a.to_dict()),
                        self.cover_letter_docs.filter({'url': {'$eq': job_offer.url}})))

    async def store_application_in_google_docs(self, job_offer_cover_letter: JobApplicationCoverLetter):
        job_application_cover_letter_dto = await asyncify(self.copy_replace_doc)(self.template_id,
                                                                                 job_offer_cover_letter)
        self.cover_letter_docs.add(job_application_cover_letter_dto)
        self.jobs.update_one({'url': job_offer_cover_letter.url}, {'$set': {'state.stored': True}},
                             expect_modified=False)

    def copy_replace_doc(self, template_id: str,
                         job_offer_cover_letter: JobApplicationCoverLetter) -> JobOfferCoverLetterDto:
        docs_service = self.credentials_service.load_service("docs", "v1")
        drive_service = self.credentials_service.load_service("drive", "v3")
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

        docs_service.documents().batchUpdate(
            documentId=cover_letter_file.get('id'), body={'requests': requests}).execute()

        return JobOfferCoverLetterDto(url=job_offer_cover_letter.url,
                                      document_id=cover_letter_file.get('id'),
                                      name=cover_letter_file.get('name'))
