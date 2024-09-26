from typing import Callable

import reflex as rx


def item(step: str, icon: str = 'play', disabled: bool = False, required=True, in_progress=False,
         complete: bool = False,
         process_callback: Callable = None,
         view_callback: Callable[[], rx.Component] = lambda: rx.text('')):
    return rx.hstack(
        rx.button(
            rx.icon(icon),
            variant=rx.cond(required & ~complete, '', 'surface'),
            disabled=disabled,
            on_click=process_callback,
            loading=in_progress
        ),
        rx.cond(complete, rx.icon('circle-check-big'), rx.cond(required, rx.icon('circle'), rx.icon('circle-dashed'))),
        rx.text(step, size="4"),
        rx.spacer(),

        rx.cond(complete,
                rx.popover.root(
                    rx.popover.trigger(
                        rx.button(
                            rx.icon('ellipsis'),
                        ),
                    ),
                    rx.popover.content(
                        view_callback(),
                        style={"max-width": 500, 'max-height': 400},
                    )

                ),
                rx.button(rx.icon('ellipsis'), disabled=True)
                ),
        width='100%',
        align='center',

    )
