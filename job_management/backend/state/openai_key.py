import os

import reflex as rx

from job_management.backend.state.application import ApplicationState


class OpenaiKeyState(rx.State):
    openai_key: str = os.getenv('OPENAI_API_KEY')
    _new_key: str = ''
    openai_key_dialog_open: bool = False

    def toggle_openai_key_dialog_open(self):
        self.openai_key_dialog_open = not self.openai_key_dialog_open

    async def new_openai_key(self, new_key: str):
        self._new_key = new_key

    async def inform_openai_api_key(self):
        if self.openai_key:
            (await self.get_state(ApplicationState)).set_openai_api_key(self.openai_key)

    def cancel_dialog(self):
        self.toggle_openai_key_dialog_open()

    async def save_dialog(self):
        self.openai_key = self._new_key
        self.toggle_openai_key_dialog_open()
        await self.inform_openai_api_key()
