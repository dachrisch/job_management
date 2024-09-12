from __future__ import annotations

import sys
from datetime import timedelta, datetime
from typing import Optional

from montydb import ASCENDING, DESCENDING
from more_itertools import one

from job_management.backend.entity.site import JobSite
from job_offer_spider.db.collection import CollectionHandler
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.sites import JobSiteDto


class JobSitesService:
    sites: CollectionHandler[JobSiteDto]

    def __init__(self, db: JobManagementDb):
        self.sites = db.sites

    def site_for_url(self, site_url: str) -> JobSite:
        return one(map(self.dto_to_site, self.sites.filter({'url': {'$eq': site_url}})))

    def update_jobs_statistics(self, site: JobSite, total: Optional[int] = None, unseen: Optional[int] = None):
        if total is not None:
            self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'jobs.total': total}}, expect_modified=False)
        if unseen is not None:
            self.sites.update_one({'url': {'$eq': site.url}}, {'$set': {'jobs.unseen': unseen}}, expect_modified=False)

    def load_sites(self, page: int, page_size: int, sort_key: str, sort_reverse: bool = False):
        return list(
            map(self.dto_to_site, self.sites.all(skip=page * page_size, limit=page_size,
                                                 sort_key=sort_key.lower(),
                                                 direction=DESCENDING if sort_reverse else ASCENDING)))

    def dto_to_site(self, s: JobSiteDto):
        return JobSite(**(s.to_dict()))

    def count_sites(self, days_from_now: int = sys.maxsize) -> int:
        condition = {}
        if days_from_now is not sys.maxsize:
            condition = {'added': {'$lt': (datetime.now() - timedelta(days=days_from_now)).timestamp()}}
        return self.sites.count(condition)

    def add_site(self, site: JobSiteDto):
        self.sites.add(site)
