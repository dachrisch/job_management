import reflex as rx

from job_management.backend.entity import JobOffer
from job_management.backend.job import JobState
from job_management.components.card import card


def header():
    return card('building', 'green', JobState.current_site.title, JobState.current_site.url)


def cards():
    return rx.grid(
        rx.foreach(JobState.jobs, job_card
                   ),
        gap="1rem",
        grid_template_columns=[
            "1fr",
            "repeat(1, 1fr)",
            "repeat(2, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
        ],
        width="100%", )


def job_card(j: JobOffer):
    return rx.container(
        card('briefcase', 'yellow', j.title, j.url,
             rx.vstack(apply_button(j), hide_button(j))),
        opacity=rx.cond(j.seen, 0.5, 1)
    )


def apply_button(j: JobOffer):
    return rx.button(
        rx.icon('mail-plus'),
        on_click=rx.redirect(f'/application?job={j.url}')
    )


def hide_button(j: JobOffer):
    return rx.cond(j.seen,
                   rx.button(
                       rx.icon('eye-off'),
                       disabled=True
                   ),
                   rx.button(
                       rx.icon('eye-off'),
                       on_click=JobState.hide_job(j)
                   )
                   )
