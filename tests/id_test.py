from datetime import datetime
from unittest import TestCase

from job_offer_spider.item.db.job_offer import JobOfferDto
from job_offer_spider.item.db.sites import JobSiteDto


class JobOfferIdTestCase(TestCase):
    def test_id_from_dict(self):
        timestamp = datetime.now().timestamp()
        dto = JobOfferDto().from_dict({'title': 'test', 'added': timestamp, '_id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(dto.to_dict(encode_json=True),
                         {'added': timestamp, 'title': 'test', 'url': None, 'site_url': None, 'seen': None})

    def test_id_from_kw_constructor(self):
        timestamp = datetime.now().timestamp()
        dto = JobOfferDto(**{'title': 'test', 'added': timestamp, 'id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(dto.to_dict(encode_json=True),
                         {'added': timestamp, 'title': 'test', 'url': None, 'site_url': None, 'seen': None})


class TargetWebsiteIdTestCase(TestCase):
    def test_empty_id(self):
        dto = JobSiteDto().from_dict({'title': 'test', 'added': None, '_id': None})
        self.assertEqual({'added': None, 'title': 'test', 'url': None, 'last_scanned': None, 'jobs': None},
                         dto.to_dict(encode_json=True))

    def test_id_from_dict(self):
        timestamp = datetime.now().timestamp()
        dto = JobSiteDto().from_dict({'title': 'test', 'added': timestamp, '_id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(
            {'added': timestamp, 'title': 'test', 'url': None, 'last_scanned': None, 'jobs': None},
            dto.to_dict(encode_json=True))

    def test_id_from_kw_constructor(self):
        timestamp = datetime.now().timestamp()
        dto = JobSiteDto(**{'title': 'test', 'added': timestamp, 'id': 1234})
        self.assertEqual(dto.id, 1234)
        self.assertEqual(
            {'added': timestamp, 'title': 'test', 'url': None, 'last_scanned': None, 'jobs': None},
            dto.to_dict(encode_json=True))
