from typing import Optional, Tuple, Callable

import reflex as rx
from reflex import Style, Var

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


def item(step: str, icon: str = 'play', enabled: bool = True, required=True, in_progress=False, complete: bool = False,
         process_callback: Callable = None,
         view_callback: Callable[[], rx.Component] = lambda: rx.text('')):
    return rx.hstack(
        rx.button(
            rx.icon(icon),
            variant=rx.cond(required & ~complete, '', 'surface'),
            enabled=enabled,
            on_click=process_callback,
            loading=in_progress
        ),
        rx.cond(complete, rx.icon('circle-check-big'), rx.icon('circle')),
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
                        style={"width": 500, 'height': 400},
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
        rx.text('Filename'),
        rx.text(CvState.cv_data.title),
        rx.text(CvState.cv_data.text)
    )


def header():
    return rx.vstack(
        card(
            'briefcase',
            'green',
            ApplicationState.job_offer.title,
            ApplicationState.job_offer.url,
        ), rx.card(
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

                     ),
                item('Generate Application',
                     'notebook-pen',
                     enabled=ApplicationState.job_offer.state.analyzed,
                     complete=ApplicationState.job_offer.state.composed,
                     process_callback=ApplicationState.analyze_job,
                     ),
                item('Store Document',
                     'hard-drive-upload',
                     enabled=ApplicationState.job_offer.state.composed,
                     complete=ApplicationState.job_offer.state.stored,
                     process_callback=ApplicationState.store_in_google_doc,
                     ),
                spacing="4",
                width="100%",
                align="start"
            )),
        rx.hstack(
            rx.button(rx.icon('search-code'), rx.text('Analyze', size='4')),
            rx.icon('chevron-right'),
            rx.button(rx.icon('file-text'), rx.text('Upload CV', size='4'), ),
            rx.icon('chevron-right'),
            rx.button(rx.icon('message-circle-more'), rx.text('Refinement', size='4'),
                      on_click=RefinementState.toggle_dialog,
                      variant='surface'
                      ),
            rx.dialog.root(
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
            ),
            rx.icon('chevron-right'),
            rx.button(rx.icon('notebook-pen'), rx.text('Generate', size='4'),
                      disabled=True),
            rx.icon('chevron-right'),
            rx.button(rx.icon('hard-drive-upload'), rx.text('Store', size='4'),
                      disabled=True),
            align='center'
        ),
        align='center'
    )


def qa(answer: rx.Component, question: Optional[rx.Component] = None) -> rx.Component:
    children: list[rx.Component] = []
    children.append(rx.box(
        rx.container(answer, style=answer_style),
        text_align="left",
    ))
    if question:
        children.append(rx.box(
            rx.container(question, style=question_style),
            text_align="right",
        ))
    return rx.box(
        *children,
        margin_y="0em",
        width='100%',
    )


def chat_header() -> rx.Component:
    return qa(rx.text('Lets start writing the application for the job'))


def chat_analyze_begin() -> rx.Component:
    return qa(
        rx.vstack(
            rx.text('We begin by analyzing the job content.'),
            rx.button(
                rx.text('Analyze'),
                on_click=ApplicationState.analyze_job,
                loading=ApplicationState.job_offer.state.is_analyzing
            )
        )
    )


def chat_analyze_load() -> rx.Component:
    return qa(
        question=rx.markdown(
            f'Analyze the job [{ApplicationState.job_offer.title}]({ApplicationState.job_offer.url})',
            component_map={
                'a': lambda text, **props: rx.link(text, target='_blank', **props)
            }
        ),
        answer=rx.vstack(
            rx.text('We begin by analyzing the job content.'),
            rx.button(
                rx.text('Analyze'),
                loading=ApplicationState.job_offer.state.is_analyzing,
                disabled=~ApplicationState.job_offer.state.is_analyzing
            )
        ),

    )


def chat_analyzed() -> rx.Component:
    return qa(
        answer=rx.vstack(rx.text('The Job was analyzed. Here is what we found.'),
                         rx.accordion.root(
                             rx.accordion.item(header='Job Description',
                                               content=rx.vstack(
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
                                               ),
                             collapsible=True,
                             width='100%',
                             variant="surface",
                         )
                         )
    )


def chat_empty() -> rx.Component:
    return None


def chat_cv_data() -> rx.Component:
    return qa(
        answer=rx.vstack(
            rx.text('Now we need your CV data'),
            rx.button('Upload CV', on_click=CvState.toggle_load_cv_data_open)
        )
    )


def chat_cv_data_received() -> rx.Component:
    return qa(
        question=rx.vstack(
            rx.text('Here is my CV data'),
            rx.accordion.root(
                rx.accordion.item(header='CV data', content=CvState.cv_data.text),
                collapsible=True,
                width='100%',
                variant="surface",

            )
        ),
        answer=rx.vstack(
            rx.text('Now we need your CV data'),
            rx.button('Upload CV', disabled=True)
        )
    )


def chat_compose() -> rx.Component:
    return qa(
        answer=rx.vstack(
            rx.text('Now, everything is ready to compose the application'),
            rx.button('Compose application', on_click=ApplicationState.compose_application)
        )
    )


def chat_composing() -> rx.Component:
    return qa(
        question=rx.vstack(rx.text('Write the application for me')),
        answer=rx.vstack(
            rx.text('Now, everything is ready to compose the application'),
            rx.button('Compose application', loading=ApplicationState.job_offer.state.is_composing,
                      disabled=ApplicationState.job_offer.state.composed),
        )
    )


def chat_composed() -> rx.Component:
    return qa(
        answer=rx.vstack(
            rx.markdown(ApplicationState.job_offer_application.text),
        )
    )


def chat_storable() -> rx.Component:
    return qa(
        answer=rx.vstack(
            rx.text('We are ready to create the cover letter'),
            rx.button('Create Google doc', on_click=ApplicationState.store_in_google_doc)
        )
    )


def chat_storing() -> rx.Component:
    return qa(
        question=rx.text('Create the cover letter in google docs.'),
        answer=rx.vstack(
            rx.text('We are ready to store the document'),
            rx.button('Create Google doc', loading=ApplicationState.job_offer.state.is_storing,
                      disabled=ApplicationState.job_offer.state.stored)
        )
    )


def chat_stored() -> rx.Component:
    return qa(
        answer=rx.vstack(
            rx.markdown(
                'Here we have your document: '
                f'[{ApplicationState.job_offer_cover_letter_doc.name}]'
                f'(https://docs.google.com/document/d/{ApplicationState.job_offer_cover_letter_doc.document_id})',
                component_map={
                    'a': lambda text, **props: rx.link(text, target='_blank', **props)
                }
            ),
        )
    )


def chat() -> rx.Component:
    chat_history: list[Tuple[Var | bool, Callable[[], rx.Component], Callable[[], rx.Component]]] = [
        (True, chat_header, chat_header)]
    chat_history.append(
        (ApplicationState.job_offer.state.analyzed | ApplicationState.job_offer.state.is_analyzing, chat_analyze_load,
         chat_analyze_begin))
    chat_history.append((ApplicationState.job_offer.state.analyzed, chat_analyzed, chat_empty))
    chat_history.append((ApplicationState.job_offer.state.analyzed & ~CvState.has_cv_data, chat_cv_data, chat_empty))
    chat_history.append(
        (ApplicationState.job_offer.state.analyzed & CvState.has_cv_data, chat_cv_data_received, chat_empty))
    chat_history.append((
        ApplicationState.job_offer.state.analyzed
        & CvState.has_cv_data
        & ~ApplicationState.job_offer.state.composed
        & ~ApplicationState.job_offer.state.is_composing,
        chat_compose, chat_empty
    ))
    chat_history.append((
        ApplicationState.job_offer.state.analyzed
        & CvState.has_cv_data
        & (ApplicationState.job_offer.state.is_composing | ApplicationState.job_offer.state.composed),
        chat_composing, chat_empty,
    ))
    chat_history.append((
        ApplicationState.job_offer.state.composed,
        chat_composed, chat_empty,
    ))
    chat_history.append((
        ApplicationState.job_offer.state.composed
        & ~(ApplicationState.job_offer.state.is_storing | ApplicationState.job_offer.state.stored),
        chat_storable, chat_empty,
    ))
    chat_history.append((
        ApplicationState.job_offer.state.composed
        & (ApplicationState.job_offer.state.is_storing | ApplicationState.job_offer.state.stored),
        chat_storing, chat_empty,
    ))
    chat_history.append((
        ApplicationState.job_offer.state.stored,
        chat_stored, chat_empty,
    ))

    return rx.vstack(
        *[rx.cond(ch[0], ch[1](), ch[2]()) for ch in chat_history],
        width='100%',
        margin_y="0em",
        align='center'
    )


def action_bar() -> rx.Component:
    return rx.hstack(
        rx.input(
            placeholder="Ask a question",
            size='3',
            radius='full',
            variant='soft',
            width='100%',
        ),
        rx.button("Ask", style=button_style),
        width='100%',
        align='center'
    )


def render():
    return rx.container(
        rx.flex(
            header(),
            chat(),
            action_bar(),
            spacing="2",
            direction="column",
        ),
    )
