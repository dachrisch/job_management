from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasId


@dataclass_json
@dataclass
class CvDto(HasId, DataClassJsonMixin):
    title: Optional[str] = None
    text: Optional[str] = None
