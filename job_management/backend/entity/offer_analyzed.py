from datetime import datetime
from typing import Optional

import reflex as rx


class JobOfferAnalyze(rx.Base):
    url: str = ''
    title: str = None
    about: str = None
    company_name: str = None
    requirements: str = None
    responsibilities: str = None
    offers: str = None
    additional: Optional[str] = None
    added: datetime = datetime.now()
