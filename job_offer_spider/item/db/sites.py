from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasUrl, HasId


@dataclass_json
@dataclass
class JobStatistic:
    total: int = 0
    unseen: int = 0


@dataclass_json
@dataclass
class JobSiteDto(HasId, HasUrl, DataClassJsonMixin):
    title: str = None
    added: datetime = field(default_factory=lambda: datetime.now())
    last_scanned: datetime = None
    jobs: JobStatistic = field(default_factory=lambda: JobStatistic())
