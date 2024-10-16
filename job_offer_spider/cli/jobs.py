from rich import box
from rich.console import Console
from rich.table import Table

from job_management.backend.service.locator import Locator


class JobsDbCli:
    def __init__(self):
        self._db = Locator().job_management_db
        console = Console()
        self._l = console.print
        self._spinner = console.status

    def print(self):
        table = Table(title='Job Offers', show_edge=False, highlight=True, box=box.HORIZONTALS)
        table.add_column('Title', style='yellow')
        table.add_column('Link', style='bright_blue')
        with self._spinner('retrieving jobs'):
            for job in self._db.jobs.all():
                table.add_row(job.title, job.url)
            self._l(table)
