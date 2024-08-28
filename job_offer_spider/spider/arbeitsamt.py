import json
from typing import override, Any, Iterable
from urllib.parse import parse_qs, urlunparse, urlencode

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.utils.url import parse_url

from job_offer_spider.item.spider.target_website import TargetWebsiteSpiderItem


def jobsuche_url(query, page: int = 1, size: int = 2):
    return f'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs?angebotsart=1&was={query}&page={page}&size={size}&pav=false&facetten=false'


class ArbeitsamtSpider(Spider):
    """
    https://jobsuche.api.bund.dev/
    """
    name = 'arbeitsamt'
    start_urls = [
        jobsuche_url('coach', 1, 50)]
    details_url = 'https://rest.arbeitsagentur.de/vermittlung/ag-darstellung-service/pc/v1/arbeitgeberdarstellung'
    headers = {'Accept': 'application/json', 'X-API-Key': 'jobboerse-jobsuche'}

    @override
    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url, headers=self.headers)

    @override
    def parse(self, response: Response, **kwargs: Any) -> Any:
        yield self.next_page(response)
        response_json = json.loads(response.text)
        if 'stellenangebote' in response_json:
            for job_offer in response_json.get('stellenangebote'):
                if 'kundennummerHash' in job_offer:
                    yield Request(f'{self.details_url}/{job_offer.get("kundennummerHash")}', headers=self.headers,
                                  callback=self.parse_ag)

    def next_page(self, response) -> Request | None:
        response_json = json.loads(response.text)
        total = int(response_json.get('maxErgebnisse'))
        page = int(response_json.get('page'))
        size = int(response_json.get('size'))
        if page * size + size < total:
            parsed_url = parse_url(response.url)
            query_params = parse_qs(parsed_url.query)
            query_params['page'] = [f'{page + 1}']
            next_page_url = urlunparse(parsed_url._replace(query=urlencode(query_params, doseq=True)))
            return Request(str(next_page_url), headers=self.headers)

    def parse_ag(self, response: Response):
        response_json = json.loads(response.text)
        company_name = response_json.get('firma')
        if 'links' in response_json:
            for link in response_json.get('links'):
                parsed_url = parse_url(link['url'])
                if company_name and link:
                    yield TargetWebsiteSpiderItem(title=company_name, url=f'{parsed_url.scheme}://{parsed_url.netloc}')
