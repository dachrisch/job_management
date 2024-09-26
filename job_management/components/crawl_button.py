import reflex as rx

from ..backend.crawl.jobs import JobsCrawlerState
from ..backend.crawl.sites import EuStartupSitesCrawlerState, ArbeitsamtSitesCrawlerState


def crawl_eu_sites_button():
    return rx.button(
        rx.cond(EuStartupSitesCrawlerState.running,
                rx.spinner(loading=True),
                rx.icon("building", size=26), ),
        rx.text("Crawl EU-Startup Websites", size="4", display=[
            "none", "none", "block"]),
        size="3",
        on_click=EuStartupSitesCrawlerState.start_crawling,
        disabled=EuStartupSitesCrawlerState.running
    )


def crawl_arbeitsamt_button():
    return rx.button(
        rx.cond(ArbeitsamtSitesCrawlerState.running,
                rx.spinner(loading=True),
                rx.icon("building", size=26), ),
        rx.text("Crawl Arbeitsamt", size="4", display=[
            "none", "none", "block"]),
        size="3",
        on_click=ArbeitsamtSitesCrawlerState.start_crawling,
        disabled=ArbeitsamtSitesCrawlerState.running
    )


def scan_jobs_button():
    return rx.button(
        rx.cond(JobsCrawlerState.running,
                rx.spinner(loading=True),
                rx.icon("briefcase", size=26), ),
        rx.text("Scan Jobs", size="4", display=[
            "none", "none", "block"]),
        size="3",
        on_click=JobsCrawlerState.start_crawling,
        disabled=JobsCrawlerState.running
    )
