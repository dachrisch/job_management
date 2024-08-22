import logging
from dataclasses import asdict
from typing import Type, Iterable, Any

from montydb import MontyClient, MontyCollection
import inspect

from job_offer_spider.item.db import HasUrl, IsDataclass, HasId
from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.target_website import TargetWebsiteDto


class CollectionHandler[T]:
    def __init__(self, collection: MontyCollection, collection_type: Type[T]):
        self.collection_type = collection_type
        self.collection = collection
        self.log = logging.getLogger(__name__)

    def add(self, item: IsDataclass):
        self.log.info(f'storing: {item}')
        self.collection.insert_one(asdict(item))

    def contains(self, item: HasUrl) -> bool:
        return self.collection.count_documents({'url': item.url})

    def all(self) -> Iterable[T]:

        inspect.signature(self.collection_type.__init__)
        return map(lambda c: self.collection_type(**dict(c)), self.collection.find({'url': {'$exists': True}}))

    @property
    def size(self) -> int:
        return self.collection.count_documents({'url': {'$exists': True}})

    def update(self, item: HasId):
        return self.collection.update_one({'_id': {'$eq': item.id}},
                                          {'$set': {k: v for k, v in asdict(item).items() if k != '_id'}})


class JobOfferDb:
    def __init__(self):
        self.client = MontyClient(repository='.mongitadb')  # Use MongitaClientMemory() for in-memory storage
        self.db = self.client['job_offers_db']
        self.log = logging.getLogger(__name__)

    @property
    def sites(self) -> CollectionHandler[TargetWebsiteDto]:
        return CollectionHandler[TargetWebsiteDto](self.db['target_sites'], TargetWebsiteDto)

    @property
    def jobs(self) -> CollectionHandler[JobOfferDto]:
        return CollectionHandler[JobOfferDto](self.db['job_offers'], JobOfferDto)
