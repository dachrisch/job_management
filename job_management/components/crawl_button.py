import reflex as rx

from job_management.backend.crawl import SitesCrawlerState


def crawl_eu_sites_button():
    return rx.button(
        rx.cond(SitesCrawlerState.running,
                rx.spinner(loading=True),
                rx.icon("building", size=26), ),
        rx.text("Crawl EU-Startup Websites", size="4", display=[
            "none", "none", "block"]),
        size="3",
        on_click=SitesCrawlerState.start_crawling,
        disabled=SitesCrawlerState.running
    )
