import base64
from datetime import datetime
from typing import Any, Type

import reflex as rx
from pydantic.v1 import Field, validator, BaseConfig
from pydantic.v1.fields import ModelField

from job_management.backend.entity.status import JobStatus


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''
    site_url: str = ''
    added: datetime = None
    seen: datetime = None

    state: JobStatus = Field(default_factory=lambda: JobStatus())

    base64_url: str = Field(default=None)

    @validator('base64_url', always=True)
    def encode_base64(cls, value: Any, values: dict[str, Any], config: Type[BaseConfig], field: ModelField):
        print(values)
        return base64.b64encode(values['url'].encode()).decode('ascii')

