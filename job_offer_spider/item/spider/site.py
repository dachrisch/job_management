import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from job_offer_spider.item import remove_non_letters


class SiteSpiderItem(scrapy.Item):
    title: str = scrapy.Field(
        input_processor=MapCompose(remove_non_letters),
        output_processor=TakeFirst()
    )
    url: str = scrapy.Field(output_processor=TakeFirst())
