import logging
from typing import Type, Iterable, Union, Any, Dict

from dataclasses_json import DataClassJsonMixin
from montydb import MontyClient, MontyCollection, set_storage, DESCENDING, ASCENDING

from job_offer_spider.item.db import HasUrl, HasId
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto, JobOfferAnalyzeDto
from job_offer_spider.item.db.target_website import TargetWebsiteDto


class CollectionHandler[T]:

    def __init__(self, collection: MontyCollection, collection_type: Union[Type[T], DataClassJsonMixin]):
        self.collection_type = collection_type
        self.collection = collection
        self.log = logging.getLogger(__name__)

    def add(self, item: DataClassJsonMixin):
        self.log.info(f'storing: {item}')
        self.collection.insert_one(item.to_dict(encode_json=True))

    def contains(self, item: HasUrl) -> bool:
        return self.collection.count_documents({'url': item.url})

    def all(self, skip: int = None, limit: int = None, sort_key: str = '',
            direction: ASCENDING | DESCENDING = ASCENDING) -> Iterable[T]:
        return self.filter({'url': {'$exists': True}}, skip, limit, sort_key, direction)

    def filter(self, condition: Dict[str, Any], skip: int = None, limit: int = None, sort_key: str = '',
               direction: ASCENDING | DESCENDING = ASCENDING) -> Iterable[T]:
        find = self.collection.find(condition)
        if skip:
            find.skip(skip)
        if limit:
            find.limit(limit)
        if sort_key or direction:
            find.sort(sort_key, direction=direction)
        return map(lambda c: self.collection_type.from_dict(c), find)

    @property
    def size(self) -> int:
        return self.count({'url': {'$exists': True}})

    def count(self, condition: Dict[str, Any]):
        return self.collection.count_documents(condition)

    def update_one(self, condition: Dict[str, Any], update: Dict[str, Any]):
        return self.collection.update_one(condition, update)

    def update_item(self, item: Union[HasId, DataClassJsonMixin]):
        return self.update_one({'_id': {'$eq': item.id}},
                               {'$set': {k: v for k, v in item.to_dict(encode_json=True).items() if
                                         k != '_id'}})

    def delete(self, item: Union[HasId, T]):
        return self.collection.delete_one({'_id': {'$eq': item.id}})


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

    @property
    def jobs_analyze(self):
        return CollectionHandler[JobOfferBodyDto](self.db['job_offers_analyze'], JobOfferAnalyzeDto)
