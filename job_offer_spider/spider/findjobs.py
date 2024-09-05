from datetime import datetime, timedelta
from typing import Callable, Iterable
from urllib.parse import urlparse

from scrapy import Request
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from scrapy.utils.sitemap import Sitemap, sitemap_urls_from_robots

from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db import HasUrl
from job_offer_spider.item.db.sites import JobSiteDto
from job_offer_spider.loader.job_offer_loader import JobOfferItemLoader


class JobsFromUrlListSpider(SitemapSpider):
    sitemap_follow = ['/job/', '/jobs/',
                      '/career/', '/careers/',
                      '/sitemap',
                      'sitemap',
                      'Sitemap',
                      '/stellenangebote',
                      ]

    def __init__(self, scan_urls_callback: Callable[[], Iterable[str]], *a, **kw):
        super().__init__(*a, **kw)
        self.scan_urls_callback = scan_urls_callback

    def start_requests(self):

        for su in self.scan_urls_callback():
            site_url = urlparse(su, 'https')
            if not site_url.hostname and site_url.path:
                site_url = site_url._replace(netloc=site_url.path)
            site_url = site_url._replace(path='/robots.txt')
            assert site_url.hostname
            assert site_url.scheme
            assert site_url.path
            yield Request(site_url.geturl(), self._parse_sitemap, cb_kwargs={'site_url': su})
            self.inform_site_scanned(su)

    def _parse_sitemap(self, response, **kwargs):
        if response.url.endswith("/robots.txt"):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap, cb_kwargs=kwargs)
            else:
                site_url = urlparse(response.url, 'https')
                yield Request(site_url._replace(path='/sitemap.xml').geturl(), callback=self._parse_sitemap,
                              cb_kwargs=kwargs)
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
                            # added cb_kwargs
                            yield Request(loc, callback=c, cb_kwargs=kwargs)
                            break

    def sitemap_filter(self, entries: Sitemap):
        for entry in entries:
            if any([loc in entry['loc'] for loc in self.sitemap_follow]):
                yield entry

    def parse(self, response, **kwargs):
        item_loader = JobOfferItemLoader(response).populate(kwargs.get('site_url'))

        if item_loader.is_valid():
            yield item_loader.load()

    def inform_site_scanned(self, site_url: str):
        pass


class JobsFromUrlSpider(JobsFromUrlListSpider):
    name = "find-jobs-from-url"

    def __init__(self, site_url: str, *a, **kw):
        super().__init__(scan_urls_callback=lambda: [site_url], *a, **kw)
        self.db = JobManagementDb()

    def inform_site_scanned(self, site_url):
        if not self.db.sites.contains(HasUrl(site_url)):
            self.db.sites.add(JobSiteDto(title=site_url, url=site_url))

        for site in self.db.sites.filter({'url': {'$eq': site_url}}):
            site.last_scanned = datetime.now()
            self.db.sites.update_item(site)


class JobsFromDbSpider(JobsFromUrlListSpider):
    name = "find-jobs-from-db"

    def __init__(self, *a, **kw):
        super().__init__(scan_urls_callback=self.load_from_database, *a, **kw)
        self.db = JobManagementDb()

    def load_from_database(self) -> Iterable[str]:
        days_offset = self.settings.get('SPIDER_DAYS_OFFSET', 7)
        timestamp_threshold = (datetime.now() - timedelta(days=days_offset)).timestamp()

        return map(lambda s: s.url, self.db.sites.filter(
            {
                '$or': [
                    {'last_scanned': {'$eq': None}},
                    {'last_scanned': {'$lt': timestamp_threshold}}
                ]
            }))

    def inform_site_scanned(self, site_url):
        for site in self.db.sites.filter({'url': {'$eq': site_url}}):
            site.last_scanned = datetime.now()
            self.db.sites.update_item(site)
