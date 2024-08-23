import time
from datetime import datetime, timedelta
from threading import Thread

from rich.console import Console
from rich.progress import Progress

from job_offer_spider.db.job_offer import JobOfferDb


class SitesScannedProgressThread(Thread):
    def __init__(self, days_offset: int):
        super().__init__()
        self.days_offset = days_offset
        console = Console()
        self._l = console.print
        self.daemon = True

    def run(self):
        now = datetime.now()
        timestamp_threshold = (now - timedelta(days=self.days_offset)).timestamp()
        sites_to_scan = JobOfferDb().sites.count(
            {'$or': [{'last_scanned': {'$eq': None}}, {'last_scanned': {'$lt': timestamp_threshold}}]})
        with Progress() as p:
            task = p.add_task(f'Crawling [{sites_to_scan}] sites for job offers', total=sites_to_scan)
            while not p.finished:
                completed = JobOfferDb().sites.count({'last_scanned': {'$gt': now.timestamp()}})
                p.update(task, completed=completed)
                time.sleep(1)

        self._l(f'Found {JobOfferDb().jobs.size} jobs')
