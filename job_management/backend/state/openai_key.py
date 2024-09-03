import os

import reflex as rx

from job_management.backend.state.application import ApplicationState


class OpenaiKeyState(rx.State):
    openai_key: str = os.getenv('OPENAI_API_KEY')
    openai_key_dialog_open: bool = False

    def toggle_openai_key_dialog_open(self):
        self.openai_key_dialog_open = not self.openai_key_dialog_open

    async def new_openai_key(self, form_data: dict):
        openai_key = form_data.get('openai_api_key')
        print(form_data)
        if openai_key:
            self.openai_key = openai_key
            await self.inform_openai_api_key()
        self.toggle_openai_key_dialog_open()

    async def inform_openai_api_key(self):
        if self.openai_key:
            (await self.get_state(ApplicationState)).set_openai_api_key(self.openai_key)
