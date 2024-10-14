import shutil
from unittest import TestCase, mock

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton
from montydb import set_storage

from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_management.backend.service.container import Container
from job_management.backend.service.locator import Locator
from job_offer_spider.db.job_management import MontyJobManagementDb
from .mocks import AuthenticatedCredentialsService
from .mocks import mocked_requests_response


class OverridingContainer(DeclarativeContainer):
    job_management_db = Singleton(MontyJobManagementDb, repository='.monty_test_db',
                                  credentials_service=AuthenticatedCredentialsService())


class JobOfferServiceTest(TestCase):
    def setUp(self):
        Container.reset_override()
        Container().unwire()
        Container.override(OverridingContainer)
        container = Container()
        container.init_resources()

        shutil.rmtree('.monty_test_db', ignore_errors=True)
        set_storage(Container().config.get('database.repository'), storage='sqlite', check_same_thread=False)
        Locator.job_management_db.init()

    @mock.patch('requests.get', side_effect=mocked_requests_response)
    def test_add_job_offer(self, response_mock):
        s = Locator.job_offer_service
        s.add_job(JobOffer(url='https://example.com'))
        self.assertEqual(1, Locator.job_management_db.jobs.count({}))

    def test_clear_jobs(self):
        s = Locator.job_offer_service
        s.clear_jobs_for_site(JobSite(url='https://example.com'))
        self.assertEqual(0, Locator.job_management_db.jobs.count({}))
