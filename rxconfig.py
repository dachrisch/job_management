import os

import reflex as rx

config = rx.Config(
    app_name="job_management",
    api_url=os.getenv('JOB_API_URL', 'http://localhost:8000'),
)
