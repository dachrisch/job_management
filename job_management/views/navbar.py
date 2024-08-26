import reflex as rx


def navbar(back_button: bool = False):
    elements = [
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
            align="center",
            spacing="3",
        ),
    ]
    if back_button:
        elements.insert(0,
                        rx.icon_button(
                            rx.icon("arrow-left", size=22),
                            on_click=rx.redirect(f'/'),
                            size="2",
                            variant="ghost",
                        ))

    return rx.flex(
        *elements,
        spacing="2",
        flex_direction=["column", "column", "row"],
        align="center",
        width="100%",
        top="0px",
        padding_top="2em",
    )
