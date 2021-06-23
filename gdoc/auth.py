from google.auth.credentials import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

OAUTH2CLIENT_CREDENTIALS = [
    "OAuth2Credentials",
    "AccessTokenCredentials",
    "GoogleCredentials",
]
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def convert_credentials(credentials) -> Credentials:
    """
    Convert from oauth2client credentials to google-auth credentials if needed.
    :param credentials: the original credentials
    :return: google-auth credentials
    """
    module = credentials.__module__
    cls = credentials.__class__.__name__

    if "oauth2client" in module and cls == "ServiceAccountCredentials":
        return _convert_service_account(credentials)
    elif "oauth2client" in module and cls in OAUTH2CLIENT_CREDENTIALS:
        return _convert_oauth(credentials)
    elif isinstance(credentials, Credentials):
        return credentials

    raise TypeError(
        "Credentials need to be from either oauth2client or from google-auth"
    )


def _convert_oauth(credentials) -> Credentials:
    return UserCredentials(
        credentials.access_token,
        credentials.refresh_token,
        credentials.id_token,
        credentials.token_uri,
        credentials.client_id,
        credentials.client_secret,
        credentials.scopes,
    )


def _convert_service_account(credentials) -> Credentials:
    data = credentials.serialization_data
    data["token_uri"] = credentials.token_uri
    scopes = credentials._scopes.split() or DEFAULT_SCOPES

    return ServiceAccountCredentials.from_service_account_info(data, scopes=scopes)
