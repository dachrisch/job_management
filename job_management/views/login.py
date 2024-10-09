import functools

import reflex as rx

from job_management.backend.state.google import GoogleState
from job_management.components.navbar import navbar


@rx.page(route='/login', title='Login',
         on_load=[])
def login() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.vstack(rx.callout('Please login with your Google Account to use this service', icon='info'),
                  rx.button('Login to Google', on_click=GoogleState.login_flow,
                            loading=GoogleState.is_running_flow),
                  align="center"
                  ),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


def require_google_login(page) -> rx.Component:
    @functools.wraps(page)
    def _auth_wrapper() -> rx.Component:
        return rx.cond(
            GoogleState.is_hydrated, rx.cond(GoogleState.is_logged_in, page(), login()), rx.spinner()
        )

    return _auth_wrapper
