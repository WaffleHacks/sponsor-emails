from requests.auth import HTTPBasicAuth as __HTTPBasicAuth
from typing import Union as __Union

from .client import MailGun
from .errors import *


def authorize(
    credentials: __Union[__HTTPBasicAuth, str], domain: str, client_class=MailGun
):
    """
    Login to the MailGun API using the specified credentials
    :param credentials: the API key to login with
    :param domain: the sending domain
    :param client_class: the class to instantiate
    :return: `client_class` instance
    """
    return client_class(credentials, domain)
