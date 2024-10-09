import logging.config

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton, Resource, Configuration, Selector
from scrapy.utils.project import get_project_settings

from job_management.backend import state, service
from job_management.backend.service.application import JobApplicationService
from job_management.backend.service.cv import CvService
from job_management.backend.service.google import GoogleCredentialsService
from job_management.backend.service.job_offer import JobOfferService
from job_management.backend.service.site import JobSitesService
from job_management.backend.service.sites_with_jobs import JobSitesWithJobsService
from job_management.backend.service.storage import JobApplicationStorageService
from job_offer_spider.db.job_management import MontyJobManagementDb, MongoJobManagementDb


class Container(DeclarativeContainer):
    config = Configuration(ini_files=['di_config.ini'], strict=True)

    logging = Resource(logging.config.dictConfig, config=get_project_settings()['LOGGING'])

    wiring_config = WiringConfiguration(
        packages=[state, service]
    )

    job_management_db = Selector(
        config.database.location,
        local=Singleton(MontyJobManagementDb, repository=config.database.repository),
        remote=Singleton(MongoJobManagementDb,
                         username=config.database.username.required(),
                         password=config.database.password.required())
    )

    credentials_service = Singleton(GoogleCredentialsService)
    job_application_service = Singleton(JobApplicationService, db=job_management_db)
    job_sites_service = Singleton(JobSitesService, db=job_management_db)
    job_offer_service = Singleton(JobOfferService, db=job_management_db)
    job_storage_service = Singleton(JobApplicationStorageService, db=job_management_db, credentials_service=credentials_service)
    sites_jobs_offer_service = Singleton(JobSitesWithJobsService, db=job_management_db)
    cv_service = Singleton(CvService, db=job_management_db)
