from __future__ import annotations

from dataclasses import dataclass, field

from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto
from job_offer_spider.item.db.sites import JobSiteDto


@dataclass
class ParseError:
    url: str
    reason: Exception


@dataclass
class SitesAndJobs:
    sites: list[JobSiteDto] = field(default_factory=lambda: [])
    jobs: dict[str, list[JobOfferDto]] = field(default_factory=lambda: {})
    jobs_body: dict[str, JobOfferBodyDto] = field(default_factory=lambda: {})
    errors: list[ParseError] = field(default_factory=lambda: [])

    def add(self, site: JobSiteDto, offer: JobOfferDto, body: JobOfferBodyDto):
        self.sites.append(site)
        if site.url not in self.jobs:
            self.jobs[site.url] = []

        self.jobs[site.url].append(offer)
        self.jobs_body[offer.url] = body

    @property
    def num_sites(self):
        return len(self.sites)

    @property
    def num_jobs(self):
        return sum(len(offer_list) for offer_list in self.jobs.values())

    @property
    def all_jobs(self) -> list[JobOfferDto]:
        return list(x for v in self.jobs.values() for x in v)

    def add_error(self, url: str, e: Exception):
        self.errors.append(ParseError(url, e))
