from .client import Client
from .types import Document
from .utils import NoValidIdFound


def authorize(credentials, client_class=Client):
    """
    Login to the Google API using OAuth2 credentials.
    This is a shortcut function which instantiates `client_class`. By default :class:`gdoc.Client` is used.
    :param credentials: Google OAuth2 credentials
    :param client_class: the class to instantiate
    :return: `client_class` instance
    """
    return client_class(credentials)
