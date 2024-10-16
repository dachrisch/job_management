import logging

import reflex as rx

from job_management.backend.service.locator import Locator


class GoogleState(rx.State):
    is_running_flow: bool = False
    credentials_store = rx.LocalStorage(name='credentials')

    @property
    def log(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @rx.background
    async def login_flow(self):
        async with self:
            self.is_running_flow = True

        auth_url = Locator.google_credentials_service.auth_url(self.router.page.host + '/google_callback',
                                                               self.router.session.client_token)
        self.log.info(f'redirecting to {auth_url}')
        yield rx.redirect(auth_url)

        async with self:
            self.is_running_flow = False

    @rx.var
    def is_logged_in(self):
        return Locator.google_credentials_service.has_valid_credentials

    def on_login_callback(self):
        Locator.google_credentials_service.authorize_code(self.router.page.params.get('code'),
                                                          self.router.page.host + '/google_callback',
                                                          self.router.session.client_token)
        if self.is_logged_in:
            self.credentials_store = Locator.google_credentials_service.credentials.to_json()
        return rx.redirect('/')

    def load_credentials_from_store(self):
        if not Locator.google_credentials_service.has_valid_credentials:
            Locator.google_credentials_service.load_from_json(self.credentials_store)
            if Locator.google_credentials_service.has_valid_credentials:
                return rx.redirect('/')

    def logout(self):
        Locator.google_credentials_service.clear_credentials()
        return rx.remove_local_storage('credentials')

    @rx.var
    def profile_picture(self) -> str:
        if self.is_logged_in:
            return Locator.google_credentials_service.get_user_info()['picture']
        else:
            return ''

    @rx.var
    def profile_email(self) -> str:
        if self.is_logged_in:
            return Locator.google_credentials_service.get_user_info()['email']
        else:
            return ''
