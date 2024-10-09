from dataclasses import dataclass, field
from datetime import datetime

import reflex as rx

from job_management.backend.entity.offer_analyzed import JobOfferAnalyze
from job_management.backend.entity.offer_application import JobOfferApplication


@dataclass
class JobApplicationCoverLetter:
    """
    Transient class for use in templating
    """
    url: str
    title: str
    company_name: str
    cover_body: str
    date: datetime = field(default_factory=lambda: datetime.now())

    @classmethod
    def from_analyze(cls, job_offer_analyzed: JobOfferAnalyze, job_offer_application: JobOfferApplication):
        return cls(url=job_offer_analyzed.url, title=job_offer_analyzed.title,
                   company_name=job_offer_analyzed.company_name,
                   cover_body=job_offer_application.text)


class JobApplicationCoverLetterDoc(rx.Base):
    url: str
    document_id: str
    name: str
    date: datetime = datetime.now()
