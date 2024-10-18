from __future__ import annotations

from typing import Any

import requests
from scrapy.http import Response, TextResponse
from scrapy.loader import ItemLoader

from job_offer_spider.item.spider.site import SiteSpiderItem


class JobSiteItemLoader:
    @classmethod
    def from_requests(cls, r: requests.Response):
        return cls(TextResponse(url=r.url, body=r.content, status=r.status_code, headers=r.headers, request=r))

    def __init__(self, response: Response):
        self.response = response
        self.item_loader = ItemLoader(item=SiteSpiderItem(), response=response)
        self.item_loader.add_xpath('title', '//meta[@property="og:title"]/@content')
        if not self.item_loader.get_output_value('title'):
            self.item_loader.add_css('title', 'title::text')
        if not self.item_loader.get_output_value('title'):
            self.item_loader.add_css('title', 'h1::text')

    def add_value(self, name: str, value: Any):
        self.item_loader.add_value(name, value)

    def is_valid(self) -> bool:
        return self.item_loader.get_output_value('title') is not None

    def load(self) -> SiteSpiderItem:
        return self.item_loader.load_item()
