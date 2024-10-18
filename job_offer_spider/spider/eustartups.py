from typing import override, Any

from scrapy.http import Response
from scrapy.spiders import SitemapSpider

from job_offer_spider.loader.job_site_loader import JobSiteItemLoader


class EuStartupsSpider(SitemapSpider):
    name = "eu-startups"
    sitemap_urls = ["https://www.eu-startups.com/wpbdp_listing-sitemap.xml"]
    sitemap_follow = ['/directory/']

    @override
    def parse(self, response: Response, **kwargs) -> Any:
        item_loader = JobSiteItemLoader(response=response)
        if item_loader.is_valid():
            return item_loader.load()
