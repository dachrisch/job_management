import logging

from scrapy import Item

from job_management.backend.service.locator import Locator
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto
from job_offer_spider.item.spider.job_offer import JobOfferSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreJobOfferPipeline(ChainablePipeline[JobOfferSpiderItem]):

    def __init__(self):
        super().__init__(JobOfferSpiderItem)
        self.db = Locator().job_management_db
        self.log = logging.getLogger(__name__)

    def process_item(self, item: JobOfferSpiderItem, spider) -> Item:
        dto = JobOfferDto.from_dict(item)
        if self.db.jobs.contains(dto):
            self.log.debug(f'Site already collected: {dto}')
        else:
            self.db.jobs.add(dto)
            job_dto = JobOfferBodyDto.from_dict(item)
            if not self.db.jobs_body.contains(job_dto):
                self.db.jobs_body.add(job_dto)
            self.db.sites.update_one({'url': {'$eq': dto.site_url}},
                                     {'$inc': {'jobs.total': 1, 'jobs.unseen': 1}}
                                     )
        return item
