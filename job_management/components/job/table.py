import reflex as rx

from job_management.backend.entity.offer import JobOffer
from job_management.backend.state.job import JobState, JobPaginationState, JobsSortableState
from job_management.components.add_site_button import add_jobs_button
from job_management.components.crawl_button import scan_jobs_button
from job_management.components.job.buttons import apply_button
from job_management.components.pagination import pagination
from job_management.components.site.sort import sort_options
from job_management.components.table import header_cell


def show_job(job: JobOffer):
    return rx.table.row(
        rx.table.cell(rx.link(job.title, href=job.url, target='_blank')),
        rx.table.cell(rx.cond(job.added, rx.moment(job.added, from_now=True), rx.text('Never'))),
        rx.table.cell(rx.link(job.site_url, href=f'/jobs?site={job.site_url}', target='_self')),
        rx.table.cell(rx.hstack(
            rx.cond(job.state.analyzed, rx.badge(rx.icon('circle-check', size=18), 'Analyzed')),
            rx.cond(job.state.composed, rx.badge(rx.icon('circle-check', size=18), 'Composed')),
            rx.cond(job.state.stored, rx.badge(rx.icon('circle-check', size=18), 'Stored'))
        )),
        rx.table.cell(apply_button(job)),
        style={"_hover": {"bg": rx.color("gray", 3)}},
        align="center",
    )


def jobs_table():
    return rx.fragment(
        rx.flex(
            rx.hstack(
                add_jobs_button(),
                rx.spacer(),
                pagination(JobPaginationState),
                rx.spacer(),
                sort_options(JobsSortableState, JobOffer.sortable_fields()),
                spacing="3",
                wrap="wrap",
                width="100%",
                padding="1em",
                align="center"
            )
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    header_cell("Job Title", "briefcase"),
                    header_cell("Added", "list-plus"),
                    header_cell("Site", "building"),
                    header_cell("Status", "text-search"),
                    header_cell("Apply", "notebook-pen"),
                ),
            ),
            rx.table.body(rx.foreach(
                JobState.jobs,
                show_job
            )),
            variant="surface",
            size="3",
            width="100%",
        ),
    )
