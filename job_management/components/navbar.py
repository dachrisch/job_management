import reflex as rx

from job_management.backend.state.cv import CvState
from job_management.backend.state.google import GoogleState
from job_management.backend.state.openai_key import OpenaiKeyState


def options_menu():
    return rx.hstack(
        rx.cond(GoogleState.is_logged_in, profile_options()),
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    'Add OpenAI API Key',
                    weight='bold',
                    margin='0', ),
                rx.dialog.description('Please enter your OpenAI API key',
                                      size="2",
                                      margin_bottom="16px", ),
                rx.flex(
                    rx.input(placeholder='sk-...', name='openai_api_key',
                             value=OpenaiKeyState.openai_key, on_change=OpenaiKeyState.new_openai_key),
                    rx.cond(OpenaiKeyState.key_validation_error,
                            rx.callout(OpenaiKeyState.key_validation_error, icon='triangle_alert')),
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
                        on_click=OpenaiKeyState.cancel_dialog,
                    ),
                    rx.button("Validate",
                              loading=OpenaiKeyState.is_validating_key,
                              on_click=OpenaiKeyState.validate_key),
                    rx.dialog.close(
                        rx.button("Save", disabled=~OpenaiKeyState.is_valid_key,
                                  on_click=OpenaiKeyState.save_dialog,
                                  )
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
            ),
            open=OpenaiKeyState.openai_key_dialog_open
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


def profile_options():
    return rx.menu.root(
        rx.menu.trigger(
            rx.icon_button(rx.avatar(src=GoogleState.profile_picture), color='inherit', background='transparent'),
        ),
        rx.menu.content(
            rx.menu.item(GoogleState.profile_email, disabled=True),
            rx.menu.separator(),
            rx.menu.item("Enter OpenAI API Key", on_click=OpenaiKeyState.toggle_openai_key_dialog_open),
            rx.menu.separator(),
            rx.menu.item(rx.hstack(rx.icon('log-out', size=18), rx.text('Logout')),
                         on_click=GoogleState.logout,
                         color_scheme='red'),
        ),
        align='center'
    )


def navbar_icons_item(
        text: str, icon: str, url: str
) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4", weight="medium"),
        ),
        href=url,
    )


def navbar_icons_menu_item(
        text: str, icon: str, url: str
) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=16),
            rx.text(text, size="3", weight="medium"),
        ),
        href=url,
    )


def navbar(back_link: rx.Var = rx.Var.create('')):
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.icon('briefcase', color="var(--accent-10)"),
                    rx.heading(
                        "Job Management", size="7", weight="bold",
                    ),
                    align_items="center",
                    on_click=rx.redirect('/')
                ),
                rx.hstack(
                    navbar_icons_item("Sites", "building", "/sites"),
                    navbar_icons_item("Jobs", "briefcase", "/jobs"),
                    navbar_icons_item("Applications", "notebook-pen", "/applications"),
                    rx.spacer(),
                    options_menu(),
                    rx.color_mode.button(),
                    spacing="6",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    rx.icon('briefcase', size=30),
                    rx.heading(
                        "Job Management", size="6", weight="bold"
                    ),
                    align_items="center",
                ),
                rx.spacer(),
                options_menu(),
                rx.color_mode.button(),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.icon("menu", size=30)
                    ),
                    rx.menu.content(
                        navbar_icons_menu_item(
                            "Sites", "building", "/sites"
                        ),
                        navbar_icons_menu_item(
                            "Jobs", "briefcase", "/jobs"
                        ),
                        navbar_icons_menu_item(
                            "Applications", "notebook-pen", "/applications"
                        ),
                    ),
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        # position="fixed",
        # top="0px",
        border_radius="20px",

        z_index="5",
        width="100%",
    )
