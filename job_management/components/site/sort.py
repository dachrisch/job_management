from typing import Tuple, Iterable

import reflex as rx
from pydantic.v1.fields import ModelField

from job_management.backend.entity.site import JobSite
from job_management.backend.state.sites import SitesState
from job_management.backend.state.sorting import SortableState


def sort_options(sortable_state:type[SortableState], sortable_fields:Iterable[Tuple[str, ModelField]]):
    return rx.hstack(
        rx.cond(
            sortable_state.sort_reverse,
            rx.icon("arrow-up-z-a", size=28, stroke_width=1.5, cursor="pointer",
                    on_click=sortable_state.toggle_sort),
            rx.icon("arrow-down-a-z", size=28, stroke_width=1.5, cursor="pointer",
                    on_click=sortable_state.toggle_sort),
        ),
        rx.select.root(
            rx.select.trigger(),
            rx.select.content(
                rx.select.group(
                    *[rx.select.item(model_field.field_info.title or field_key, value=field_key) for
                      field_key, model_field in sortable_fields],
                ),

            ),
            default_value=sortable_state.sort_value,
            on_change=sortable_state.change_sort_value
        ),
        justify='center'
    )
