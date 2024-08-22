from typing import override

from scrapy import Request
from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.spiders import SitemapSpider

from job_offer_spider.items import TargetWebsiteSpiderItem


class EuStartupsSpider(SitemapSpider):
    name = "eu-startups"
    sitemap_urls = ["https://www.eu-startups.com/wpbdp_listing-sitemap.xml"]
    sitemap_follow = ['/directory/']

    @override
    def parse(self, response: Response, **kwargs) -> Request:
        item_loader = ItemLoader(item=TargetWebsiteSpiderItem(), response=response)
        item_loader.add_xpath('title', '//meta[@property="og:title"]/@content')
        item_loader.add_css('url', 'div.wpbdp-field-website div.value::text')
        if item_loader.get_output_value('url'):
            return item_loader.load_item()
