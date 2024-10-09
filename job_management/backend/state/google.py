import json

import reflex as rx

from job_management.backend.service.google import GoogleCredentialsService
from job_management.backend.service.locator import Locator


class GoogleState(rx.State):
    is_running_flow: bool = False
    credentials_store = rx.LocalStorage(name='credentials')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials_service: GoogleCredentialsService = Locator.credentials_handler

    @rx.background
    async def login_flow(self):
        async with self:
            self.is_running_flow = True

        yield rx.redirect(self.credentials_service.auth_url(self.router.page.host + '/google_callback',
                                                            next_url=self.router.page.raw_path))

        async with self:
            self.is_running_flow = False

    @rx.var
    def is_logged_in(self):
        return self.credentials_service.has_valid_credentials

    def on_login_callback(self):
        self.credentials_service.authorize_code(self.router.page.params.get('code'))
        if self.is_logged_in:
            self.credentials_store = self.credentials_service.credentials.to_json()
        return rx.redirect(self.router.page.params.get('next_url'))

    def load_credentials_from_store(self):
        self.credentials_service.load_from_json(self.credentials_store)

    def logout(self):
        self.credentials_service.clear_credentials()
        return rx.remove_local_storage('credentials')

    @rx.var
    def user_info(self) -> str:
        if self.is_logged_in:
            return json.dumps(self.credentials_service.get_user_info())
        else:
            return ''

    @rx.var
    def profile_picture(self) -> str:
        if self.is_logged_in:
            return self.credentials_service.get_user_info()['picture']
        else:
            return ''

    @rx.var
    def profile_email(self) -> str:
        if self.is_logged_in:
            return self.credentials_service.get_user_info()['email']
        else:
            return ''
