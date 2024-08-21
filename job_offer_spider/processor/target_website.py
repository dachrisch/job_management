import logging

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.items import TargetWebsiteSpiderItem
from job_offer_spider.processor.chainable import ChainablePipeline


class StoreTargetWebsitePipeline(ChainablePipeline[TargetWebsiteSpiderItem]):

    def __init__(self):
        super().__init__(TargetWebsiteSpiderItem)
        self.db = JobOfferDb()
        self.log = logging.getLogger(__name__)

    def process_item(self, item: TargetWebsiteSpiderItem, spider):
        if self.db.sites.contains(item):
            self.log.debug(f'Site already collected: {item['url']}')
        else:
            self.db.sites.add(item)
        return item
