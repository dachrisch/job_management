from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasUrl, HasId


@dataclass_json
@dataclass
class JobOfferState:
    is_analyzing: bool = False
    analyzed: bool = False


@dataclass_json
@dataclass
class JobOfferDto(HasUrl, HasId, DataClassJsonMixin):
    title: Optional[str] = None
    added: datetime = datetime.now()
    seen: Optional[datetime] = None
    site_url: Optional[str] = None
    state: JobOfferState = field(default_factory=lambda: JobOfferState())


@dataclass_json
@dataclass
class JobOfferBodyDto(HasUrl, HasId, DataClassJsonMixin):
    body: str = field(default=None, repr=False)
    added: datetime = datetime.now()


@dataclass_json
@dataclass
class JobOfferAnalyzeDto(HasUrl, HasId, DataClassJsonMixin):
    title: Optional[str] = None
    about: Optional[str] = None
    company_name: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    offers: Optional[str] = None
    additional: Optional[str] = None
    added: datetime = datetime.now()
