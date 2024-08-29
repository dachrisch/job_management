import os

import reflex as rx
from reflex import Style

from job_management.backend.ai.conversation import Conversation
from job_management.backend.entity import JobOffer, JobOfferAnalyze
from job_management.components.card import card
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.job_offer import JobOfferAnalyzeDto


class ApplicationState(rx.State):
    job_offer: JobOffer = JobOffer()
    is_analyzing: bool = False
    analyzed_job_offer: JobOfferAnalyze = JobOfferAnalyze()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JobOfferDb()

    def load_current_job_offer(self):
        job_url = self.router.page.params.get('job', None)
        if job_url:
            self.job_offer = next(
                map(lambda s: JobOffer(**s.to_dict()), self.db.jobs.filter({'url': {'$eq': job_url}})))
            self.analyzed_job_offer = next(map(lambda a: JobOfferAnalyze(**a.to_dict()),
                                               self.db.jobs_analyze.filter({'url': {'$eq': self.job_offer.url}})), None)
            self.job_offer.is_analyzed = self.analyzed_job_offer is not None

    @rx.background
    async def analyze_job(self):
        async with self:
            self.is_analyzing = True

        c = Conversation(openai_api_key=os.getenv('OPENAI_API_KEY'))
        system_prompt = ('Analyze the content of this webpage and find the job description. '
                         'if no job description is found, return empty json as {}'
                         'if a job description is found, respond with'
                         '{'
                         '"job":{'
                         '"title": <job title>,'
                         '"about": <all infos about the company and general job description>,'
                         '"company_name": <name of the company>,'
                         '"requirements": <all infos about required skills>,'
                         '"responsibilities": <all infos about the tasks and responsibilities of this role>,'
                         '"offers": <what the company is offering in this position>,'
                         '"additional": <all additional infos not covered before>'
                         '}'
                         '}')
        page_content = list(self.db.jobs_body.filter({'url': {'$eq': self.job_offer.url}}))[0]
        user_prompt = f'The web page content is: {page_content.body}'

        async with self:
            analyzed_result = c.as_system(system_prompt).as_user(user_prompt).complete()
            analyze_dto = JobOfferAnalyzeDto(**analyzed_result['job'])
            analyze_dto.url = self.job_offer.url
            self.db.jobs_analyze.add(analyze_dto)
            self.job_offer.is_analyzed = True

        async with self:
            self.is_analyzing = False


# Common styles for questions and answers.
shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
chat_margin = "0%"
message_style = dict(
    padding="1em",
    border_radius="5px",
    margin_y="0.5em",
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
            rx.cond(
                ApplicationState.job_offer.is_analyzed,
                rx.button(rx.icon('search-check'), disabled=True, title='Analyzed'),
                rx.button(
                    rx.icon('search'),
                    on_click=ApplicationState.analyze_job,
                    loading=ApplicationState.is_analyzing
                )
            )
        ),
        rx.cond(
            ApplicationState.job_offer.is_analyzed,
            rx.accordion.root(
                rx.accordion.item(
                    header='Job Description',
                    content=rx.vstack(
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
                ),
                collapsible=True,
            )
        ),
        align='center'
    )


def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(question, style=question_style),
            text_align="right",
        ),
        rx.box(
            rx.text(answer, style=answer_style),
            text_align="left",
        ),
        margin_y="1em",
        width='100%',
    )


def chat() -> rx.Component:
    qa_pairs = [
        (
            "What is Reflex?",
            "A way to build web apps in pure Python!",
        ),
        (
            "What can I make with it?",
            "Anything from a simple website to a complex web app! very long text very long text very long text very long text very long text very long text very long text very long text very long text very long text very long text very long text very long text very long text ",
        ),
    ]
    return rx.vstack(
        *[
            qa(question, answer)
            for question, answer in qa_pairs
        ],
        width='100%',
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
