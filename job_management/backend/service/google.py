import json
import logging
from functools import lru_cache
from json import JSONDecodeError
from typing import Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


class CredentialsService:
    @property
    def has_valid_credentials(self) -> bool:
        return False


class GoogleCredentialsService(CredentialsService):
    credentials: Credentials = Credentials(None)
    flow: Optional[Flow] = None
    log = logging.getLogger(__name__)

    def auth_url(self, redirect_url: str, state: str) -> str:
        flow = Flow.from_client_secrets_file('google.json', SCOPES,
                                             redirect_uri=redirect_url, state=state)
        return flow.authorization_url(approval_prompt='force')[0]

    def authorize_code(self, code: str, redirect_url: str, state: str) -> None:
        flow = Flow.from_client_secrets_file('google.json', SCOPES,
                                             redirect_uri=redirect_url, state=state)
        flow.fetch_token(code=code)
        self.credentials = flow.credentials

    @lru_cache
    def get_user_info(self):
        user_info_service = self.load_service('oauth2', 'v2')
        user_info = user_info_service.userinfo().get().execute()
        return user_info

    @property
    def has_valid_credentials(self) -> bool:
        return self.credentials and self.credentials.valid

    def load_from_json(self, credentials_json: str):
        if credentials_json:
            try:
                self.credentials = Credentials.from_authorized_user_info(json.loads(credentials_json), SCOPES)
                if self.credentials.expired:
                    self.credentials.refresh(Request())
            except (JSONDecodeError, RefreshError):
                self.clear_credentials()
        self.log.info(f'Loading credentials from storage successful: {self.has_valid_credentials}')

    def clear_credentials(self):
        self.credentials = Credentials(None)

    def load_service(self, service_name: str, version: str):
        return self._load_service(service_name, version, self.credentials)

    @lru_cache
    def _load_service(self, service_name: str, version: str, credentials: Credentials):
        return build(service_name, version, credentials=credentials)


SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive', 'openid',
          'https://www.googleapis.com/auth/userinfo.email']
