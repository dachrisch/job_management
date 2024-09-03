from datetime import datetime
from typing import Any, Type

import reflex as rx
from pydantic.v1 import Field, validator, BaseConfig
from pydantic.v1.fields import ModelField

from job_management.backend.entity.stat import Statistics
from job_management.backend.entity.status import SiteStatus


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    jobs: Statistics = Field(default_factory=lambda: Statistics())
    added: datetime = None
    last_scanned: datetime = None
    status: SiteStatus = SiteStatus()

    @validator('jobs', pre=True)
    def jobs_not_none(cls, value: Any, values: dict[str, Any], config: Type[BaseConfig], field: ModelField):
        if not value:
            return field.get_default()
        return value
