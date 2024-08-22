# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose


class TargetWebsiteSpiderItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose()
    )
    url = scrapy.Field()


class JobOfferSpiderItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
