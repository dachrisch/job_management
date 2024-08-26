import logging
from threading import Lock
from typing import Type, Iterable, Union, Any, Dict

from dataclasses_json import DataClassJsonMixin
from montydb import MontyClient, MontyCollection, set_storage

from job_offer_spider.item.db import HasUrl, HasId
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto
from job_offer_spider.item.db.target_website import TargetWebsiteDto


class CollectionHandler[T]:
    _mutex = Lock()

    def __init__(self, collection: MontyCollection, collection_type: Union[Type[T], DataClassJsonMixin]):
        self.collection_type = collection_type
        self.collection = collection
        self.log = logging.getLogger(__name__)

    def add(self, item: DataClassJsonMixin):
        with self._mutex:
            self.log.info(f'storing: {item}')
            self.collection.insert_one(item.to_dict(encode_json=True))

    def contains(self, item: HasUrl) -> bool:
        with self._mutex:
            return self.collection.count_documents({'url': item.url})

    def all(self) -> Iterable[T]:
        return self.filter({'url': {'$exists': True}})

    def filter(self, condition: Dict[str, Any]):
        with self._mutex:
            return map(lambda c: self.collection_type(**dict(c)), self.collection.find(condition))

    @property
    def size(self) -> int:
        return self.count({'url': {'$exists': True}})

    def count(self, condition: Dict[str, Any]):
        with self._mutex:
            return self.collection.count_documents(condition)

    def update(self, item: Union[HasId, DataClassJsonMixin]):
        with self._mutex:
            return self.collection.update_one({'_id': {'$eq': item.id}},
                                              {'$set': {k: v for k, v in item.to_dict(encode_json=True).items() if
                                                        k != '_id'}})


class JobOfferDb:
    def __init__(self):
        set_storage('.mongitadb', storage='sqlite', check_same_thread=False)
        self.client = MontyClient(repository='.mongitadb')
        self.db = self.client['job_offers_db']
        self.log = logging.getLogger(__name__)

    @property
    def sites(self) -> CollectionHandler[TargetWebsiteDto]:
        return CollectionHandler[TargetWebsiteDto](self.db['target_sites'], TargetWebsiteDto)

    @property
    def jobs(self) -> CollectionHandler[JobOfferDto]:
        return CollectionHandler[JobOfferDto](self.db['job_offers'], JobOfferDto)

    @property
    def jobs_body(self) -> CollectionHandler[JobOfferBodyDto]:
        return CollectionHandler[JobOfferBodyDto](self.db['job_offers_body'], JobOfferBodyDto)
