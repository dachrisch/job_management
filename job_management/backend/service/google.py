import json
from functools import lru_cache
from json import JSONDecodeError
from typing import Optional
from urllib.parse import urlencode

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


class GoogleCredentialsService(object):
    credentials: Credentials = Credentials(None)
    flow: Optional[Flow] = None

    def auth_url(self, redirect_url: str, next_url: str = '') -> str:
        self.flow = Flow.from_client_secrets_file('google.json', SCOPES,
                                                  redirect_uri=redirect_url + '?' + urlencode({'next_url': next_url}))
        return self.flow.authorization_url()[0]

    def authorize_code(self, code: str) -> None:
        self.flow.fetch_token(code=code)
        self.credentials = self.flow.credentials

        self.flow = None

    @lru_cache
    def get_user_info(self):
        user_info_service = build('oauth2', 'v2', credentials=self.credentials)
        user_info = user_info_service.userinfo().get().execute()
        return user_info

    @property
    def has_valid_credentials(self) -> bool:
        return self.credentials.valid

    def load_from_json(self, credentials_json: str):
        try:
            self.credentials = Credentials.from_authorized_user_info(json.loads(credentials_json), SCOPES)
        except JSONDecodeError:
            self.clear_credentials()

    def clear_credentials(self):
        self.credentials = Credentials(None)


SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive', 'openid',
          'https://www.googleapis.com/auth/userinfo.email']
