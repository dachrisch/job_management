import logging

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.target_website import TargetWebsiteDto
from job_offer_spider.item.spider.target_website import TargetWebsiteSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreTargetWebsitePipeline(ChainablePipeline[TargetWebsiteSpiderItem]):

    def __init__(self):
        super().__init__(TargetWebsiteSpiderItem)
        self.db = JobOfferDb()
        self.log = logging.getLogger(__name__)

    def process_item(self, item: TargetWebsiteSpiderItem, spider):
        dto = TargetWebsiteDto(**dict(item))
        if self.db.sites.contains(dto):
            self.log.debug(f'Site already collected: {dto.url}')
        else:
            self.db.sites.add(dto)
        return item
