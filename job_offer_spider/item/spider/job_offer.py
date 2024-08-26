import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from job_offer_spider.item import remove_non_letters


class JobOfferSpiderItem(scrapy.Item):
    title: str = scrapy.Field(
        input_processor=MapCompose(remove_non_letters),
        output_processor=TakeFirst()
    )
    url: str = scrapy.Field(output_processor=TakeFirst())
    body: str = scrapy.Field(output_processor=TakeFirst())
    site_url: str = scrapy.Field(output_processor=TakeFirst())
