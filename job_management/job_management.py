import reflex as rx

from .backend.backend import SiteState, JobsState
from .components.stats_cards import stats_cards_group
from .views import job_site
from .views.navbar import navbar
from .views.table import main_table


@rx.page(route="/", title="Job Management App")
def index() -> rx.Component:
    return rx.vstack(
        navbar(),
        stats_cards_group(),
        rx.box(
            main_table(),
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route="/jobs", title="Job Site", on_load=[SiteState.update_current_site, JobsState.load_jobs])
def jobs() -> rx.Component:
    return rx.vstack(
        navbar(True),
        rx.flex(
            job_site.header(),
            job_site.cards(),
            spacing="5",
            width="100%",
            wrap="wrap",
            display=["none", "none", "flex"],
        ),

        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    )


app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="grass"
    ),
)
