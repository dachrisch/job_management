import logging
from typing import Any, Union

from scrapy import Spider
from scrapy.http import Response
from scrapy.logformatter import LogFormatter, SCRAPEDMSG
from twisted.python.failure import Failure


class NoBodyLogFormatter(LogFormatter):
    def scraped(
            self, item: Any, response: Union[Response, Failure], spider: Spider
    ) -> dict:
        """Logs a message when an item is scraped by a spider."""
        src: Any
        if isinstance(response, Failure):
            src = response.getErrorMessage()
        else:
            src = response
        return {
            "level": logging.DEBUG,
            "msg": SCRAPEDMSG,
            "args": {
                "src": src,
                "item": self.cap_item_fields(item),
            },
        }

    def cap_item_fields(self, item: dict[str,Any], max_length=50):
        capped_item = {}
        for f in item.keys():
            if len(item[f]) > max_length:
                capped_item[f] = f'{item[f][:max_length]}<{len(item[f]) - max_length} characters more>'
            else:
                capped_item[f] = item[f]
        return capped_item
