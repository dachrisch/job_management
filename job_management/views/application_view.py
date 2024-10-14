import reflex as rx

from job_management.backend.entity.storage import JobApplicationCoverLetterDoc
from job_management.backend.state.all_steps import AllStepsState
from job_management.backend.state.application import ApplicationState
from job_management.backend.state.cv import CvState
from job_management.backend.state.google import GoogleState
from job_management.backend.state.openai_key import OpenaiKeyState
from job_management.backend.state.refinement import RefinementState
from job_management.components.application.item import item
from job_management.components.card import card
from job_management.components.dialog.refinement import refinement_dialog
from job_management.components.dialog.text_area import TextAreaDialog


def render():
    return rx.container(
        rx.flex(
            header(),
            rx.vstack(
                rx.cond(OpenaiKeyState.is_valid_key & GoogleState.is_logged_in, process_steps(),
                        render_logins()),
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
            rx.link(ApplicationState.job_offer.site_url, href=f'/jobs?site={ApplicationState.job_offer.site_url}')
        ),
        align='center'
    )


def render_logins():
    return rx.card(
        rx.vstack(rx.cond(~OpenaiKeyState.is_valid_key,
                          rx.vstack(rx.callout('An OpenAI API Key is needed to proceed', icon='info'),
                                    rx.button('Provide Key', on_click=OpenaiKeyState.toggle_openai_key_dialog_open),
                                    align="center"
                                    )
                          ),
                  rx.cond(~GoogleState.is_logged_in,
                          rx.vstack(rx.callout('Google Drive Login required', icon='info'),
                                    rx.button('Login to Google', on_click=GoogleState.login_flow,
                                              loading=GoogleState.is_running_flow),
                                    align="center"
                                    )
                          ),
                  spacing="4",
                  width="100%",
                  align="center"
                  ))


def process_steps():
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.spacer(),
                rx.button(rx.icon('play'), 'All Steps', on_click=AllStepsState.run_all_steps,
                          disabled=~CvState.has_cv_data,
                          loading=AllStepsState.running),
                rx.spacer(),
                align='center',
                width='100%',
            ),
            item('Analyse',
                 'search-code',
                 disabled=AllStepsState.running,
                 complete=ApplicationState.job_offer.state.analyzed,
                 in_progress=ApplicationState.job_offer.state.is_analyzing,
                 process_callback=ApplicationState.analyze_job,
                 view_callback=display_analyzed_job
                 ),
            item('Upload CV',
                 'file-text',
                 disabled=AllStepsState.running,
                 complete=CvState.has_cv_data,
                 process_callback=CvState.toggle_load_cv_data_open,
                 view_callback=display_cv,
                 ),
            item('Prompt Refinements',
                 'message-circle-more',
                 required=False,
                 disabled=AllStepsState.running,
                 complete=RefinementState.has_prompt,
                 process_callback=RefinementState.toggle_dialog,
                 view_callback=display_prompt
                 ),
            refinement_dialog(),
            item('Generate Application',
                 'notebook-pen',
                 disabled=~(ApplicationState.job_offer.state.analyzed & CvState.has_cv_data) | AllStepsState.running,
                 complete=ApplicationState.job_offer.state.composed,
                 in_progress=ApplicationState.job_offer.state.is_composing,
                 process_callback=ApplicationState.compose_application,
                 view_callback=display_application
                 ),
            item('Store Document',
                 'hard-drive-upload',
                 disabled=~ApplicationState.job_offer.state.composed | AllStepsState.running,
                 complete=ApplicationState.job_offer.state.stored,
                 in_progress=ApplicationState.job_offer.state.is_storing,
                 process_callback=ApplicationState.store_in_google_doc,
                 view_callback=display_stored_doc
                 ),
            spacing="4",
            width="100%",
            align="start"
        ))


def display_analyzed_job():
    return rx.vstack(
        rx.hstack(rx.heading('Company'), rx.spacer(),
                  TextAreaDialog.create(title='Analyze from source',
                                        icon='pencil',
                                        trigger='paste description',
                                        description='Paste the job description to be analyzed',
                                        placeholder='Job description',
                                        form_field='job_description',
                                        on_submit=ApplicationState.edit_analyzed_job)),
        ApplicationState.job_offer_analyzed.company_name,
        rx.heading('Title'),
        ApplicationState.job_offer_analyzed.title,
        rx.heading('About'),
        ApplicationState.job_offer_analyzed.about,
        rx.heading('Requirements'),
        ApplicationState.job_offer_analyzed.requirements,
        rx.heading('Offers'),
        ApplicationState.job_offer_analyzed.offers,

        width='100%'
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


def stored_doc_link(cover_letter: JobApplicationCoverLetterDoc):
    return rx.hstack(
        rx.icon('book-check'),
        rx.moment(cover_letter.date, from_now=True),
        rx.link(rx.text(cover_letter.name),
                href=f'https://docs.google.com/document/d/{cover_letter.document_id}',
                target='_blank'),
        align='center'
    )


def display_stored_doc():
    return rx.vstack(
        rx.heading('Application Doc'),
        rx.foreach(ApplicationState.job_offer_cover_letter_docs, stored_doc_link),
    )
