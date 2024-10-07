import asyncio

import reflex as rx

from . import wire, setup_scrapy
from .backend.state.application import ApplicationState
from .backend.state.cv import CvState
from .backend.state.job import JobState
from .backend.state.openai_key import OpenaiKeyState
from .backend.state.statistics import JobsStatisticsState
from .components.navbar import navbar
from .views import jobs_view, application_view
from .views import sites_view
from .views.sites_view import stats_cards_group


@rx.page('/', on_load=rx.redirect('/sites'))
def index() -> rx.Component:
    return rx.heading('redirecting...')


@rx.page(route="/sites", title="Sites", on_load=[JobsStatisticsState.load_jobs_statistic])
def sites() -> rx.Component:
    return rx.vstack(
        navbar(),
        stats_cards_group(),
        rx.box(
            sites_view.main_table(),
            width="100%",
        ),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route="/jobs", title="Jobs",
         on_load=[JobState.update_current_site, JobState.load_jobs, JobsStatisticsState.load_jobs_statistic])
def jobs() -> rx.Component:
    return rx.vstack(
        navbar(rx.Var.create('/', _var_is_string=True)),
        jobs_view.render(),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route='/applications', title='Applications',
         on_load=[ApplicationState.load_current_job_offer, CvState.load_cv, OpenaiKeyState.inform_openai_api_key])
def applications() -> rx.Component:
    return rx.vstack(
        navbar(f'/jobs/?site={ApplicationState.job_offer.site_url}'),
        application_view.render(),
        width="100%",
        spacing="6",
        align="center",
        padding_x=["1.5em", "1.5em", "3em"],
    )


class GoogleTaskState(rx.State):
    is_running: bool = False
    is_logged_in: bool = False
    num: int = 0

    @rx.background
    async def task_with_login(self):
        async with self:
            self.is_running = True
            self.is_logged_in = False
            self.num = 0

        rx.button('Login', on_click=GoogleTaskState.task_with_login, loading=GoogleTaskState.is_running)

        if not self.is_logged_in:
            print('not logged in')
            yield rx.redirect('/google_login_callback', external=True)

            while not self.is_logged_in:
                async with self:
                    self.num += 1
                yield
                await asyncio.sleep(1)
                print('waiting for login...')

        async with self:
            self.is_running = False
            print('finished')

    @rx.background
    async def on_callback1(self):
        print('logging in...')
        yield
        await asyncio.sleep(6)
        print('Logged in')
        async with self:
            self.is_logged_in = True


@rx.page(route='/google_login', title='Google Login',
         on_load=[])
def google_login() -> rx.Component:
    return rx.vstack(
        rx.text(GoogleTaskState.num),
        rx.button('Login', on_click=GoogleTaskState.task_with_login, loading=GoogleTaskState.is_running))


@rx.page(route='/google_login_callback', title='Google Login Callback',
         on_load=GoogleTaskState.on_callback1)
def google_login_callback() -> rx.Component:
    return rx.button('close', on_click=GoogleTaskState.on_callback1)


app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, radius="large", accent_color="purple"
    ),
)

wire()

setup_scrapy()
