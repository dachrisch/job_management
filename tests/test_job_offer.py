from unittest import TestCase

from more_itertools import flatten

from job_management.backend.entity.offer import JobOffer


def flatten_dict(content):
    return  sorted({x for v in content.values() for x in v})


class TestJobOffer(TestCase):
    def test_job_site_has_base64(self):
        self.assertEqual('dGVzdCB1cmw=', JobOffer(url='test url').base64_url)

    def test_flatten_dict(self):
        self.assertEqual(
            ['a', 'b', 'c', 'd', 'e'],
            flatten_dict({'1': ['a', 'b', 'c', 'd'],
             '2': ['e']})
        )
