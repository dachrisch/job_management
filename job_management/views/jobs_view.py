import reflex as rx

from job_management.backend.job import JobState
from job_management.components.card import card


def header():
    return card('building', 'green', JobState.current_site.title, JobState.current_site.url)


def cards():
    return rx.grid(
        rx.foreach(JobState.jobs, lambda j: card('briefcase', 'yellow', j.title, j.url, rx.button(
            rx.icon('mail-plus'),
            on_click=rx.redirect(f'/application?job={j.url}')
        ))),
        gap="1rem",
        grid_template_columns=[
            "1fr",
            "repeat(1, 1fr)",
            "repeat(2, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
        ],
        width="100%", )
