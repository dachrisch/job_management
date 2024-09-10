import fire

from job_management import wire
from job_offer_spider.cli import JobOfferCli

if __name__ == '__main__':
    wire()
    fire.Fire(JobOfferCli)
