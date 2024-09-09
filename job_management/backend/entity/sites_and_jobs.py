from __future__ import annotations

from dataclasses import dataclass, field

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite


@dataclass
class SitesAndJobs:

    sites: list[JobSite] = field(default_factory=lambda: [])
    jobs: dict[str, list[JobOffer]] = field(default_factory=lambda: {})

    def add(self, site:JobSite, offer:JobOffer):
        self.sites.append(site)
        if site.url not in self.jobs:
            self.jobs[site.url] =[]

        self.jobs[site.url].append(offer)

    @property
    def num_sites(self):
        return len(self.sites)

    @property
    def num_jobs(self):
        return sum(len(offer_list) for offer_list in self.jobs.values())
