from dataclasses import dataclass
from datetime import datetime


from job_offer_spider.item.db import HasUrl, HasId


@dataclass
class JobOfferDto(HasUrl, HasId):
    title: str = None
    added: datetime = datetime.now()
