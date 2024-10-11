import reflex as rx

from job_management.backend.state.job import JobState
from job_management.backend.state.statistics import JobsStatisticsState
from job_management.components.job.cards import cards
from job_management.components.job.dialog import add_job_dialog
from job_management.components.job.table import jobs_table
from job_management.components.stats_cards import stats_card


def render() -> rx.Component:
    return rx.cond(JobState.current_site.url, render_site_jobs(), render_all_jobs())


def render_all_jobs() -> rx.Component:
    return rx.flex(
        rx.vstack(
            stats_card(
                'Total Jobs',
                JobsStatisticsState.num_jobs,
                JobsStatisticsState.num_jobs_yesterday,
                "briefcase",
                "blue",
            ),
            jobs_table(),
            width="100%",
            spacing="6",
            align="center",
            padding_x=["1.5em", "1.5em", "3em"],
        ),
        spacing="5",
        width="100%",
        wrap="wrap",
    )


def render_site_jobs() -> rx.Component:
    return rx.flex(
        header(),
        cards(),
        spacing="5",
        width="100%",
        wrap="wrap",
        display=["column", "column", "flex"],
    )


def header() -> rx.Component:
    return rx.container(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        rx.icon(tag='building', size=34),
                        radius="full",
                        padding="0.7rem",
                    ),
                    rx.heading(
                        JobState.current_site.title,
                        size="6",
                        weight="bold",
                    ),
                    rx.spacer(),
                    add_job_dialog(),
                    spacing="1",
                    height="100%",
                    align_items="start",
                    width="100%",
                ),
                rx.hstack(
                    rx.link(
                        JobState.current_site.url,
                        href=JobState.current_site.url,
                        target='_blank',
                        size="2",
                        color=rx.color("gray", 10),
                    ),
                    align="center",
                    align_items='start',
                    width="100%",
                ),
                spacing="3",
            ),
            size="3",
            width="100%",
        )
    )
