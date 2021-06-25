import requests
from requests.auth import HTTPBasicAuth
import typing as t

from .errors import *
from .types import Domain

BASE_URL = "https://api.mailgun.net/v3"


class MailGun(object):
    """A light-weight, typed wrapper around the MailGun v3 API"""

    def __init__(self, auth: t.Union[HTTPBasicAuth, str], domain: str):
        if isinstance(auth, str):
            auth = HTTPBasicAuth("api", auth)

        self.domain = domain
        self.session = requests.Session()
        self.session.auth = auth

    @staticmethod
    def __check_status(response: requests.Response):
        """
        Raise an error if an invalid status code is encountered
        :param response: the response information
        """
        if response.status_code == 404:
            raise DomainNotFoundException(response.status_code)
        elif response.status_code == 401:
            raise UnauthorizedException(response.status_code)
        elif response.status_code >= 500:
            raise MailGunException(response.status_code)

    def info(self) -> Domain:
        """Get information about the current domain"""
        response = self.session.get(f"{BASE_URL}/domains/{self.domain}")
        self.__check_status(response)
        return Domain.parse_obj(response.json())

    def send(
        self,
        from_: str,
        to: t.List[str],
        subject: str,
        text: str,
        html: str = None,
        files: t.List[t.BinaryIO] = None,
    ):
        """
        Send a MIME email
        :param from_: who the email is from
        :param to: the email recipient(s)
        :param subject: the email subject
        :param text: the plaintext content
        :param html: optional HTML content (if the recipient client supports it)
        :param files: attachments to the message
        """
        # Construct the attachments
        attachments = []
        if files is not None:
            attachments = [("attachment", file.read()) for file in files]

        # Construct the body
        body = {"from": from_, "to": ",".join(to), "subject": subject, "text": text}
        if html:
            body["html"] = html

        # Send the request
        response = self.session.post(
            f"{BASE_URL}/{self.domain}/messages", files=attachments, data=body
        )
        self.__check_status(response)
