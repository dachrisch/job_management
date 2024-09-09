from typing import Any, Iterable

from reflex import EventHandler
from reflex.event import BACKGROUND_TASK_MARKER

from job_management.backend.state.add_jobs import AddJobsState
from job_management.backend.state.sites import SitesState


class SitesStateMock:
    async def load_sites(self):
        return


async def get_state_mock(state):
    return SitesStateMock()


class AddJobsStateBypassWrapper:
    def __init__(self):
        AddJobsState.__aenter__ = lambda x: x
        AddJobsState.__await__ = lambda x: iter(())
        self.instance = AddJobsState()
        self.instance.get_state = get_state_mock

    def add_jobs_to_db(self, form_dict: dict[str, Any]):
        event: EventHandler = AddJobsState.add_jobs_to_db
        function = event.fn
        setattr(function, BACKGROUND_TASK_MARKER, True)
        return function(self.instance, form_dict)


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

    def contains(self, item):
        return self.test_contains(item, ('url',))

    def count(self, condition):
        return 0

    def update_one(self, condition, update, expect_modified):
        return

    def test_contains(self, item, keys: Iterable[str]):
        containing_items = filter(lambda i: isinstance(i, type(item)), self.added_items)
        for containing_item in containing_items:
            if all([getattr(item, key, None) == getattr(containing_item, key, None) for key in keys]):
                return True
        return False
