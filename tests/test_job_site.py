from unittest import TestCase

from job_management.backend.entity.site import JobSite
from job_management.backend.entity.stat import Statistics
from job_offer_spider.item.db.sites import JobSiteDto, JobStatistic


class JobOfferTest(TestCase):

    def test_jobs_dto(self):
        dto_from_dict = JobSiteDto.from_dict({'url': 'test', 'jobs': {'total': 1}})
        self.assertEqual(JobSiteDto(url='test', jobs=JobStatistic(total=1), added=dto_from_dict.added),
                         dto_from_dict)

    def test_jobs_frontend(self):
        self.assertEqual(JobSite(title='test', jobs=Statistics(total=1)),
                         JobSite.parse_obj({'title': 'test', 'jobs': {'total': 1}}))

    def test_jobs_frontend_none(self):
        self.assertEqual(JobSite(title='test', jobs=Statistics(total=0)),
                         JobSite(**{'title': 'test', 'jobs': None}))

    def test_jobs_frontend_none_dict(self):
        site = JobSite(**{'title': 'test'})
        statistics = Statistics(total=0)
        self.assertEqual(statistics, site.jobs)
        self.assertEqual(JobSite(title='test', jobs=statistics),
                         site)
