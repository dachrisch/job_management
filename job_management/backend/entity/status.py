import reflex as rx


class SiteStatus(rx.Base):
    clearing: bool = False
    crawling: bool = False
    deleting: bool = False


class JobStatus(rx.Base):
    is_analyzing: bool = False
    analyzed: bool = False
    is_composing: bool = False
    composed: bool = False
    is_storing: bool = False
    stored: bool = False
