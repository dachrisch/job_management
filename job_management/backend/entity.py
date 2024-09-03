from datetime import datetime
from typing import Optional, Any, Type

import reflex as rx
from pydantic.v1 import Field, validator, BaseConfig
from pydantic.v1.fields import ModelField


class Statistics(rx.Base):
    total: int = 0
    unseen: int = 0


class Status(rx.Base):
    clearing: bool = False
    crawling: bool = False
    deleting: bool = False


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    jobs: Statistics = Field(default_factory=lambda: Statistics())
    added: datetime = None
    last_scanned: datetime = None
    crawling: bool = False
    deleting: bool = False
    status: Status = Field(default_factory=lambda: Status())

    @validator('jobs', pre=True)
    def jobs_not_none(cls, value: Any, values: dict[str, Any], config: Type[BaseConfig], field: ModelField):
        if not value:
            return field.get_default()
        return value


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''
    site_url: str = ''
    added: datetime = None
    seen: datetime = None
    is_analyzed: bool = False
    is_analyzing: bool = False


class JobOfferAnalyze(rx.Base):
    url: str = ''
    title: str = None
    about: str = None
    company_name: str = None
    requirements: str = None
    responsibilities: str = None
    offers: str = None
    additional: Optional[str] = None
    added: datetime = datetime.now()
