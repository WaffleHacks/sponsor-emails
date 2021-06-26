from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from pathlib import Path
from pydantic import BaseModel, EmailStr, FilePath, HttpUrl, validator
import re
from requests.auth import HTTPBasicAuth

from .constants import DEFAULT_CONFIG, SCOPES

GOOGLE_DRIVE_RE = re.compile(r"^/(document|spreadsheets)/d/[a-zA-Z0-9-_]+(/\w+)?")


def is_present(value: str) -> str:
    """
    Ensure that a string is present
    :param value: the string to validate
    :return: a valid string
    """
    if value == "":
        raise ValueError("must be present")
    return value


def is_google_drive(value: HttpUrl) -> HttpUrl:
    """
    Ensure that a URL is a Google Drive URL
    :param value: the url to validate
    :return: a valid URL
    """
    if value.host != "docs.google.com" or not GOOGLE_DRIVE_RE.fullmatch(value.path):
        raise ValueError("must be a Google Docs URL")
    return value


class Config(BaseModel):
    """
    The configuration for all of the program
    """

    credentials: "Credentials"
    senders: "Senders"
    sponsors: "Sponsors"
    template: "Template"

    @staticmethod
    def load(p: Path) -> "Config":
        """
        Load configuration from the given path
        :param p: config path
        :return: loaded configuration
        """
        if not p.exists():
            p.write_text(DEFAULT_CONFIG)
        return Config.parse_file(p)


class Credentials(BaseModel):
    gcp_service_account: FilePath = "./service-account.json"
    mailgun_domain: str
    mailgun_api_key: str

    _is_present_mailgun_domain = validator("mailgun_domain", allow_reuse=True)(
        is_present
    )
    _is_present_mailgun_api_key = validator("mailgun_api_key", allow_reuse=True)(
        is_present
    )

    def gcp(self) -> ServiceAccountCredentials:
        """
        Get authentication information for GCP
        """
        full_path = self.gcp_service_account.resolve()
        return ServiceAccountCredentials.from_service_account_file(
            str(full_path), scopes=SCOPES
        )

    def mailgun(self) -> HTTPBasicAuth:
        """
        Get authentication information for the MailGun API
        """
        return HTTPBasicAuth("api", self.mailgun_api_key)


class Senders(BaseModel):
    url: HttpUrl = "https://docs.google.com/spreadsheets/d/your-senders-sheet/edit"
    sheet: str = "Organizers"
    reply_to: EmailStr = "sponsors@your.domain"
    header: str = "Name"

    _sheet_is_present = validator("sheet", allow_reuse=True)(is_present)
    _url_is_google_drive = validator("url", allow_reuse=True)(is_google_drive)


class Sponsors(BaseModel):
    url: HttpUrl = "https://docs.google.com/spreadsheets/d/your-sponsors-sheet/edit"
    sheet: str = "Sponsorship Database"
    headers: "SponsorsHeaders"

    _sheet_is_present = validator("sheet", allow_reuse=True)(is_present)
    _url_is_google_drive = validator("url", allow_reuse=True)(is_google_drive)


class SponsorsHeaders(BaseModel):
    company_name: str = "Company Name"
    contact_name: str = "Contact Person"
    contact_email: str = "Contact Email"

    _is_present = validator("*", allow_reuse=True)(is_present)


class Template(BaseModel):
    url: HttpUrl = "https://docs.google.com/document/d/your-document/edit"
    placeholders: "TemplatePlaceholders"

    _url_is_google_drive = validator("url", allow_reuse=True)(is_google_drive)


class TemplatePlaceholders(BaseModel):
    company_name: str = "{COMPANY}"
    contact_name: str = "{RECIPIENT}"
    sender_name: str = "{SENDER}"

    _is_present = validator("*", allow_reuse=True)(is_present)


Config.update_forward_refs()
Sponsors.update_forward_refs()
Template.update_forward_refs()
