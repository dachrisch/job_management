from datetime import datetime

import reflex as rx
from pydantic import Field


class JobOfferApplication(rx.Base):
    url: str = ''
    text: str = ''
    added: datetime = Field(default_factory=lambda: datetime.now(), title='Date added')
