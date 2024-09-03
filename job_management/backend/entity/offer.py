from datetime import datetime

import reflex as rx
from pydantic.v1 import Field

from job_management.backend.entity.status import JobStatus


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''
    site_url: str = ''
    added: datetime = None
    seen: datetime = None

    state: JobStatus = Field(default_factory=lambda: JobStatus())
