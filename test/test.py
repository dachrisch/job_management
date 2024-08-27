from datetime import datetime
from typing import Any

import reflex as rx


# Assume you have an ORM like SQLAlchemy for database access.
# from your_database_module import session, JobSiteModel

class JobSite(rx.Base):
    title: str = ''
    url: str = ''
    num_jobs: int = 0
    last_scanned: datetime = None
    crawling: bool = False


class JobSiteState(rx.State):
    sites: list[JobSite] = []

    def fetch_sites(self):
        # Example query using SQLAlchemy. Replace with your actual database logic.
        # results = session.query(JobSiteModel).all()

        # Simulating database results for this example.
        results = [
            JobSite(title="Indeed", url="https://indeed.com", num_jobs=1500, last_scanned=datetime.now()),
            JobSite(title="LinkedIn", url="https://linkedin.com", num_jobs=1200, last_scanned=datetime.now()),
            JobSite(title="Glassdoor", url="https://glassdoor.com", num_jobs=800, last_scanned=datetime.now()),
        ]

        # Convert database models to the JobSite class
        self.sites = [JobSite(title=r.title, url=r.url, num_jobs=r.num_jobs, last_scanned=r.last_scanned) for r in
                      results]

    def crawl(self, site: dict[str,Any]):
        print(f'crawl {site}')
        for s in self.sites:
            if s.url == site['url']:
                s.crawling = True
                print(s)
                break


def job_site_table():
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell('Title'),
                rx.table.column_header_cell("URL"),
                rx.table.column_header_cell("Number of Jobs"),
                rx.table.column_header_cell("Last Scanned"),
                rx.table.column_header_cell("Crawlign"),
            )
        )
        ,
        rx.table.body(
            # Loop through the sites in the state to create rows.
            rx.foreach(JobSiteState.sites, lambda site: rx.table.row(
                rx.table.cell(site.title),
                rx.table.cell(rx.link(site.url, href=site.url, target="_blank")),  # Make the URL a clickable link
                rx.table.cell(site.num_jobs),
                rx.table.cell(site.last_scanned),
                rx.table.cell(rx.button(
                    site.title,
                    loading=site.crawling,
                    on_click=lambda: JobSiteState.crawl(site)
                )),
            ))
        ),
        on_mount=JobSiteState.fetch_sites
    )


def crawl_button(site, crawl_handler):
    return rx.button(
        site,
        on_click=lambda: crawl_handler(site)
    )


@rx.page('/')
def index():
    return rx.vstack(
        rx.text("Job Sites"),
        job_site_table(),
    )


# Run the app
app = rx.App()
