import base64
from datetime import datetime
from typing import Any, Type, Iterable, Tuple

import reflex as rx
from pydantic.v1 import Field, validator, BaseConfig
from pydantic.v1.fields import ModelField

from job_management.backend.entity.status import JobStatus


class JobOffer(rx.Base):
    title: str = Field('', title='Job Title')
    url: str = Field('', title='Job Url')
    site_url: str = Field('', title='Site Url')
    added: datetime = Field(None, title='Date added')
    seen: datetime = Field(None, title='Date seen')

    state: JobStatus = Field(default_factory=lambda: JobStatus(), title='Process State')

    base64_url: str = Field(default=None, sort_exclude=True)

    @validator('base64_url', always=True)
    def encode_base64(cls, value: Any, values: dict[str, Any], config: Type[BaseConfig], field: ModelField):
        return base64.b64encode(values['url'].encode()).decode('ascii')

    @classmethod
    def sortable_fields(cls) -> Iterable[Tuple[str, ModelField]]:
        return filter(lambda kv: not kv[1].field_info.extra.get('sort_exclude', False),
                      cls.get_fields().items())
