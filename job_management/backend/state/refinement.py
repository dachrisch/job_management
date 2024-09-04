import reflex as rx


class RefinementState(rx.State):
    prompt: str = ''
    refinement_open: bool = False
    _new_prompt:str=''

    def toggle_dialog(self):
        self.refinement_open = not self.refinement_open

    def new_prompt(self, new_prompt: str):
        self._new_prompt = new_prompt

    def cancel_dialog(self):
        self.toggle_dialog()

    def save_dialog(self):
        self.prompt=self._new_prompt
        self.toggle_dialog()
