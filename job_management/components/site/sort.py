import reflex as rx

from job_management.backend.entity.site import JobSite
from job_management.backend.state.sites import SitesState


def sort_options():
    return rx.hstack(
        rx.cond(
            SitesState.sort_reverse,
            rx.icon("arrow-up-z-a", size=28, stroke_width=1.5, cursor="pointer",
                    on_click=SitesState.toggle_sort),
            rx.icon("arrow-down-a-z", size=28, stroke_width=1.5, cursor="pointer",
                    on_click=SitesState.toggle_sort),
        ),
        rx.select.root(
            rx.select.trigger(),
            rx.select.content(
                rx.select.group(
                    *[rx.select.item(model_field.field_info.title or field_key, value=field_key) for
                      field_key, model_field in JobSite.sortable_fields()],
                ),

            ),
            default_value=SitesState.sort_value,
            on_change=SitesState.change_sort_value
        ),
        justify='center'
    )
