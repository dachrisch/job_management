from dependency_injector.wiring import Provide

from job_management.backend.service.application import JobApplicationService
from job_management.backend.service.container import Container
from job_management.backend.service.cv import CvService
from job_management.backend.service.job_offer import JobOfferService
from job_management.backend.service.site import JobSitesService
from job_management.backend.service.sites_with_jobs import JobSitesWithJobsService
from job_management.backend.service.storage import JobApplicationStorageService
from job_offer_spider.db.job_management import JobManagementDb


class Locator:
    job_offer_service: JobOfferService = Provide[Container.job_offer_service]
    job_sites_service: JobSitesService = Provide[Container.job_sites_service]
    jobs_sites_with_jobs_service: JobSitesWithJobsService = Provide[Container.sites_jobs_offer_service]
    application_service: JobApplicationService = Provide[Container.job_application_service]
    storage_service: JobApplicationStorageService = Provide[Container.job_storage_service]
    cv_service: CvService = Provide[Container.cv_service]

    db: JobManagementDb = Provide[Container.job_management_db]
