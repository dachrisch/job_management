import reflex as rx

from ..backend.crawl import SitesCrawlerState, JobsCrawlerState
from ..backend.data import SitesState
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
                rx.button(
                    rx.icon('refresh-cw'),
                    loading=site.crawling,
                    on_click=lambda: SitesState.start_crawl(site)
                ),
                rx.button(
                    rx.icon('trash-2'),
                    loading=SitesState.deleting,
                    on_click=lambda: SitesState.delete_site(site),
                    color_scheme='red'
                )
            )),
        style={"_hover": {"bg": rx.color("gray", 3)}},
        align="center",
    )


def form_field(
        label: str, placeholder: str, type: str, name: str, icon: str, default_value: str = ""
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.hstack(
                rx.icon(icon, size=16, stroke_width=1.5),
                rx.form.label(label),
                align="center",
                spacing="2",
            ),
            rx.form.control(
                rx.input(
                    placeholder=placeholder, type=type, default_value=default_value
                ),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def add_site_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=26),
                rx.text("Add Site", size="4", display=[
                    "none", "none", "block"]),
                size="3",
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="link", size=34),
                    color_scheme="grass",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Add New Site",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Add Site to be crawled",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5em",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        form_field(
                            "Name",
                            "Site Name",
                            "text",
                            "title",
                            "building",
                        ),
                        form_field(
                            "Url",
                            "Site Url",
                            "text",
                            "url",
                            "link",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("refresh-cw", size=16, stroke_width=1.5),
                                rx.text("Crawling"),
                                align="center",
                                spacing="2",
                            ),
                            rx.checkbox(
                                'After adding',
                                name="crawling",
                                direction="row",
                                as_child=True,
                            ),
                        ),
                        direction="column",
                        spacing="3",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button("Submit Site"),
                            ),
                            as_child=True,
                        ),
                        padding_top="2em",
                        spacing="3",
                        mt="4",
                        justify="end",
                    ),
                    on_submit=SitesState.add_site_to_db,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1.5em",
            border=f"2px solid {rx.color('accent', 7)}",
            border_radius="25px",
        ),
    )


def main_table():
    return rx.fragment(
        rx.flex(
            rx.button(
                rx.cond(SitesCrawlerState.running,
                        rx.spinner(loading=True),
                        rx.icon("building", size=26), ),
                rx.text("Crawl EU-Startup Websites", size="4", display=[
                    "none", "none", "block"]),
                size="3",
                on_click=SitesCrawlerState.start_crawling,
                disabled=SitesCrawlerState.running
            ),
            add_site_button(),
            rx.spacer(),
            rx.button(
                rx.cond(JobsCrawlerState.running,
                        rx.spinner(loading=True),
                        rx.icon("briefcase", size=26), ),
                rx.text("Scan Jobs", size="4", display=[
                    "none", "none", "block"]),
                size="3",
                on_click=JobsCrawlerState.start_crawling,
                disabled=JobsCrawlerState.running
            ),
            rx.hstack(
                rx.cond(
                    SitesState.sort_reverse,
                    rx.icon("arrow-up-z-a", size=28, stroke_width=1.5, cursor="pointer",
                            on_click=SitesState.toggle_sort),
                    rx.icon("arrow-down-a-z", size=28, stroke_width=1.5, cursor="pointer",
                            on_click=SitesState.toggle_sort),
                ),
                rx.select(
                    map(lambda f: f.capitalize(), JobSite.get_fields()),
                    placeholder=f"Sort By: {list(JobSite.get_fields())[0].capitalize()}",
                    on_change=SitesState.set_sort_value
                )
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
                    _header_cell("Website", "link"),
                    _header_cell("Last Scanned", "refresh-cw"),
                    _header_cell("Jobs", "briefcase"),
                    _header_cell("Actions", "cog"),
                ),
            ),
            rx.table.body(rx.foreach(
                SitesState.sites,
                show_site
            )),
            variant="surface",
            size="3",
            width="100%",
            on_mount=SitesState.load_sites,
        ),
    )
