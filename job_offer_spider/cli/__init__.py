from job_offer_spider.cli.crawl import CrawlCli
from job_offer_spider.cli.jobs import JobsDbCli


class JobOfferCli:
    def __init__(self):
        self.jobs = JobsDbCli()
        self.crawl = CrawlCli()
