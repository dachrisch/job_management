import reflex as rx

from job_management.backend.entity.offer import JobOffer
from job_management.backend.state.job import JobState
from job_management.components.card import card
from job_management.components.job.buttons import apply_button, hide_button


def cards() -> rx.Component:
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


def job_card(j: JobOffer) -> rx.Component:
    state = rx.cond(j.state.analyzed, 'Analyzed', '')
    return rx.container(
        card('briefcase', 'yellow', j.title, j.url,None,
             rx.vstack(apply_button(j), hide_button(j)), badge=state),
        opacity=rx.cond(j.seen, 0.5, 1)
    )
