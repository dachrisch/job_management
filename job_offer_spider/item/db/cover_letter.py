from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, DataClassJsonMixin

from job_offer_spider.item.db import HasId, HasUrl


@dataclass_json
@dataclass
class JobOfferCoverLetterDto(HasId, HasUrl, DataClassJsonMixin):
    name: Optional[str] = None
    document_id: Optional[str] = None
