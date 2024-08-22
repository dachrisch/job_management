import logging

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.spider.job_offer import JobOfferSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreJobOfferPipeline(ChainablePipeline[JobOfferSpiderItem]):

    def __init__(self):
        super().__init__(JobOfferSpiderItem)
        self.db = JobOfferDb()
        self.log = logging.getLogger(__name__)

    def process_item(self, item: JobOfferSpiderItem, spider):
        dto = JobOfferDto(**dict(item))
        if self.db.jobs.contains(dto):
            self.log.debug(f'Site already collected: {dto}')
        else:
            self.db.jobs.add(dto)
        return item
