from dataclasses import dataclass
from datetime import datetime


from job_offer_spider.item.db import HasUrl, HasId


@dataclass
class TargetWebsiteDto(HasUrl, HasId):
    title: str = None
    added: datetime = datetime.now()
    last_scanned: datetime = None

