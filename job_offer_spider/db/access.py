import logging
from inspect import getattr_static, ismethod
from typing import Iterable, Dict, Any, Union

from dataclasses_json import DataClassJsonMixin

from job_management.backend.service.google import CredentialsService
from job_offer_spider.db.collection import CollectionHandler, ASCENDING
from job_offer_spider.item.db import HasUrl, HasId


class EmptyCollectionHandler(CollectionHandler):

    def __init__(self):
        pass

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


class CheckedAccessWrapper(CollectionHandler):
    def __init__(self, wrapped: Any, credentials_service: CredentialsService):
        self.credentials_service = credentials_service
        self.wrapped = wrapped

    def __getattribute__(self, name: str) -> Any:
        log = logging.getLogger(__name__)
        method = getattr(getattr_static(self, 'wrapped'), name)
        if ismethod(method):
            def wrapper(*args, **kwargs):
                credentials_service: CredentialsService = getattr_static(self, 'credentials_service')
                if credentials_service.has_valid_credentials:
                    log.debug(f'Call to {name} authorized')
                    return method(*args, **kwargs)
                else:
                    log.debug(f'Call to {name} NOT authorized')
                    return getattr(EmptyCollectionHandler(), name)(*args, **kwargs)

            return wrapper
        else:
            return method
