import unittest
from typing import Any, Iterable
from unittest import IsolatedAsyncioTestCase

import mock
from reflex.event import EventHandler

from job_management.backend.state.sites import SitesState
from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.sites import JobSiteDto, JobStatistic


class SitesStateBypassWrapper:
    def __init__(self):
        self.instance = SitesState()

    def add_jobs_to_db(self, form_dict: dict[str, Any]):
        event: EventHandler = SitesState.add_jobs_to_db
        return event.fn(self.instance, form_dict)


def mocked_requests_response(url: str, *args, **kwargs):
    class MockResponse:
        def __init__(self, url: str, status_code: int):
            self.status_code = status_code
            self.url = url
            self.headers = None

        def raise_for_status(self):
            pass

        @property
        def content(self):
            return bytes('<html><h1>Test Title</h1></html>', 'utf-8')

        @property
        def text(self):
            return self.content.decode('utf-8')

    return MockResponse(url, 200)


class MockDb:
    def __init__(self):
        self.added_items = []

    def add(self, item):
        self.added_items.append(item)

    def contains(self, item, keys:Iterable[str]):
        containing_items = filter(lambda i: isinstance(i,type(item)), self.added_items)
        for containing_item in containing_items:
            if all([getattr(item, key, None) == getattr(containing_item, key, None) for key in keys]):
                return True
        return False



class JobSitesStateTest(IsolatedAsyncioTestCase):
    @mock.patch('requests.get', side_effect=mocked_requests_response)
    async def test_add_jobs_from_form(self, requests_mock):
        wrapper = SitesStateBypassWrapper()
        mock_db = MockDb()
        wrapper.instance.site_service.sites = mock_db
        wrapper.instance.site_service.jobs = mock_db
        await wrapper.add_jobs_to_db({'job_urls': 'http://example.com/jobs/description\nhttp://break-example.com/jobs/title-position'})
        self.assertTrue(mock_db.contains(JobSiteDto(url='http://example.com',
            title='Example.com'), ('url', 'title')))
        self.assertTrue(mock_db.contains(JobOfferDto(url='http://example.com/jobs/description',
            title='Test Title'), ('url', 'title')), f'item not found in {mock_db.added_items}')
        self.assertTrue(mock_db.contains(JobSiteDto(url='http://break-example.com',
            title='Break-example.com'), ('url', 'title')))
        self.assertTrue(mock_db.contains(JobOfferDto(url='http://break-example.com/jobs/title-position',
            title='Test Title'), ('url', 'title')))



if __name__ == '__main__':
    unittest.main()
