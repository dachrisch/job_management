from urllib.parse import urljoin

import scrapy
from scrapy import Request
from scrapy.utils.sitemap import Sitemap

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.items import JobOfferSpiderItem


class FindjobsSpider(scrapy.spiders.SitemapSpider):
    name = "find-jobs"

    def start_requests(self):
        db = JobOfferDb()
        for site in db.sites.all():
            yield Request(urljoin(site['url'], '/robots.txt'), self._parse_sitemap)

    def sitemap_filter(self, entries: Sitemap):
        for entry in entries:
            if '/jobs/' in entry['loc']:
                yield entry

    def parse(self, response, **kwargs):
        title = response.css('h1::text').get()
        yield JobOfferSpiderItem(title=title, url=response.url)
