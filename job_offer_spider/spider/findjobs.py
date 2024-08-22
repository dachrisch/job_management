from urllib.parse import urlparse

from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.spiders import SitemapSpider

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.spider.job_offer import JobOfferSpiderItem


class FindjobsSpider(SitemapSpider):
    name = "find-jobs"
    sitemap_follow = ['/job', '/career']

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

    def parse(self, response, **kwargs):
        item_loader = ItemLoader(item=JobOfferSpiderItem(), response=response)
        item_loader.add_css('title', 'h1::text')
        item_loader.add_value('url', response.url)
        yield item_loader.load_item()
