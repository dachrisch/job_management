import logging
from typing import Any, Union

from scrapy import Spider
from scrapy.http import Response
from scrapy.logformatter import LogFormatter, SCRAPEDMSG
from twisted.python.failure import Failure


class NoBodyLogFormatter(LogFormatter):
    pass
