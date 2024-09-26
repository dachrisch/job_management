import reflex as rx

from job_management.backend.state.refinement import RefinementState


def refinement_dialog():
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title('Prompt Refinements'),
            rx.dialog.description('Enter the prompt to refine the application generation',
                                  size="2",
                                  margin_bottom="16px", ),
            rx.flex(
                rx.text_area(placeholder='Your prompt refinements', name='prompt_refinement',
                             value=RefinementState.prompt, on_change=RefinementState.new_prompt),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        color_scheme="gray",
                        variant="soft",
                    ),
                    on_click=RefinementState.cancel_dialog,
                ),
                rx.dialog.close(
                    rx.button("Save"),
                    on_click=RefinementState.save_dialog,
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=RefinementState.refinement_open
    )
