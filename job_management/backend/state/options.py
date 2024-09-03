import os

import reflex as rx
from more_itertools import first


class OptionsState(rx.State):
    openai_key: str = os.getenv('OPENAI_API_KEY')
    openai_key_dialog_open: bool = False
    load_cv_data_open: bool = False

    cv_data: str = ''
    has_cv_data: bool = False

    def toggle_openai_key_dialog_open(self):
        self.openai_key_dialog_open = not self.openai_key_dialog_open

    def new_openai_key(self, form_data: dict):
        openai_key = form_data.get('openai_api_key')
        print(form_data)
        if openai_key:
            self.openai_key = openai_key
        self.toggle_openai_key_dialog_open()

    def toggle_load_cv_data_open(self):
        self.load_cv_data_open = not self.load_cv_data_open

    async def new_cv_data(self, cv_files: list[rx.UploadFile]):
        cv_file = first(cv_files, None)
        if cv_file:
            self.cv_data = (await cv_file.read()).decode('utf-8')
            self.has_cv_data = True
        self.toggle_load_cv_data_open()
