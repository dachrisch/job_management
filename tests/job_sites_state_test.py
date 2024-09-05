import unittest
from unittest import TestCase, IsolatedAsyncioTestCase

from job_management.backend.state.sites import SitesState
import reflex as rx

class StateWrapper:
    def __init__(self, wrappee:rx.State):
        self.wrappee = wrappee

    def __getattribute__(self, name:str):
        return getattr(SitesState)


class JobSitesStateTest(IsolatedAsyncioTestCase):
    async def test_add_jobs_from_form(self):
        await SitesState().add_jobs_to_db({'job_urls': 'long text\nwith breaks'})
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
