import reflex as rx

from job_management.backend.entity.offer import JobOffer
from job_management.backend.state.job import JobState
from job_management.components.card import card


def render():
    return rx.flex(
        header(),
        cards(),
        spacing="5",
        width="100%",
        wrap="wrap",
        display=["column", "column", "flex"],
    ),


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
    state=rx.cond(j.state.analyzed, 'Analyzed', '')
    return rx.container(
        card('briefcase', 'yellow', j.title, j.url,
             rx.vstack(apply_button(j), hide_button(j)), badge=state),
        opacity=rx.cond(j.seen, 0.5, 1)
    )


def apply_button(j: JobOffer):
    return rx.button(
        rx.icon('mail-plus'),
        disabled=rx.cond(j.seen, True, False),
        on_click=rx.redirect(f'/application?job={j.url}')
    )


def hide_button(j: JobOffer):
    return rx.cond(j.seen,
                   rx.button(
                       rx.icon('eye'),
                       on_click=JobState.show_job(j),
                       title='Show Job'
                   ),
                   rx.button(
                       rx.icon('eye-off'),
                       on_click=JobState.hide_job(j),
                       title='Hide Job'
                   )
                   )
