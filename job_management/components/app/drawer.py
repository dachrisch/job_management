from typing import Optional, Union, Dict, Any

import reflex as rx
from reflex import Var
from reflex.event import EventType

from job_management.backend.state.add_jobs import AddJobsState


def drawer_dialog(icon: str, entry_title: str, entry_description: str,
                  dialog_is_submitting: Optional[Union[Var[bool], bool]],
                  dialog_on_submit: Optional[EventType[Dict[str, Any]]],
                  dialog_fields: list[Dict[str, str]]) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(drawer_entry(icon, entry_title, entry_description)),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(icon, size=34),
                    color_scheme="grass",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        entry_title,
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        entry_description
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
                        *[rx.form.field(
                            rx.flex(
                                rx.hstack(
                                    rx.icon(icon, size=16, stroke_width=1.5),
                                    rx.form.label(field['label']),
                                    align="center",
                                    spacing="2",
                                ),
                                rx.form.control(
                                    rx.input(
                                        placeholder=field['placeholder']
                                    ),
                                    as_child=True,
                                ),
                                direction="column",
                                spacing="1",
                            ),
                            name=field['name'],
                            width="100%",
                        ) for field in dialog_fields],
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
                                rx.button("Submit", loading=dialog_is_submitting),
                            ),
                            as_child=True,
                        ),
                        padding_top="2em",
                        spacing="3",
                        mt="4",
                        justify="end",
                    ),
                    on_submit=dialog_on_submit,
                )
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1.5em",
            border=f"2px solid {rx.color('accent', 7)}",
            border_radius="25px",
        ),
    )


def drawer_entry(icon: str, entry_title: str, entry_description: str):
    return rx.hstack(
        rx.icon(icon, size=40),
        rx.vstack(
            rx.text.strong(entry_title),
            rx.text(entry_description),
            spacing='1'
        ),
        align='center',
    )


def add_drawer():
    return rx.drawer.root(
        rx.drawer.trigger(rx.icon("plus")),
        rx.drawer.overlay(z_index="5"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.box(
                    rx.vstack(
                        drawer_dialog(
                            icon='briefcase', entry_title='Add Job',
                            entry_description='Add a job from URL',
                            dialog_on_submit=AddJobsState.add_job,
                            dialog_is_submitting=AddJobsState.loading,
                            dialog_fields=[{'name': 'job_url', 'label': 'Job URL', 'placeholder': 'Enter job url'}]

                        ),
                        drawer_entry(icon='copy-plus', entry_title='Add Jobs',
                                     entry_description='Add a multiple jobs from URL', ),
                        drawer_entry(icon='building', entry_title='Add Site',
                                     entry_description='Add a new job site for discovery', ),
                    ),
                    align_items="start",
                    direction="column",
                ),
                top="auto",
                width="100%",
                heigth="20em",
                border_top_right_radius="20px",
                border_top_left_radius="20px",
                background_color=rx.color("accent", 3),
                padding="2em",
            )
        ),
        direction="bottom",
    )
