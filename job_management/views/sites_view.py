import reflex as rx

from ..backend.crawl import JobsCrawlerState
from ..backend.entity.site import JobSite
from ..backend.state.sites import SitesState
from ..backend.state.statistics import JobsStatisticsState
from ..components.add_site_button import add_site_button, add_jobs_button
from ..components.crawl_button import crawl_eu_sites_button
from ..components.icon_button import icon_button
from ..components.stats_cards import stats_card
from ..components.table import header_cell


def show_site(site: JobSite):
    return rx.table.row(
        rx.table.cell(site.title),
        rx.table.cell(rx.link(site.url, href=site.url, target='_blank')),
        rx.table.cell(rx.cond(site.last_scanned, rx.moment(site.last_scanned, from_now=True), rx.text('Never'))),
        rx.table.cell(
            rx.button(rx.hstack(rx.text(site.jobs.unseen), rx.text(' / '), rx.text(site.jobs.total)),
                      on_click=rx.redirect(f'/jobs/?site={site.url}'),
                      size="2",
                      variant="solid")
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon('refresh-cw'),
                    loading=site.status.crawling,
                    on_click=lambda: SitesState.start_crawl(site)
                ),
                icon_button('eraser', SitesState.clear_jobs(site), site.status.clearing, 'yellow'),
                rx.button(
                    rx.icon('trash-2'),
                    loading=site.status.deleting,
                    on_click=lambda: SitesState.delete_site(site),
                    color_scheme='red'
                )
            )),
        style={"_hover": {"bg": rx.color("gray", 3)}},
        align="center",
    )


def main_table():
    return rx.fragment(
        rx.flex(
            rx.hstack(
                add_site_button(),
                add_jobs_button(),
                crawl_eu_sites_button(),
                rx.spacer(),
                pagination(),
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
                        on_change=SitesState.change_sort_value
                    ),
                    justify='center'
                ),
                spacing="3",
                wrap="wrap",
                width="100%",
                padding="1em",
                align="center"
            )
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    header_cell("Site", "building"),
                    header_cell("Website", "link"),
                    header_cell("Last Scanned", "refresh-cw"),
                    header_cell("Jobs", "briefcase"),
                    header_cell("Actions", "cog"),
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


def pagination():
    return rx.hstack(
        rx.button(
            rx.icon('arrow-left-from-line'),
            disabled=SitesState.at_beginning,
            on_click=SitesState.first_page
        ),
        rx.button(
            rx.icon('arrow-left'),
            disabled=SitesState.at_beginning,
            on_click=SitesState.prev_page
        ),
        rx.text(
            f'Page {SitesState.page + 1} / {SitesState.total_pages}'
        ),
        rx.button(
            rx.icon('arrow-right'),
            disabled=SitesState.at_end,
            on_click=SitesState.next_page
        ),
        rx.button(
            rx.icon('arrow-right-from-line'),
            disabled=SitesState.at_end,
            on_click=SitesState.last_page
        ),
    )


def stats_cards_group() -> rx.Component:
    return rx.flex(
        stats_card(
            'Total Websites',
            SitesState.num_sites,
            SitesState.num_sites_yesterday,
            "building",
            "blue",
        ),
        stats_card(
            'Total Jobs',
            JobsStatisticsState.num_jobs,
            JobsStatisticsState.num_jobs_yesterday,
            "briefcase",
            "blue",
        ),
        spacing="5",
        width="100%",
        wrap="wrap",
        display=["none", "none", "flex"],
    )
