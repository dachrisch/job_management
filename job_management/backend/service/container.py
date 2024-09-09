import logging.config

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Factory, Resource
from dependency_injector.wiring import Provider, Provide
from scrapy.utils.project import get_project_settings

from job_management.backend.service.application import JobApplicationService
from job_management.backend.service.storage import JobApplicationStorageService
from job_offer_spider.db.job_management import JobManagementDb


class Container(DeclarativeContainer):
    logging = Resource(logging.config.dictConfig, config=get_project_settings()['LOGGING'])

    job_management_db = Singleton(JobManagementDb)

    job_application_service = Factory(JobApplicationService, db=job_management_db)
    job_storage_service = Factory(JobApplicationStorageService, db=job_management_db)


class Locator:
    application_service: JobApplicationService = Provide[Container.job_application_service]
    storage_service: JobApplicationStorageService = Provide[Container.job_storage_service]
