from dependency_injector.wiring import Provide

from job_management.backend.service.application import JobApplicationService
from job_management.backend.service.container import Container
from job_management.backend.service.cv import CvService
from job_management.backend.service.site import SitesJobsOfferService
from job_management.backend.service.storage import JobApplicationStorageService


class Locator:
    application_service: JobApplicationService = Provide[Container.job_application_service]
    storage_service: JobApplicationStorageService = Provide[Container.job_storage_service]
    sites_jobs_offer_service: SitesJobsOfferService = Provide[Container.sites_jobs_offer_service]
    cv_service: CvService = Provide[Container.cv_service]

