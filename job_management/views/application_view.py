from typing import Optional, Tuple, Callable

import reflex as rx
from reflex import Style, Var

from job_management.backend.state.application import ApplicationState
from job_management.backend.state.options import OptionsState
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
        answer=rx.vstack(
            rx.heading('Company'),
            ApplicationState.analyzed_job_offer.company_name,
            rx.heading('Title'),
            ApplicationState.analyzed_job_offer.title,
            rx.heading('About'),
            ApplicationState.analyzed_job_offer.about,
            rx.heading('Requirements'),
            ApplicationState.analyzed_job_offer.requirements,
            rx.heading('Offers'),
            ApplicationState.analyzed_job_offer.offers,
        )
    )


def chat_empty() -> rx.Component:
    return None


def chat_cv_data() -> rx.Component:
    return qa(
        answer=rx.vstack(
            rx.text('Now we need your CV data'),
            rx.button('Upload CV', on_click=OptionsState.toggle_load_cv_data_open)
        )
    )

def chat_cv_data_received()-> rx.Component:
    return qa(
        question=rx.vstack(
            rx.text('Here is my CV data'),
            rx.text(OptionsState.cv_data)
        ),
        answer=rx.vstack(
            rx.text('Now we need your CV data'),
            rx.button('Upload CV', disabled=True)
        )
    )


def chat() -> rx.Component:
    chat_history: list[Tuple[Var | bool, Callable[[], rx.Component], Callable[[], rx.Component]]] = [
        (True, chat_header, chat_header)]
    chat_history.append(
        (ApplicationState.job_offer.state.analyzed | ApplicationState.job_offer.state.is_analyzing, chat_analyze_load,
         chat_analyze_begin))
    chat_history.append((ApplicationState.job_offer.state.analyzed, chat_analyzed, chat_empty))
    chat_history.append((ApplicationState.job_offer.state.analyzed & ~OptionsState.has_cv_data, chat_cv_data, chat_empty))
    chat_history.append((ApplicationState.job_offer.state.analyzed & OptionsState.has_cv_data, chat_cv_data_received, chat_empty))
    chat_history.append((
        ApplicationState.job_offer.state.analyzed
        & OptionsState.has_cv_data,
        chat_cv_data_received, chat_empty
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
