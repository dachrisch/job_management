from unittest import TestCase

from job_management.backend.entity.offer import JobOffer


class TestJobOffer(TestCase):
    def test_job_site_has_base64(self):
        self.assertEqual('dGVzdCB1cmw=', JobOffer(url='test url').base64_url)
