import reflex as rx

from job_management.components.app.drawer import add_drawer
from job_management.components.navbar import app_logo


def footer():
    return rx.el.footer(
        rx.flex(
            rx.spacer(),
            rx.text('Made in 🥨 with ♥️', weight="light"),
            rx.spacer(),
            align='center',
            width='100%')
    )


def app_view(*children: rx.Component):
    return rx.vstack(
        rx.box(
            rx.hstack(
                app_logo(),
                rx.spacer(),
                add_drawer(),
                spacing="5"
            ),
            z_index="5",
            width='100%',
            padding="1em",
            border_radius="20px",
            bg=rx.color("accent", 3),
        ),
        *children,
        rx.spacer(),
        footer(),
        width="100%",
        height="100vh",
        spacing="6",
        align="center",
        padding='1em'
    )
