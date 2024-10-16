from typing import Any

import fire
from montydb import MontyCollection
from rich import json
from rich.console import Console

from job_management import wire
from job_management.backend.service.locator import Locator


class DbViewerCli:
    def __init__(self):
        self._db = Locator().job_management_db

    def sites(self):
        return DbCollectionViewer(self._db.sites.collection)

    def jobs(self):
        return DbCollectionViewer(self._db.jobs.collection)

    def jobs_body(self):
        return DbCollectionViewer(self._db.jobs_body.collection)


class DbCollectionViewer:
    def __init__(self, collection: MontyCollection):
        self._collection = collection
        console = Console()
        self._l = console.print

    def find(self, condition: dict[str, Any]):
        self._l(json.JSON.from_data([
            {key: value for key, value in item.items() if key != '_id'}
            for item in self._collection.find(condition)
        ]))

    def delete(self, condition: dict[str, Any]):
        deleted_result = self._collection.delete_many(condition)
        self._l(f'deleted {deleted_result.deleted_count} items')

    def update(self, condition: dict[str, Any], update_clause: dict[str, Any]):
        self._l(f"updated: {self._collection.update_many(condition, {'$set': update_clause}).modified_count} items")


if __name__ == '__main__':
    wire()
    fire.Fire(DbViewerCli)
