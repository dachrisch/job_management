from datetime import datetime
from typing import Optional

import reflex as rx


class JobOfferApplication(rx.Base):
    url: str = ''
    text: str = ''
    added: datetime = datetime.now()
