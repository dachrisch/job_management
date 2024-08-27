from datetime import datetime

import reflex as rx


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    num_jobs: int = 0
    added: datetime = None
    last_scanned: datetime = None
    crawling: bool = False


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''
