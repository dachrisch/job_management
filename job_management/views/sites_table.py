import reflex as rx
from reflex import Var

from ..backend.crawl import SitesCrawlerState, JobsCrawlerButton, JobsCrawlerState
from ..backend.data import SiteState
from ..backend.entity import JobSite


def _header_cell(text: str, icon: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )


def show_site(site: JobSite):
    return rx.table.row(
        rx.table.cell(site.title),
        rx.table.cell(rx.link(site.url, href=site.url, target='_blank')),
        rx.table.cell(rx.moment(site.last_scanned, from_now=True)),
        rx.table.cell(rx.button(rx.text(site.num_jobs),
                                on_click=rx.redirect(f'/jobs/?site={site.url}'),
                                size="2",
                                variant="solid")),
        rx.table.cell(
            rx.hstack(
                JobsCrawlerButton.create(site_url=site.url),
            )
        ),
        style={"_hover": {"bg": rx.color("gray", 3)}},
        align="center",
    )


def main_table():
    return rx.fragment(
        rx.flex(
            rx.button(
                rx.cond(SitesCrawlerState.running,
                        rx.spinner(loading=True),
                        rx.icon("building", size=26), ),
                rx.text("Crawl Websites", size="4", display=[
                    "none", "none", "block"]),
                size="3",
                on_click=SitesCrawlerState.start_crawling,
                disabled=SitesCrawlerState.running
            ),
            spacing="3",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Site", "building"),
                    _header_cell("Url", "link"),
                    _header_cell("Last Scanned", "history"),
                    _header_cell("Jobs", "briefcase"),
                    _header_cell("Actions", "cog"),
                ),
            ),
            rx.table.body(rx.foreach(SiteState.sites, show_site)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=SiteState.load_sites,
        ),
    )
