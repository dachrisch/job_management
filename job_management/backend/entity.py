from datetime import datetime
from typing import Optional

import reflex as rx


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    num_jobs: int = 0
    added: datetime = None
    last_scanned: datetime = None
    crawling: bool = False
    deleting:bool = False


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''
    site_url:str=''
    added: datetime = None
    is_analyzed: bool = False
    is_analyzing: bool = False

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
