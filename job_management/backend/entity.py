from datetime import datetime

import reflex as rx


class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    num_jobs: int = 0
    last_scanned: datetime = None


class JobOffer(rx.Base):
    title: str = ''
    url: str = ''
