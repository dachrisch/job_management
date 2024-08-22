from dataclasses import dataclass
from datetime import datetime

from job_offer_spider.item.db import HasUrl


@dataclass
class TargetWebsiteDto(HasUrl):
    title: str
    added: datetime= datetime.now()
    last_scanned: datetime = datetime.now()
