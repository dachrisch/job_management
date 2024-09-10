import os

import reflex as rx

api_url = os.getenv('JOB_API_URL', 'http://localhost:8000')
print(f'Running with backend at: {api_url}')
config = rx.Config(
    app_name="job_management",
    api_url=api_url,
)
