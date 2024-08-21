import logging

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.items import JobOfferSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreJobOfferPipeline(ChainablePipeline[JobOfferSpiderItem]):

    def __init__(self):
        super().__init__(JobOfferSpiderItem)
        self.db = JobOfferDb()
        self.log = logging.getLogger(__name__)

    def process_item(self, item: JobOfferSpiderItem, spider):
        if self.db.jobs.contains(item):
            self.log.debug(f'Site already collected: {item['url']}')
        else:
            self.db.jobs.add(item)
        return item
