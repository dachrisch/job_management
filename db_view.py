from typing import Any

import fire
from montydb import MontyCollection
from rich.console import Console

from job_offer_spider.db.job_offer import JobOfferDb


class DbViewerCli:
    def __init__(self):
        self._db = JobOfferDb()

    def sites(self):
        return DbCollectionViewer(self._db.sites.collection)

    def jobs(self):
        return DbCollectionViewer(self._db.jobs.collection)


class DbCollectionViewer:
    def __init__(self, collection: MontyCollection):
        self._collection = collection
        console = Console()
        self._l=console.print

    def find(self, condition: dict[str, Any]):
        self._l(list(self._collection.find(condition)))


if __name__ == '__main__':
    fire.Fire(DbViewerCli)
