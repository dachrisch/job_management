import reflex as rx


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
