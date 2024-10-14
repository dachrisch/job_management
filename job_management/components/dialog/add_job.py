import reflex as rx

from job_management.backend.state.job import JobState


def add_job_dialog():
    return rx.dialog.root(
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
    )
