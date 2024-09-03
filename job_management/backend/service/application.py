import logging
import string

from more_itertools import one, first

from job_management.backend.ai.conversation import Conversation
from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.offer_analyzed import JobOfferAnalyze
from job_management.backend.service.job_offer import JobOfferService
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.job_offer import JobOfferAnalyzeDto


class JobApplicationService(JobOfferService):
    openai_api_key: str = None

    def __init__(self, db: JobManagementDb, ):
        super().__init__(db)
        self.jobs = db.jobs
        self.jobs_body = db.jobs_body
        self.jobs_analyze = db.jobs_analyze
        self.cvs = db.cvs
        self.log = logging.getLogger(f'{__name__}')

    def load_job_analysis(self, job_offer: JobOffer):
        return first(map(lambda a: JobOfferAnalyze(**a.to_dict()),
                         self.jobs_analyze.filter({'url': {'$eq': job_offer.url}})), None)

    def analyze_job(self, job_offer: JobOffer) -> JobOfferAnalyzeDto:
        c = Conversation(openai_api_key=self.openai_api_key)
        self.log.info(f'Analyzing [{job_offer}]')
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
        page_content = one(self.jobs_body.filter({'url': {'$eq': job_offer.url}}))
        user_prompt = f'The web page content is: {page_content.body}'
        analyzed_result = c.as_system(system_prompt).as_user(user_prompt).complete()
        analyze_dto = JobOfferAnalyzeDto(url=job_offer.url, **analyzed_result['job'])
        self.log.debug(f'Finished analyzing offer: {analyze_dto}')
        self.jobs_analyze.add(analyze_dto)
        self.jobs.update_one({'url': job_offer.url}, {'$set': {'state.analyzed': True}})

        return analyze_dto

    def compose_application(self, job_offer: JobOffer)->str:
        prompt_template = string.Template('''Help me write an application for the job indicated by JOBDESC

Use the data from my cv as indicated by CVDATA

match the style of the application letter to the tone of the job description, especially if the writing in in german du-style or sie-style.
don't refer to the company names directly, instead use a general description of the role.

Only output the letter text, dont sign it and with the context
(no title)
Greeting to the hiring team
letter text
(exclude the final clause)

>>>>JOBDESC

${JOBDESC}

<<<<JOBDESC

>>>>CVDATA

${CVDATA}

<<<<CVDATA

''')
        analyzed_job = self.load_job_analysis(job_offer)
        cv_data = first(self.cvs.all(), None)
        application_prompt = prompt_template.safe_substitute({
            'JOBDESC': repr(analyzed_job),
            'CVDATA': cv_data.text
        })
        c = Conversation(openai_api_key=self.openai_api_key, response_format="text")
        c.as_user(application_prompt)

        return c.complete()
