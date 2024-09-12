import logging
from typing import Union, Type, Iterable, Dict, Any

import montydb.results
import pymongo.results
from dataclasses_json import DataClassJsonMixin
from montydb import MontyCollection
from pymongo.collection import Collection

from job_offer_spider.item.db import HasUrl, HasId

ASCENDING = 1
DESCENDING = -1


class CollectionHandler[T]:

    def __init__(self, collection: Union[Collection, MontyCollection],
                 collection_type: Union[Type[T], DataClassJsonMixin]):
        self.collection_type = collection_type
        self.collection = collection
        self.log = logging.getLogger(f'{__name__}[{collection.name}]')

    def add(self, item: DataClassJsonMixin):
        self.log.info(f'storing: {item}')
        self.collection.insert_one(item.to_dict(encode_json=True))

    def contains(self, item: HasUrl) -> bool:
        return self.collection.count_documents({'url': item.url}) > 0

    def all(self, skip: int = None, limit: int = None, sort_key: str = '',
            direction: int = ASCENDING) -> Iterable[T]:
        return self.filter({}, skip, limit, sort_key, direction)

    def filter(self, condition: Dict[str, Any], skip: int = None, limit: int = None, sort_key: str = '',
               direction: int = ASCENDING) -> Iterable[T]:
        cursor = self.collection.find(condition)
        if skip:
            cursor.skip(skip)
        if limit:
            cursor.limit(limit)
        if sort_key and direction:
            cursor.sort(sort_key, direction=direction)

        self.log.debug(f'Filtered with [{condition}]: {cursor}')
        return map(lambda c: self.collection_type.from_dict(c), cursor)

    @property
    def size(self) -> int:
        return self.count({'url': {'$exists': True}})

    def count(self, condition: Dict[str, Any]):
        count_documents = self.collection.count_documents(condition)
        self.log.debug(f'found [{count_documents}] document for [{condition}]')
        return count_documents

    def update_one(self, condition: Dict[str, Any], update: Dict[str, Any], expect_modified: bool = True):
        update_result = self.collection.update_one(condition, update)
        self.log.debug(
            f'updating [{condition}] with [{update}]: {update_result.modified_count} '
            f'updated, {update_result.matched_count} matched')
        assert (not expect_modified or update_result.modified_count == 1) and update_result.matched_count == 1
        return update_result

    def update_item(self, item: Union[HasId, DataClassJsonMixin]):
        assert item.id, f'Item has no id: {item}'
        return self.update_one({'_id': {'$eq': item.id}},
                               {'$set': {k: v for k, v in item.to_dict(encode_json=True).items() if
                                         k != '_id'}})

    def delete(self, item: Union[HasId, T]) -> \
            Union[montydb.results.DeleteResult, pymongo.results.DeleteResult]:
        return self.collection.delete_one({'_id': {'$eq': item.id}})

    def delete_many(self, condition: Dict[str, Any]) -> \
            Union[montydb.results.DeleteResult, pymongo.results.DeleteResult]:
        many = self.collection.delete_many(condition)
        self.log.debug(f'Deleting [{condition}] affected [{many.deleted_count}] items')
        return many
