from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']


class GoogleLoginService:
    _credentials: Credentials | None = None

    def auth_url(self, state: str, base_url: str) -> str:
        flow = Flow.from_client_secrets_file(
            'google.json', SCOPES, state=state,
            redirect_uri=f'{base_url}/google_login_callback'
        )
        url, state = flow.authorization_url()
        return url

    def on_callback(self, state: str, base_url: str, authorization_code: str):
        flow = Flow.from_client_secrets_file(
            'google.json', SCOPES, state=state,
            redirect_uri=f'{base_url}/google_login_callback'
        )
        flow.fetch_token(code=authorization_code)
        self._credentials = flow.credentials

    @property
    def is_logged_in(self):
        return self._credentials and self._credentials.valid
