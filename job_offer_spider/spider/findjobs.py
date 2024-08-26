from datetime import datetime, timedelta
from urllib.parse import urlparse

from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from scrapy.utils.sitemap import Sitemap, sitemap_urls_from_robots

from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.spider.job_offer import JobOfferSpiderItem


class FindJobsSpider(SitemapSpider):
    name = "find-jobs"
    sitemap_follow = ['/job/', '/jobs/', '/career/', '/careers/']

    def start_requests(self):
        days_offset = self.settings.get('SPIDER_DAYS_OFFSET', 7)
        db = JobOfferDb()
        timestamp_threshold = (datetime.now() - timedelta(days=days_offset)).timestamp()

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
            yield Request(site_url.geturl(), self._parse_sitemap, cb_kwargs={'site_url': site.url})
            site.last_scanned = datetime.now()
            db.sites.update(site)

    def _parse_sitemap(self, response, **kwargs):
        if response.url.endswith("/robots.txt"):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap, cb_kwargs=kwargs)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                self.logger.warning(
                    "Ignoring invalid sitemap: %(response)s",
                    {"response": response},
                    extra={"spider": self},
                )
                return

            s = Sitemap(body)
            it = self.sitemap_filter(s)

            if s.type == "sitemapindex":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap, cb_kwargs=kwargs)
            elif s.type == "urlset":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    for r, c in self._cbs:
                        if r.search(loc):
                            yield Request(loc, callback=c, cb_kwargs=kwargs)
                            break

    def sitemap_filter(self, entries: Sitemap):
        for entry in entries:
            if any([loc in entry['loc'] for loc in self.sitemap_follow]):
                yield entry

    def parse(self, response, **kwargs):
        item_loader = ItemLoader(item=JobOfferSpiderItem(), response=response)
        item_loader.add_css('title', 'h1::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('body', response.text)
        item_loader.add_value('site_url', kwargs.get('site_url', None))
        if not item_loader.get_output_value('title'):
            item_loader.replace_xpath('title', '//meta[@property="og:title"]/@content')
        yield item_loader.load_item()
