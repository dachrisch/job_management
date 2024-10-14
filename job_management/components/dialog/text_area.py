from typing import Optional

import reflex as rx
from reflex.event import EventSpec


class TextAreaDialog(rx.ComponentState):
    value: str = ''

    @classmethod
    def get_component(cls, trigger: str = '', title: str = '', icon: str = '', description: str = '', value: str = '',
                      placeholder: str = '', form_field: str = '',
                      on_submit: Optional[EventSpec] = None, *children, **props) -> rx.Component:
        cls.value = value
        return rx.dialog.root(
            rx.dialog.trigger(rx.button(rx.icon(icon), rx.text(trigger))),
            rx.dialog.content(
                rx.dialog.title(title),
                rx.dialog.description(description,
                                      size="2",
                                      margin_bottom="16px", ),
                rx.form.root(
                    rx.flex(
                        rx.text_area(placeholder=placeholder, name=form_field,
                                     value=cls.value, on_change=cls.set_value),
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
                    on_submit=on_submit
                ),

            ),
        )
