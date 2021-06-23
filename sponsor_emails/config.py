from pathlib import Path
from pydantic import BaseModel, FilePath, HttpUrl, validator

from .constants import DEFAULT_CONFIG


def is_present(value: str) -> str:
    """
    Ensure that a string is present
    :param value: the string to validate
    :return: a valid string
    """
    if value == "":
        raise ValueError("must be present")
    return value


def load_config(p: Path) -> "Config":
    """
    Load configuration from the given path
    :param p: config path
    :return: loaded configuration
    """
    if not p.exists():
        p.write_text(DEFAULT_CONFIG)
    return Config.parse_file(p)


class Config(BaseModel):
    """
    The configuration for all of the program
    """

    credentials: "Credentials"
    sponsors: "Sponsors"
    template: "Template"


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


class Sponsors(BaseModel):
    url: HttpUrl = "https://docs.google.com/spreadsheets/d/your-sheet/edit"
    sheet: str = "Sponsorship Database"
    headers: "SponsorsHeaders"

    _sheet_is_present = validator("sheet", allow_reuse=True)(is_present)


class SponsorsHeaders(BaseModel):
    company_name: str = "Company Name"
    contact_name: str = "Contact Person"
    contact_email: str = "Contact Email"

    _is_present = validator("*", allow_reuse=True)(is_present)


class Template(BaseModel):
    url: HttpUrl = "https://docs.google.com/document/d/your-document/edit"
    placeholders: "TemplatePlaceholders"


class TemplatePlaceholders(BaseModel):
    company_name: str = "{COMPANY}"
    contact_name: str = "{RECIPIENT}"
    sender_name: str = "{SENDER}"

    _is_present = validator("*", allow_reuse=True)(is_present)


Config.update_forward_refs()
Sponsors.update_forward_refs()
Template.update_forward_refs()
