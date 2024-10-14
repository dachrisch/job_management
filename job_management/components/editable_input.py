import reflex as rx


class EditableInput(rx.ComponentState):
    value: str = ''

    def on_change(self, new_value: str):
        self.value = new_value

    @classmethod
    def get_component(cls, **props):
        name = props.pop("name", "input_name")
        placeholder = props.pop("placeholder", "")
        initial_value = props.pop("initial_value", '')
        cls.value = initial_value

        return rx.input(
            name=name,
            placeholder=placeholder,
            value=cls.value,
            on_change=cls.on_change
        )
