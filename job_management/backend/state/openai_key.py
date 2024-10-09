import os

import reflex as rx

from job_management.backend.api.conversation import Conversation


class OpenaiKeyState(rx.State):
    openai_key: str = os.getenv('OPENAI_API_KEY')
    _new_key: str = os.getenv('OPENAI_API_KEY')
    is_valid_key: bool = False
    is_validating_key: bool = False
    key_validation_error: str = ''
    openai_key_dialog_open: bool = False

    def toggle_openai_key_dialog_open(self):
        self.key_validation_error = ''
        self.openai_key_dialog_open = not self.openai_key_dialog_open

    async def new_openai_key(self, new_key: str):
        self.is_valid_key = False
        self._new_key = new_key

    def cancel_dialog(self):
        self.is_validating_key = False
        self.toggle_openai_key_dialog_open()

    def save_dialog(self):
        self.toggle_openai_key_dialog_open()

    @rx.background
    async def validate_key(self):
        async with self:
            self.is_validating_key = True

        if await Conversation(self._new_key).is_valid_key():
            async with self:
                self.openai_key = self._new_key
                self.is_valid_key = True
        else:
            async with self:
                self.is_valid_key = False
                self.key_validation_error = 'Invalid OpenAI API Key'

        async with self:
            self.is_validating_key = False

