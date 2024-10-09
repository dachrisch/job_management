import logging
from typing import Union

from montydb import MontyClient, set_storage
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from job_management.backend.service.google import GoogleCredentialsService, CredentialsService
from job_offer_spider.db.access import CheckedAccessWrapper
from job_offer_spider.db.collection import CollectionHandler
from job_offer_spider.item.db.cover_letter import JobOfferCoverLetterDto
from job_offer_spider.item.db.cv import CvDto
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto, JobOfferAnalyzeDto, JobOfferApplicationDto
from job_offer_spider.item.db.sites import JobSiteDto


class JobManagementDb:
    def __init__(self, client: Union[MontyClient, MongoClient], credentials_service: CredentialsService):
        self.db = client['job_management_db']
        self.credentials_service = credentials_service
        self.log = logging.getLogger(self.__class__.__name__)

    @property
    def sites(self) -> CollectionHandler[JobSiteDto]:
        return CheckedAccessWrapper(CollectionHandler[JobSiteDto](self.db['job_sites'], JobSiteDto),
                                    self.credentials_service)

    @property
    def jobs(self) -> CollectionHandler[JobOfferDto]:
        return CheckedAccessWrapper(CollectionHandler[JobOfferDto](self.db['job_offers'], JobOfferDto),
                                    self.credentials_service)

    @property
    def jobs_body(self) -> CollectionHandler[JobOfferBodyDto]:
        return CheckedAccessWrapper(CollectionHandler[JobOfferBodyDto](self.db['job_offers_body'], JobOfferBodyDto),
                                    self.credentials_service)

    @property
    def jobs_analyze(self):
        return CheckedAccessWrapper(
            CollectionHandler[JobOfferAnalyzeDto](self.db['job_offers_analyze'], JobOfferAnalyzeDto),
            self.credentials_service)

    @property
    def jobs_application(self):
        return CheckedAccessWrapper(
            CollectionHandler[JobOfferApplicationDto](self.db['job_offers_application'], JobOfferApplicationDto),
            self.credentials_service)

    @property
    def cover_letter_docs(self):
        return CheckedAccessWrapper(
            CollectionHandler[JobOfferCoverLetterDto](self.db['cover_letter_docs'], JobOfferCoverLetterDto),
            self.credentials_service)

    @property
    def cvs(self):
        return CheckedAccessWrapper(CollectionHandler[CvDto](self.db['cv'], CvDto), self.credentials_service)


class MontyJobManagementDb(JobManagementDb):
    def __init__(self, repository: str, credentials_service: GoogleCredentialsService):
        set_storage(repository, storage='sqlite', check_same_thread=False)
        super().__init__(MontyClient(repository=repository), credentials_service)
        self.init()

    def init(self):
        for c in [self.sites, self.jobs, self.jobs_body, self.jobs_application, self.jobs_analyze, self.cvs,
                  self.cover_letter_docs]:
            _id = c.collection.insert_one({}).inserted_id
            assert c.collection.delete_one({'_id': _id}).deleted_count == 1


class MongoJobManagementDb(JobManagementDb):
    def __init__(self, username: str, password: str, credentials_service: GoogleCredentialsService):
        uri = f'mongodb+srv://{username}:{password}@cluster0.mhyen.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
        super().__init__(MongoClient(uri, server_api=ServerApi('1')), credentials_service)
