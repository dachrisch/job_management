from datetime import datetime

import reflex as rx


class JobOfferApplication(rx.Base):
    url: str = ''
    text: str = ''
    added: datetime = datetime.now()
