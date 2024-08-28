import logging.config
import sys

import crochet
import reflex as rx
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet.pollreactor import install

from .backend.data import SitesState, JobState, JobsState
from .components.stats_cards import stats_cards_group
from .views import jobs_view
from .components.navbar import navbar
from .views import sites_view


@rx.page(route="/", title="Job Management App", on_load=[JobsState.load_jobs])
def index() -> rx.Component:
    return rx.vstack(
        navbar(),
        stats_cards_group(),
        rx.box(
            sites_view.main_table(),
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route="/jobs", title="Job Site", on_load=[JobState.update_current_site, JobState.load_jobs])
def jobs() -> rx.Component:
    return rx.vstack(
        navbar(True),
        rx.flex(
            jobs_view.header(),
            jobs_view.cards(),
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

if "twisted.internet.reactor" not in sys.modules:
    configure_logging(get_project_settings(), install_root_handler=False)
    logging.config.dictConfig(get_project_settings()['LOGGING'])
    install()
    crochet.setup()
