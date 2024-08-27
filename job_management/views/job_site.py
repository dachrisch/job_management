import reflex as rx
from reflex.components.radix.themes.base import LiteralAccentColor

from job_management.backend.data import SiteState, JobsState


def header():
    return card('building', 'green', SiteState.current_site.title, SiteState.current_site.url)


def card(icon: str, icon_color: LiteralAccentColor, title: str, link: str):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag=icon, size=34),
                    color_scheme=icon_color,
                    radius="full",
                    padding="0.7rem",
                ),
                rx.vstack(
                    rx.heading(
                        title,
                        size="6",
                        weight="bold",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                    width="100%",
                ),
                height="100%",
                spacing="4",
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.link(
                    link,
                    href=link,
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


def cards():
    return rx.grid(
        rx.foreach(JobsState.jobs, lambda j: card('briefcase', 'yellow', j.title, j.url)),
        gap="1rem",
        grid_template_columns=[
            "1fr",
            "repeat(1, 1fr)",
            "repeat(2, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
        ],
        width="100%", )
