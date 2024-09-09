from datetime import datetime
from unittest import TestCase

from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.sites import JobSiteDto


class JobOfferIdTestCase(TestCase):
    def test_id_from_dict(self):
        timestamp = datetime.now().timestamp()
        dto = JobOfferDto.from_dict({'url': 'test', 'added': timestamp, '_id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(dto.to_dict(encode_json=True),
                         {'added': timestamp, 'url': 'test', 'title': None, 'site_url': None,
                          'state': {'analyzed': False, 'composed': False, 'stored': False},
                          'seen': None})

    def test_id_from_kw_constructor(self):
        timestamp = datetime.now().timestamp()
        dto = JobOfferDto(**{'url': 'test', 'added': timestamp, 'id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(dto.to_dict(encode_json=True),
                         {'added': timestamp, 'url': 'test', 'title': None, 'site_url': None, 'seen': None,
                          'state': {'analyzed': False, 'composed': False, 'stored': False}})


class TargetWebsiteIdTestCase(TestCase):
    def test_empty_id(self):
        dto = JobSiteDto.from_dict({'url': 'test', 'added': None, '_id': None})
        self.assertEqual(
            {'added': None, 'url': 'test', 'title': None, 'last_scanned': None, 'jobs': {'total': 0, 'unseen': 0}, },
            dto.to_dict(encode_json=True))

    def test_id_from_dict(self):
        timestamp = datetime.now().timestamp()
        dto = JobSiteDto.from_dict({'url': 'test', 'added': timestamp, '_id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(
            {'added': timestamp, 'url': 'test', 'title': None, 'last_scanned': None,
             'jobs': {'total': 0, 'unseen': 0}, },
            dto.to_dict(encode_json=True))

    def test_id_from_kw_constructor(self):
        timestamp = datetime.now().timestamp()
        dto = JobSiteDto(**{'url': 'test', 'added': timestamp, 'id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(
            {'added': timestamp, 'url': 'test', 'title': None, 'last_scanned': None, 'jobs': {'total': 0, 'unseen': 0}},
            dto.to_dict(encode_json=True))
