# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from difflib import SequenceMatcher
from urllib.parse import urlparse

from more_itertools import first, one
from scrapy import signals, Request, Spider
from scrapy.http import Response
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import SitemapSpider

from job_offer_spider.spider.findjobs import JobsFromUrlSpider, JobsFromDbSpider


class SitemapWhenRobotsFailsSpiderMiddleware:
    def process_spider_exception(self, response: Response, exception: Exception, spider: Spider):
        if response.status >= 400 and isinstance(exception, HttpError) and isinstance(spider, SitemapSpider):
            url = urlparse(response.url, 'https')
            sitemap_url = url._replace(path='/sitemap.xml')
            site_url = url._replace(path='')
            yield Request(sitemap_url.geturl(), callback=spider._parse_sitemap,
                          cb_kwargs={'site_url': self.find_site_url(site_url.geturl(), spider)})

    def find_site_url(self, url: str, spider: SitemapSpider):
        if isinstance(spider, JobsFromUrlSpider):
            return one(spider.scan_urls_callback())
        elif isinstance(spider, JobsFromDbSpider):
            matches:dict[str,float] = {}
            for scan_url in spider.scan_urls_callback():
                matches[scan_url]=SequenceMatcher(a=url, b=scan_url).ratio()
            return max(matches, key=matches.get)
        raise NotImplementedError


class JobOfferSpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class JobOfferSpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
