import logging
from abc import ABC, abstractmethod
from typing import Type

from scrapy import Item


class ChainablePipeline[T](ABC):
    def __init__(self, item_type: Type[T]):
        self.item_type = item_type

    def accepts(self, item: Item) -> bool:
        return isinstance(item, self.item_type)

    @abstractmethod
    def process_item(self, item: T, spider):
        raise NotImplementedError


class DefaultPipeline(ChainablePipeline[Item]):

    def __init__(self):
        super().__init__(Item)
        self.log = logging.getLogger(__name__)

    def process_item(self, item: Item, spider):
        self.log.error(f'Item not processed: {item}')
