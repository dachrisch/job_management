from unittest import IsolatedAsyncioTestCase

import mock

from job_management import wire
from job_management.backend import service
from job_management.backend.service.container import Container
from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.sites import JobSiteDto
from tests.mocks import SitesStateBypassWrapper, mocked_requests_response, MockDb


class JobSitesStateTest(IsolatedAsyncioTestCase):
    def setUp(self):
        wire()

    @mock.patch('requests.get', side_effect=mocked_requests_response)
    async def test_add_jobs_from_form(self, requests_mock):
        wrapper = SitesStateBypassWrapper()
        mock_db = MockDb()
        wrapper.instance.site_service.sites = mock_db
        wrapper.instance.site_service.jobs = mock_db
        await wrapper.add_jobs_to_db(
            {'job_urls': 'http://example.com/jobs/description\nhttp://break-example.com/jobs/title-position'})
        self.assertTrue(mock_db.test_contains(JobSiteDto(url='http://example.com',
                                                         title='Example.com'), ('url', 'title')))
        self.assertTrue(mock_db.test_contains(JobOfferDto(url='http://example.com/jobs/description',
                                                          title='Test Title'), ('url', 'title')),
                        f'item not found in {mock_db.added_items}')
        self.assertTrue(mock_db.test_contains(JobSiteDto(url='http://break-example.com',
                                                         title='Break-example.com'), ('url', 'title')))
        self.assertTrue(mock_db.test_contains(JobOfferDto(url='http://break-example.com/jobs/title-position',
                                                          title='Test Title'), ('url', 'title')))


