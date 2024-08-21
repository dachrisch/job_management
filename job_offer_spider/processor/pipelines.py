# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import Item

from job_offer_spider.processor.job_offer import StoreJobOfferPipeline
from job_offer_spider.processor.target_website import StoreTargetWebsitePipeline


class MultiPipesSpiderPipeline:
    def __init__(self):
        self.pipelines = [StoreTargetWebsitePipeline(), StoreJobOfferPipeline()]

    def process_item(self, item: Item, spider):
        return next(filter(lambda p: p.accepts(item), self.pipelines)).process_item(item, spider)
