import reflex as rx

from job_management.backend.entity.offer import JobOffer
from job_management.backend.state.job import JobState


def apply_button(j: JobOffer) -> rx.Component:
    return rx.button(
        rx.icon('mail-plus'),
        disabled=rx.cond(j.seen, True, False),
        on_click=rx.redirect(f'/applications?job={j.base64_url}')
    )


def hide_button(j: JobOffer) -> rx.Component:
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
