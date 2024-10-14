from typing import Literal, Callable, Union, Optional, Coroutine

import reflex as rx
from reflex import Var
from reflex.components.lucide.icon import LUCIDE_ICON_LIST
from reflex.event import EventSpec, EventHandler


def icon_button(icon_name: Literal[tuple(LUCIDE_ICON_LIST)],
                on_click_handler: Union[EventHandler, EventSpec, list, Callable, Coroutine],
                is_loading: Union[bool, Var[bool]] = False,
                color_scheme: Optional[
                    Union[
                        Var[
                            Literal[
                                "tomato",
                                "red",
                                "ruby",
                                "crimson",
                                "pink",
                                "plum",
                                "purple",
                                "violet",
                                "iris",
                                "indigo",
                                "blue",
                                "cyan",
                                "teal",
                                "jade",
                                "green",
                                "grass",
                                "brown",
                                "orange",
                                "sky",
                                "mint",
                                "lime",
                                "yellow",
                                "amber",
                                "gold",
                                "bronze",
                                "gray",
                            ]
                        ],
                        Literal[
                            "tomato",
                            "red",
                            "ruby",
                            "crimson",
                            "pink",
                            "plum",
                            "purple",
                            "violet",
                            "iris",
                            "indigo",
                            "blue",
                            "cyan",
                            "teal",
                            "jade",
                            "green",
                            "grass",
                            "brown",
                            "orange",
                            "sky",
                            "mint",
                            "lime",
                            "yellow",
                            "amber",
                            "gold",
                            "bronze",
                            "gray",
                        ],
                    ]
                ] = None):
    return rx.button(
        rx.icon(icon_name),
        loading=is_loading,
        on_click=on_click_handler,
        color_scheme=color_scheme
    )
