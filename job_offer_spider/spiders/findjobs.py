from urllib.parse import urlparse

from scrapy import Request
from scrapy.spiders import SitemapSpider
from scrapy.utils.sitemap import Sitemap

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.items import JobOfferSpiderItem


class FindjobsSpider(SitemapSpider):
    name = "find-jobs"

    def start_requests(self):
        db = JobOfferDb()
        for site in db.sites.all():
            site_url = urlparse(site['url'], 'https')
            if not site_url.hostname and site_url.path:
                site_url = site_url._replace(netloc=site_url.path)
            site_url = site_url._replace(path='/robots.txt')
            assert site_url.hostname
            assert site_url.scheme
            assert site_url.path
            yield Request(site_url.geturl(), self._parse_sitemap)

    def sitemap_filter(self, entries: Sitemap):
        for entry in entries:
            if '/jobs/' in entry['loc']:
                yield entry

    def parse(self, response, **kwargs):
        title = response.css('h1::text').get()
        yield JobOfferSpiderItem(title=title, url=response.url)
