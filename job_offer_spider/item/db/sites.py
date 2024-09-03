from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasUrl, HasId


@dataclass_json
@dataclass
class JobStatistic:
    total: int = 0
    unseen: int = 0


@dataclass_json
@dataclass
class JobSiteDto(HasUrl, HasId, DataClassJsonMixin):
    title: str = None
    added: datetime = datetime.now()
    last_scanned: datetime = None
    jobs: Optional[JobStatistic]  = None
