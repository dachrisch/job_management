import logging

from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.item.spider.site import SiteSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreTargetWebsitePipeline(ChainablePipeline[SiteSpiderItem]):

    def __init__(self):
        super().__init__(SiteSpiderItem)
        self.db = JobManagementDb()
        self.log = logging.getLogger(__name__)

    def process_item(self, item: SiteSpiderItem, spider):
        dto = JobSiteDto.from_dict(item)
        if self.db.sites.contains(dto):
            self.log.debug(f'Site already collected: {dto.url}')
        else:
            self.db.sites.add(dto)
        return item
