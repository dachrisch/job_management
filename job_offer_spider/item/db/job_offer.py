from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json

from job_offer_spider.item.db import HasUrl, HasId


@dataclass_json
@dataclass
class JobOfferDto(HasUrl, HasId):
    title: str = None
    added: datetime = datetime.now()
