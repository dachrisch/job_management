import shutil
from unittest import TestCase, mock

from dependency_injector import containers
from dependency_injector.providers import Singleton
from montydb import set_storage

from job_management.backend import service
from job_management.backend.entity.offer import JobOffer
from job_management.backend.entity.site import JobSite
from job_management.backend.service import locator
from job_management.backend.service.locator import Locator
from job_offer_spider.db.job_management import MontyJobManagementDb
from job_management.backend.service.container import Container
from mocks import mocked_requests_response


# Overriding ``Container`` with ``OverridingContainer``:
@containers.override(Container)
class OverridingContainer(containers.DeclarativeContainer):
    job_management_db = Singleton(MontyJobManagementDb, repository='.monty_test_db')


class JobOfferServiceTest(TestCase):
    def setUp(self):
        container = Container()
        container.init_resources()
        container.wire(packages=[service, locator])
        shutil.rmtree('.monty_test_db')
        set_storage(container.config.get('database.repository'), storage='sqlite', check_same_thread=False)
        Locator.db.init()

    @mock.patch('requests.get', side_effect=mocked_requests_response)
    def test_add_job_offer(self, response_mock):
        s = Locator.job_offer_service
        s.add_job(JobOffer(url='https://example.com'))
        self.assertEqual(1, Locator.db.jobs.count({}))

    def test_clear_jobs(self):
        s = Locator.job_offer_service
        s.clear_jobs_for_site(JobSite(url='https://example.com'))
        self.assertEqual(0, Locator.db.jobs.count({}))
