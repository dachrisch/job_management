import reflex as rx
from reflex import Var
from reflex.components.radix.themes.base import LiteralAccentColor


def card(icon: str, icon_color: LiteralAccentColor, title: str, link: str, subtitle: rx.Component = None,
         *actions: rx.Component,
         badge: Var[str] = Var[str].create('')):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag=icon, size=40),
                    color_scheme=icon_color,
                    radius="full",
                    padding="0.7rem",
                ),
                rx.vstack(rx.heading(
                    title,
                    size="6",
                    weight="bold",
                ),
                    rx.text(subtitle or rx.text(''),
                            as_='div',
                            color=rx.color("gray", 10),
                            ),
                    spacing="1",
                ),
                rx.spacer(),
                actions,
                spacing="1",
                height="100%",
                align_items="start",
                width="100%",
            ),
            rx.hstack(
                rx.link(
                    link,
                    href=link,
                    target='_blank',
                    size="2",
                    color=rx.color("gray", 10),
                ),
                align="center",
                align_items='start',
                width="100%",
            ),
            rx.cond(badge, rx.badge(
                rx.icon('circle-check', size=18),
                badge),
                    ),
            spacing="3",
        ),
        size="3",
        width="100%",
    )
