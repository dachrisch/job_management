import logging
from dataclasses import asdict

from montydb import MontyClient, MontyCollection
from scrapy import Item

from job_offer_spider.item.db import HasUrl, IsDataclass


class CollectionHandler:
    def __init__(self, collection: MontyCollection):
        self.collection = collection
        self.log = logging.getLogger(__name__)

    def add(self, item: IsDataclass):
        self.log.info(f'storing: {item}')
        self.collection.insert_one(asdict(item))

    def contains(self, item: HasUrl):
        return self.collection.count_documents({'url': item.url})

    def all(self):
        return self.collection.find({'url': {'$exists': True}})

    @property
    def size(self):
        return self.collection.count_documents({'url': {'$exists': True}})

class SitesCollectionHandler(CollectionHandler):
    def __init__(self, collection: MontyCollection):
        super().__init__(collection)


class JobOfferDb:
    def __init__(self):
        self.client = MontyClient(repository='.mongitadb')  # Use MongitaClientMemory() for in-memory storage
        self.db = self.client['job_offers_db']
        self.log = logging.getLogger(__name__)

    @property
    def sites(self):
        return SitesCollectionHandler(self.db['target_sites'])

    @property
    def jobs(self):
        return SitesCollectionHandler(self.db['job_offers'])
