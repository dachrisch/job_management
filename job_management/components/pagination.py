from typing import Type

import reflex as rx

from job_management.backend.state.pagination import PaginationState


def pagination(pagination_state: Type[PaginationState]):
    return rx.hstack(
        rx.button(
            rx.icon('arrow-left-from-line'),
            disabled=pagination_state.at_beginning,
            on_click=pagination_state.first_page
        ),
        rx.button(
            rx.icon('arrow-left'),
            disabled=pagination_state.at_beginning,
            on_click=pagination_state.prev_page
        ),
        rx.text(
            f'Page {pagination_state.page + 1} / {pagination_state.total_pages}'
        ),
        rx.button(
            rx.icon('arrow-right'),
            disabled=pagination_state.at_end,
            on_click=pagination_state.next_page
        ),
        rx.button(
            rx.icon('arrow-right-from-line'),
            disabled=pagination_state.at_end,
            on_click=pagination_state.last_page
        ),
    )
