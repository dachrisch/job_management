import logging.config

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton, Factory, Resource
from scrapy.utils.project import get_project_settings

from job_management.backend import state, service
from job_management.backend.service.application import JobApplicationService
from job_management.backend.service.cv import CvService
from job_management.backend.service.job_offer import JobOfferService
from job_management.backend.service.site import JobSitesService
from job_management.backend.service.sites_with_jobs import JobSitesWithJobsService
from job_management.backend.service.storage import JobApplicationStorageService
from job_offer_spider.db.job_management import JobManagementDb


class Container(DeclarativeContainer):
    logging = Resource(logging.config.dictConfig, config=get_project_settings()['LOGGING'])
    wiring_config = WiringConfiguration(
        packages=[state, service]
    )

    job_management_db = Singleton(JobManagementDb)

    job_application_service = Factory(JobApplicationService, db=job_management_db)
    job_storage_service = Factory(JobApplicationStorageService, db=job_management_db)
    job_sites_service = Factory(JobSitesService, db=job_management_db)
    job_offer_service = Factory(JobOfferService, db=job_management_db)
    sites_jobs_offer_service = Factory(JobSitesWithJobsService, db=job_management_db)
    cv_service = Factory(CvService, db=job_management_db)


