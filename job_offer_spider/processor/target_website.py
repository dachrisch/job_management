import logging

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.item.spider.target_website import TargetWebsiteSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreTargetWebsitePipeline(ChainablePipeline[TargetWebsiteSpiderItem]):

    def __init__(self):
        super().__init__(TargetWebsiteSpiderItem)
        self.db = JobOfferDb()
        self.log = logging.getLogger(__name__)

    def process_item(self, item: TargetWebsiteSpiderItem, spider):
        dto = JobSiteDto.from_dict(item)
        if self.db.sites.contains(dto):
            self.log.debug(f'Site already collected: {dto.url}')
        else:
            self.db.sites.add(dto)
        return item
