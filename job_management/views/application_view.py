from typing import Optional

import reflex as rx
from reflex import Style

from job_management.backend.state.application import ApplicationState
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
    if question:
        children.append(rx.box(
            rx.container(question, style=question_style),
            text_align="right",
        ))
    children.append(rx.box(
        rx.container(answer, style=answer_style),
        text_align="left",
    ))
    return rx.box(
        *children,
        margin_y="0em",
        width='100%',
    )


def chat() -> rx.Component:
    return rx.vstack(
        qa(rx.vstack(
            rx.text('Lets start writing the application for the job'),
            rx.text('We begin by analyzing the job content.'),
            rx.cond(~ApplicationState.job_offer.state.analyzed , rx.button(
                    rx.text('Analyze'),
                    on_click=ApplicationState.analyze_job,
                    loading=ApplicationState.job_offer.state.is_analyzing
                )
                    )
        ),
        ),
        rx.cond(ApplicationState.job_offer.state.analyzed,
                qa(rx.vstack(
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
                        ),
                    rx.markdown(
                        f'Analyze the job [{ApplicationState.job_offer.title}]({ApplicationState.job_offer.url})',
                        component_map={
                            'a': lambda text, **props: rx.link(text, target='_blank', **props)
                        }
                    )
                )
                ),
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
