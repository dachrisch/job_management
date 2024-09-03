import logging
import os

from more_itertools import one, first

from job_management.backend.ai.conversation import Conversation
from job_management.backend.entity import JobOffer, JobOfferAnalyze
from job_management.backend.service.job_offer import JobOfferService
from job_offer_spider.db.job_offer import JobOfferDb
from job_offer_spider.item.db.job_offer import JobOfferAnalyzeDto


class JobApplicationService(JobOfferService):
    def __init__(self, db: JobOfferDb, openai_api_key=os.getenv('OPENAI_API_KEY')):
        super().__init__(db)
        self.jobs = db.jobs
        self.jobs_body = db.jobs_body
        self.jobs_analyze = db.jobs_analyze
        self.c = Conversation(openai_api_key=openai_api_key)
        self.log = logging.getLogger(f'{__name__}')

    def job_analysis(self, job_offer: JobOffer):
        return first(map(lambda a: JobOfferAnalyze(**a.to_dict()),
                         self.jobs_analyze.filter({'url': {'$eq': job_offer.url}})), None)

    def analyze_job(self, job_offer: JobOffer) -> JobOfferAnalyzeDto:
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
        analyzed_result = self.c.as_system(system_prompt).as_user(user_prompt).complete()
        analyze_dto = JobOfferAnalyzeDto(**analyzed_result['job'])
        analyze_dto.url = job_offer.url
        self.log.debug(f'Finished analyzing offer: {analyze_dto}')
        self.jobs_analyze.add(analyze_dto)
        self.jobs.update_one({'url': job_offer.url}, {'$set': {'state.analyzed': True}})

        return analyze_dto
