import reflex as rx


class RefinementState(rx.State):
    prompt: str = ''
    _new_prompt: str = ''
    refinement_open: bool = False
    has_prompt: bool = False

    def toggle_dialog(self):
        self.refinement_open = not self.refinement_open

    def new_prompt(self, new_prompt: str):
        self._new_prompt = new_prompt

    def cancel_dialog(self):
        self.toggle_dialog()

    def save_dialog(self):
        self.prompt = self._new_prompt
        self.has_prompt = self.prompt is not None and self.prompt != ''
        self.toggle_dialog()
