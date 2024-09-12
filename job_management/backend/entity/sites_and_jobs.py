from __future__ import annotations

from dataclasses import dataclass, field

from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto
from job_offer_spider.item.db.sites import JobSiteDto


@dataclass
class SitesAndJobs:
    sites: list[JobSiteDto] = field(default_factory=lambda: [])
    jobs: dict[str, list[JobOfferDto]] = field(default_factory=lambda: {})
    jobs_body: dict[str, JobOfferBodyDto] = field(default_factory=lambda: {})

    def add(self, site: JobSiteDto, offer: JobOfferDto, body: JobOfferBodyDto):
        self.sites.append(site)
        if site.url not in self.jobs:
            self.jobs[site.url] = []

        self.jobs[site.url].append(offer)
        self.jobs_body[offer.url]=body

    @property
    def num_sites(self):
        return len(self.sites)

    @property
    def num_jobs(self):
        return sum(len(offer_list) for offer_list in self.jobs.values())
