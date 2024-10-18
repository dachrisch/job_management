from datetime import datetime
from typing import Any, Type, Iterable, Tuple

import reflex as rx
from pydantic.v1 import Field, validator, BaseConfig
from pydantic.v1.fields import ModelField

from job_management.backend.entity.stat import Statistics
from job_management.backend.entity.status import SiteStatus


class JobSite(rx.Base):
    title: str = Field('', title='Site Title')
    url: str = Field('', title='Site URL')
    jobs: Statistics = Field(default_factory=lambda: Statistics(), title='Found Jobs')
    added: datetime = Field(default_factory=lambda: datetime.now(), title='Date added')
    last_scanned: datetime = Field(None, title='Date last scanned')
    status: SiteStatus = Field(default_factory=lambda: SiteStatus(), sort_exclude=True)

    @validator('jobs', pre=True)
    def jobs_not_none(cls, value: Any, values: dict[str, Any], config: Type[BaseConfig], field: ModelField):
        if not value:
            return field.get_default()
        return value

    @classmethod
    def sortable_fields(cls) -> Iterable[Tuple[str, ModelField]]:
        return filter(lambda kv: not kv[1].field_info.extra.get('sort_exclude', False),
                      cls.get_fields().items())
