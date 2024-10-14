from unittest import IsolatedAsyncioTestCase

import mock
from dependency_injector import containers
from dependency_injector.providers import Singleton

from job_management import Container
from job_management.backend.service.google import CredentialsService
from job_management.backend.service.locator import Locator
from job_offer_spider.db.collection import CollectionHandler
from job_offer_spider.db.job_management import JobManagementDb
from job_offer_spider.item.db.job_offer import JobOfferDto, JobOfferBodyDto
from job_offer_spider.item.db.sites import JobSiteDto
from tests.mocks import AddJobsStateBypassWrapper, mocked_requests_response, MockCollectionHandler, \
    AuthenticatedCredentialsService



class MockJobManagementDb(JobManagementDb):
    def __init__(self, collection_handler: MockCollectionHandler):
        self.collection_handler = collection_handler

    @property
    def jobs(self) -> CollectionHandler[JobOfferDto]:
        return self.collection_handler

    @property
    def sites(self) -> CollectionHandler[JobSiteDto]:
        return self.collection_handler

    @property
    def jobs_body(self) -> CollectionHandler[JobOfferBodyDto]:
        return self.collection_handler

    @property
    def jobs_analyze(self):
        return self.collection_handler

    @property
    def jobs_application(self):
        return self.collection_handler

    @property
    def cover_letter_docs(self):
        return self.collection_handler

    @property
    def cvs(self):
        return self.collection_handler


class OverridingContainer(containers.DeclarativeContainer):
    credentials_service = Singleton(AuthenticatedCredentialsService)
    job_management_db = Singleton(MockJobManagementDb, collection_handler=MockCollectionHandler())


class JobSitesStateTest(IsolatedAsyncioTestCase):
    def setUp(self):
        Container.reset_override()
        Container().unwire()
        Container.override(OverridingContainer)
        container = Container()
        container.init_resources()

        assert isinstance(Locator().job_management_db,
                          MockJobManagementDb), Locator().job_management_db.__class__

    @mock.patch('requests.get', side_effect=mocked_requests_response)
    async def test_add_jobs_from_form(self, requests_mock):
        db = Locator().job_management_db
        wrapper = AddJobsStateBypassWrapper()
        mock_collection_handler: MockCollectionHandler = db.collection_handler
        await wrapper.add_jobs_to_db(
            {'job_urls': 'http://example.com/jobs/description\nhttp://break-example.com/jobs/title-position'})
        self.assertTrue(mock_collection_handler.test_contains(JobSiteDto(url='http://example.com',
                                                                         title='Example.com'), ('url', 'title')))
        self.assertTrue(mock_collection_handler.test_contains(JobOfferDto(url='http://example.com/jobs/description',
                                                                          title='Test Title'), ('url', 'title')),
                        f'item not found in {mock_collection_handler.added_items}')
        self.assertTrue(mock_collection_handler.test_contains(JobSiteDto(url='http://break-example.com',
                                                                         title='Break-example.com'), ('url', 'title')))
        self.assertTrue(
            mock_collection_handler.test_contains(JobOfferDto(url='http://break-example.com/jobs/title-position',
                                                              title='Test Title'), ('url', 'title')))
