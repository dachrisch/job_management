from __future__ import annotations

import requests
from scrapy.http import Response, TextResponse
from scrapy.loader import ItemLoader

from job_offer_spider.item.spider.job_offer import JobOfferSpiderItem


class JobOfferItemLoader:
    @classmethod
    def from_requests(cls, r: requests.Response):
        return cls(TextResponse(url=r.url, body=r.content, status=r.status_code, headers=r.headers, request=r))

    def __init__(self, response: Response):
        self.response = response
        self.item_loader = ItemLoader(item=JobOfferSpiderItem(), response=response)
        self.item_loader.add_css('title', 'h1::text')
        if not self.item_loader.get_output_value('title'):
            self.item_loader.replace_xpath('title', '//meta[@property="og:title"]/@content')
        if not self.item_loader.get_output_value('title'):
            self.item_loader.add_css('title', 'h1::text')

    def populate(self, site_url: str) -> JobOfferItemLoader:
        self.item_loader.add_value('url', self.response.url)
        self.item_loader.add_value('body', self.response.text)
        self.item_loader.add_value('site_url', site_url)

        return self

    def is_valid(self) -> bool:
        return self.item_loader.get_output_value('title') is not None

    def load(self) -> JobOfferSpiderItem:
        return self.item_loader.load_item()
