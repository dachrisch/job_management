from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasUrl, HasId


@dataclass_json
@dataclass
class JobOfferDto(HasUrl, HasId, DataClassJsonMixin):
    title: str = None
    added: datetime = datetime.now()


@dataclass_json
@dataclass
class JobOfferBodyDto(HasUrl, HasId, DataClassJsonMixin):
    body: str = None
    added: datetime = datetime.now()
