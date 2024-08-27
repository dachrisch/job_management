from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasUrl, HasId


@dataclass_json
@dataclass
class JobOfferDto(HasUrl, HasId, DataClassJsonMixin):
    title: str = None
    added: datetime = datetime.now()
    site_url: str = None


@dataclass_json
@dataclass
class JobOfferBodyDto(HasUrl, HasId, DataClassJsonMixin):
    body: str = field(default=None, repr=False)
    added: datetime = datetime.now()
