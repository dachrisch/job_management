import sys

import crochet
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet.pollreactor import install

from job_management.backend.service.container import Container


def wire():
    container = Container()
    container.init_resources()


def setup_scrapy():
    if "twisted.internet.reactor" not in sys.modules:
        configure_logging(get_project_settings(), install_root_handler=False)
        install()
        crochet.setup()
