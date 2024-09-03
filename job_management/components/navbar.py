import reflex as rx

from job_management.backend.state.options import OptionsState, CvState
from job_management.components.form import form_field


def options_menu():
    return rx.hstack(
        rx.menu.root(
            rx.menu.trigger(
                rx.button(rx.icon('cog'), variant="soft"),
            ),
            rx.menu.content(
                rx.menu.item("OpenAI API Key", shortcut="Strg E",
                             on_click=OptionsState.toggle_openai_key_dialog_open),
            ),
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.dialog.title(
                        "Add OpenAI API Key",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Please enter your OpenAI API key",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                rx.flex(
                    rx.form.root(
                        rx.flex(
                            form_field(
                                "OpenAI API Key",
                                "API Key",
                                "text",
                                "openai_api_key",
                                "key",
                            ),

                            direction="column",
                            spacing="3",
                        ),
                        rx.flex(
                            rx.dialog.close(
                                rx.button(
                                    "Cancel",
                                    variant="soft",
                                    color_scheme="gray",
                                ),
                                on_click=OptionsState.toggle_openai_key_dialog_open
                            ),
                            rx.form.submit(
                                rx.dialog.close(
                                    rx.button("Submit"),
                                ),
                                as_child=True,
                            ),
                            padding_top="2em",
                            spacing="3",
                            mt="4",
                            justify="end",
                        ),
                        on_submit=OptionsState.new_openai_key,
                        reset_on_submit=False,
                    ),

                ),
            ),
            open=OptionsState.openai_key_dialog_open,

        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.dialog.title(
                        "Load CV data",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Upload your CV data",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                rx.flex(
                    rx.form.root(
                        rx.flex(
                            rx.upload(
                                rx.text("Upload CV data"), rx.icon(tag="upload"),
                                id="cv_upload",
                                multiple=False,
                                accept={
                                    'text/plain': ['.txt']
                                },
                                max_files=1
                            ),
                            rx.hstack(rx.foreach(rx.selected_files("cv_upload"), rx.text)),
                            direction="column",
                            spacing="3",
                        ),
                        rx.flex(
                            rx.dialog.close(
                                rx.button(
                                    "Cancel",
                                    variant="soft",
                                    color_scheme="gray",
                                ),
                                on_click=CvState.toggle_load_cv_data_open
                            ),
                            rx.form.submit(
                                rx.dialog.close(
                                    rx.button("Submit"),
                                ),
                                as_child=True,
                            ),
                            padding_top="2em",
                            spacing="3",
                            mt="4",
                            justify="end",
                        ),
                        on_submit=CvState.new_cv_data(rx.upload_files(upload_id="cv_upload")),
                        reset_on_submit=False,
                    ),

                ),
            ),
            open=CvState.load_cv_data_open,

        ),
    )


def navbar(back_link: rx.Var = rx.Var.create('', _var_is_string=True)):
    return rx.flex(
        rx.cond(back_link != '',
                rx.icon_button(
                    rx.icon("arrow-left", size=22),
                    on_click=rx.redirect(back_link),
                    size="2",
                    variant="ghost",
                )
                ),
        rx.badge(
            rx.icon(tag="table-2", size=28),
            rx.heading("Job Management App", size="6"),
            color_scheme="green",
            radius="large",
            align="center",
            variant="surface",
            padding="0.65rem",
        ),
        rx.spacer(),
        rx.hstack(
            rx.logo(),
            rx.color_mode.button(),
            options_menu(),
            align="center",
            spacing="3",
        ),

        spacing="2",
        flex_direction=["column", "column", "row"],
        align="center",
        width="100%",
        top="0px",
        padding_top="2em",
    )
