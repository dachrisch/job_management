import reflex as rx

from . import wire, setup_scrapy
from .backend.state.application import ApplicationState
from .backend.state.cv import CvState
from .backend.state.google import GoogleState
from .backend.state.job import JobState
from .backend.state.openai_key import OpenaiKeyState
from .backend.state.sites import SitesState
from .backend.state.statistics import JobsStatisticsState
from .components.navbar import navbar
from .views import jobs_view, application_view
from .views import sites_view
from .views.login import require_google_login
from .views.sites_view import stats_cards_group


@rx.page('/', on_load=rx.redirect('/sites'))
def index() -> rx.Component:
    return rx.heading('redirecting...')


def footer():
    return rx.el.footer(
        rx.flex(
            rx.spacer(),
            rx.text('Made in 🥨 with ♥️', weight="light"),
            rx.spacer(),
            align='center',
            width='100%')
    )


@rx.page(route="/sites", title="Sites",
         on_load=[JobsStatisticsState.load_jobs_statistic, GoogleState.load_credentials_from_store,
                  SitesState.load_sites])
@require_google_login
def sites() -> rx.Component:
    return rx.vstack(
        navbar(),
        stats_cards_group(),
        rx.box(
            sites_view.main_table(),
            width="100%",
        ),
        footer(),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route="/jobs", title="Jobs",
         on_load=[JobState.update_current_site, JobState.load_jobs, JobsStatisticsState.load_jobs_statistic,
                  GoogleState.load_credentials_from_store])
@require_google_login
def jobs() -> rx.Component:
    return rx.vstack(
        navbar(rx.Var.create('/')),
        jobs_view.render(),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route='/applications', title='Applications',
         on_load=[ApplicationState.load_current_job_offer, CvState.load_cv, OpenaiKeyState.validate_key,
                  GoogleState.load_credentials_from_store])
@require_google_login
def applications() -> rx.Component:
    return rx.vstack(
        navbar(f'/jobs/?site={ApplicationState.job_offer.site_url}'),
        application_view.render(),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route='/google_callback', on_load=GoogleState.on_login_callback)
def google_login_callback() -> rx.Component:
    return rx.text(f'Logged_in: {GoogleState.is_logged_in}')


app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, radius="large", accent_color="purple"
    ),
)

wire()

setup_scrapy()
