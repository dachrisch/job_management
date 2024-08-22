from datetime import datetime, timedelta
from urllib.parse import urlparse

from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.spiders import SitemapSpider
from scrapy.utils.sitemap import Sitemap

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.spider.job_offer import JobOfferSpiderItem


class FindJobsSpider(SitemapSpider):
    name = "find-jobs"
    sitemap_follow = ['/job', '/career']

    def start_requests(self):
        db = JobOfferDb()
        timestamp_threshold = (datetime.now() - timedelta(days=7)).timestamp()

        for site in db.sites.filter(
                {
                    '$or': [
                        {'last_scanned': {'$eq': None}},
                        {'last_scanned': {'$lt': timestamp_threshold}}
                    ]
                }):
            site_url = urlparse(site.url, 'https')
            if not site_url.hostname and site_url.path:
                site_url = site_url._replace(netloc=site_url.path)
            site_url = site_url._replace(path='/robots.txt')
            assert site_url.hostname
            assert site_url.scheme
            assert site_url.path
            site.last_scanned = datetime.now()
            db.sites.update(site)
            yield Request(site_url.geturl(), self._parse_sitemap)

    def sitemap_filter(self, entries: Sitemap):
        for entry in entries:
            if any([loc in entry['loc'] for loc in self.sitemap_follow]):
                yield entry

    def parse(self, response, **kwargs):
        item_loader = ItemLoader(item=JobOfferSpiderItem(), response=response)
        item_loader.add_css('title', 'h1::text')
        item_loader.add_value('url', response.url)
        if not item_loader.get_output_value('title'):
            item_loader.replace_xpath('title', '//meta[@property="og:title"]/@content')
        yield item_loader.load_item()
