import logging
from typing import Union, Dict, Any, Iterable

from dataclasses_json import DataClassJsonMixin
from montydb import MontyClient, set_storage
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from job_management.backend.service.google import GoogleCredentialsService, CredentialsService, \
    AlwaysValidCredentialsService
from job_offer_spider.db.collection import CollectionHandler, ASCENDING
from job_offer_spider.item.db import HasId, HasUrl
from job_offer_spider.item.db.cover_letter import JobOfferCoverLetterDto
from job_offer_spider.item.db.cv import CvDto
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto, JobOfferAnalyzeDto, JobOfferApplicationDto
from job_offer_spider.item.db.sites import JobSiteDto


class EmptyCollectionHandler(CollectionHandler):
    def __init__(self):
        super().__init__(None, None)

    def add(self, item: DataClassJsonMixin):
        pass

    def contains(self, item: HasUrl) -> bool:
        return False

    def all(self, skip: int = None, limit: int = None, sort_key: str = '', direction: int = ASCENDING) -> Iterable:
        return []

    def filter(self, condition: Dict[str, Any], skip: int = None, limit: int = None, sort_key: str = '',
               direction: int = ASCENDING) -> Iterable:
        return []

    @property
    def size(self) -> int:
        return 0

    def count(self, condition: Dict[str, Any]):
        return 0

    def update_one(self, condition: Dict[str, Any], update: Dict[str, Any], expect_modified: bool = True):
        pass

    def update_item(self, item: Union[HasId, DataClassJsonMixin]):
        pass

    def delete(self, item):
        pass

    def delete_many(self, condition: Dict[str, Any]):
        pass


class JobManagementDb:
    def __init__(self, client: Union[MontyClient, MongoClient], credentials_service: CredentialsService):
        self.db = client['job_management_db']
        self.credentials_service = credentials_service
        self.log = logging.getLogger(self.__class__.__name__)

    @property
    def sites(self) -> CollectionHandler[JobSiteDto]:
        return CollectionHandler[JobSiteDto](self.db['job_sites'], JobSiteDto)

    @property
    def jobs(self) -> CollectionHandler[JobOfferDto]:
        return CollectionHandler[JobOfferDto](self.db['job_offers'], JobOfferDto)

    @property
    def jobs_body(self) -> CollectionHandler[JobOfferBodyDto]:
        return CollectionHandler[JobOfferBodyDto](self.db['job_offers_body'], JobOfferBodyDto)

    @property
    def jobs_analyze(self):
        return CollectionHandler[JobOfferAnalyzeDto](self.db['job_offers_analyze'], JobOfferAnalyzeDto)

    @property
    def jobs_application(self):
        return CollectionHandler[JobOfferApplicationDto](self.db['job_offers_application'], JobOfferApplicationDto)

    @property
    def cover_letter_docs(self):
        return CollectionHandler[JobOfferCoverLetterDto](self.db['cover_letter_docs'], JobOfferCoverLetterDto)

    @property
    def cvs(self):
        return CollectionHandler[CvDto](self.db['cv'], CvDto)


class MontyJobManagementDb(JobManagementDb):
    def __init__(self, repository: str):
        set_storage(repository, storage='sqlite', check_same_thread=False)
        super().__init__(MontyClient(repository=repository), AlwaysValidCredentialsService())
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
