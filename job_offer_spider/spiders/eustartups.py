from typing import override

import scrapy
from scrapy import Request
from scrapy.http import Response

from job_offer_spider.items import TargetWebsiteSpiderItem


class EuStartupsSpider(scrapy.Spider):
    name = "eu-startups"
    start_urls = ["https://www.eu-startups.com/directory/wpbdp_category/german-startups/page/4/"]

    @override
    def parse(self, response: Response, **kwargs) -> Request:
        next_pages = response.css('div.listing-thumbnail a::attr("href")')
        for next_page_selector in next_pages:
            next_page = next_page_selector.get()
            if next_page.endswith('/'):
                yield response.follow(next_page, self.parse_listing)

    def parse_listing(self, response: Response) -> Request:
        website = response.css('div.wpbdp-field-website div.value::text').get()
        title = response.xpath('//meta[@property="og:title"]/@content').get()
        if website:
            yield TargetWebsiteSpiderItem(title=title, url=website)
