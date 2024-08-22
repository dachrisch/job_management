# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def remove_non_letters(string: str):
    return re.sub(r'[^A-Za-z0-9 ]+', '', string)


class TargetWebsiteSpiderItem(scrapy.Item):
    title: str = scrapy.Field(
        input_processor=MapCompose(remove_non_letters),
        output_processor=TakeFirst()
    )
    url: str = scrapy.Field(output_processor=TakeFirst())


class JobOfferSpiderItem(scrapy.Item):
    title: str = scrapy.Field(
        input_processor=MapCompose(remove_non_letters),
        output_processor=TakeFirst()
    )
    url: str = scrapy.Field(output_processor=TakeFirst())
