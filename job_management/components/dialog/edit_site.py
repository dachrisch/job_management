import reflex as rx

from job_management.backend.state.job import JobState
from job_management.components.editable_input import EditableInput


def edit_site_dialog():
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon('pencil'), rx.text('Edit Site'))),
        rx.dialog.content(
            rx.dialog.title('Edit Job Site'),

            rx.form.root(
                rx.flex(
                    rx.text(
                        'Site Title',
                        as_="div",
                        size="2",
                        margin_bottom="4px",
                        weight="bold",
                    ),
                    EditableInput.create(
                        name='site_title',
                        placeholder="Site title...",
                        initial_value=JobState.current_site.title
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
                            rx.button("Save"),
                        ),
                        as_child=True,
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
                on_submit=JobState.on_submit_edit_site
            ),
        ),
    )
