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
                    rx.dialog.root(
                        rx.dialog.trigger(rx.button(rx.icon('briefcase'), rx.text("Add Job"))),
                        rx.dialog.content(
                            rx.dialog.title('Add Job Site'),
                            rx.dialog.description(
                                'Add a site belonging to this company',
                                size="2",
                                margin_bottom="16px",
                            ),
                            rx.form.root(
                                rx.flex(
                                    rx.text(
                                        'Job Title',
                                        as_="div",
                                        size="2",
                                        margin_bottom="4px",
                                        weight="bold",
                                    ),
                                    rx.input(
                                        name='job_title',
                                        placeholder="Job title...",
                                    ),
                                    rx.text(
                                        'Url',
                                        as_="div",
                                        size="2",
                                        margin_bottom="4px",
                                        weight="bold",
                                    ),
                                    rx.input(
                                        name='job_url',
                                        placeholder='Site url with job description',
                                    ),
                                    direction="column",
                                    spacing="3",
                                ),
                                rx.flex(
                                    rx.dialog.close(
                                        rx.button(
                                            "Cancel",
                                            color_scheme="gray",
                                            variant="soft",
                                        ),
                                    ),
                                    rx.form.submit(
                                        rx.dialog.close(
                                            rx.button("Add"),
                                        ),
                                        as_child=True,
                                    ),
                                    spacing="3",
                                    margin_top="16px",
                                    justify="end",
                                ),
                                on_submit=JobState.add_job
                            ),
                        ),
                    ),
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
    state = rx.cond(j.state.analyzed, 'Analyzed', '')
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
