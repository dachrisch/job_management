from typing import Callable

import reflex as rx
from reflex import Style

from job_management.backend.state.application import ApplicationState
from job_management.backend.state.cv import CvState
from job_management.backend.state.refinement import RefinementState
from job_management.components.card import card

# Common styles for questions and answers.
shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
chat_margin = "1em"
message_style = dict(
    padding="1em",
    border_radius="5px",
    margin_y="1em",
    box_shadow=shadow,
    max_width="30em",
    display="inline-block",
)

# Set specific styles for questions and answers.
question_style = message_style | dict(
    margin_left=chat_margin,
    background_color=rx.color("gray", 4),
)
answer_style = message_style | dict(
    margin_right=chat_margin,
    background_color=rx.color("accent", 8),
)

button_style = Style(
    background_color=rx.color("accent", 10),
    box_shadow=shadow,
)


def render():
    return rx.container(
        rx.flex(
            header(),
            rx.vstack(
                process_steps(),
                align='center',
            ),
            spacing="2",
            direction="column",
        ),
    )


def header():
    return rx.vstack(
        card(
            'briefcase',
            'green',
            ApplicationState.job_offer.title,
            ApplicationState.job_offer.url,
        ),
        align='center'
    )


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


def process_steps():
    return rx.card(
        rx.vstack(
            item('Analyse',
                 'search-code',
                 complete=ApplicationState.job_offer.state.analyzed,
                 in_progress=ApplicationState.job_offer.state.is_analyzing,
                 process_callback=ApplicationState.analyze_job,
                 view_callback=display_analyzed_job
                 ),
            item('Upload CV',
                 'file-text',
                 complete=CvState.has_cv_data,
                 process_callback=CvState.toggle_load_cv_data_open,
                 view_callback=display_cv,
                 required=False
                 ),
            item('Prompt Refinements',
                 'message-circle-more',
                 required=False,
                 complete=RefinementState.has_prompt,
                 process_callback=RefinementState.toggle_dialog,
                 view_callback=display_prompt
                 ),
            refinement_dialog(),
            item('Generate Application',
                 'notebook-pen',
                 disabled=~ApplicationState.job_offer.state.analyzed,
                 complete=ApplicationState.job_offer.state.composed,
                 in_progress=ApplicationState.job_offer.state.is_composing,
                 process_callback=ApplicationState.compose_application,
                 view_callback=display_application
                 ),
            item('Store Document',
                 'hard-drive-upload',
                 disabled=~ApplicationState.job_offer.state.composed,
                 complete=ApplicationState.job_offer.state.stored,
                 in_progress=ApplicationState.job_offer.state.is_storing,
                 process_callback=ApplicationState.store_in_google_doc,
                 view_callback=display_stored_doc
                 ),
            spacing="4",
            width="100%",
            align="start"
        ))


def item(step: str, icon: str = 'play', disabled: bool = False, required=True, in_progress=False,
         complete: bool = False,
         process_callback: Callable = None,
         view_callback: Callable[[], rx.Component] = lambda: rx.text('')):
    return rx.hstack(
        rx.button(
            rx.icon(icon),
            variant=rx.cond(required & ~complete, '', 'surface'),
            disabled=disabled,
            on_click=process_callback,
            loading=in_progress
        ),
        rx.cond(complete, rx.icon('circle-check-big'), rx.cond(required, rx.icon('circle'), rx.icon('circle-dashed'))),
        rx.text(step, size="4"),
        rx.spacer(),

        rx.cond(complete,
                rx.popover.root(
                    rx.popover.trigger(
                        rx.button(
                            rx.icon('ellipsis'),
                        ),
                    ),
                    rx.popover.content(
                        view_callback(),
                        style={"max-width": 500, 'max-height': 400},
                    )

                ),
                rx.button(rx.icon('ellipsis'), disabled=True)
                ),
        width='100%',
        align='center',

    )


def display_analyzed_job():
    return rx.vstack(
        rx.heading('Company'),
        ApplicationState.job_offer_analyzed.company_name,
        rx.heading('Title'),
        ApplicationState.job_offer_analyzed.title,
        rx.heading('About'),
        ApplicationState.job_offer_analyzed.about,
        rx.heading('Requirements'),
        ApplicationState.job_offer_analyzed.requirements,
        rx.heading('Offers'),
        ApplicationState.job_offer_analyzed.offers,
    )


def display_cv():
    return rx.vstack(
        rx.text(
            rx.hstack(
                rx.heading('Filename: '),
                rx.text(CvState.cv_data.title, size='4'),
                align='center'
            )
        ),
        rx.markdown(CvState.cv_data.text)
    )

def display_prompt():
    return rx.vstack(
        rx.heading('Prompt Refinement'),
        rx.text_area(RefinementState.prompt, read_only=True)
    )

def display_application():
    return rx.vstack(rx.heading('Your Cover Letter'),
                     rx.markdown(ApplicationState.job_offer_application.text)
                     )


def display_stored_doc():
    return rx.vstack(
        rx.heading('Application Doc'),
        rx.hstack(
            rx.icon('book-check'),
            rx.markdown(f'[{ApplicationState.job_offer_cover_letter_doc.name}]'
                        f'(https://docs.google.com/document/d/{ApplicationState.job_offer_cover_letter_doc.document_id})'),
            align='center'
        )
    )
