from click import style
from enum import Enum
from googleapiclient.errors import HttpError
import gdoc
import gspread
from json import JSONDecodeError
from pydantic import BaseModel
import requests
import typing as t

from ..config import Config
from ..constants import MAILGUN_URL

TEST_DATA = {
    "company_name": "TEST_COMPANY",
    "contact_name": "TEST_CONTACT",
    "sender_name": "TEST_SENDER",
}


class Status(str, Enum):
    ok = style("OK", fg="green")
    error = style("ERROR", fg="red", bold=True)


class Result(BaseModel):
    status: Status
    component: str
    error_message: t.Optional[str]

    @classmethod
    def ok(cls, component: str) -> "Result":
        return cls(status=Status.ok, component=component)

    @classmethod
    def error(cls, component: str, error: str) -> "Result":
        return cls(
            status=Status.error,
            component=component,
            error_message=style(error, fg="yellow"),
        )

    def __str__(self):
        error = f"\n\t{self.error_message}" if self.error_message else ""
        return f"{self.status.value}: {self.component}{error}"


def validate(cfg: Config) -> t.List[Result]:
    return [test_mailgun(cfg), test_sheets(cfg), test_docs(cfg)]


def test_mailgun(cfg: Config) -> Result:
    """
    Test authentication and check if the domain exists for MailGun
    :param cfg: the configuration
    :return: status of the test
    """
    try:
        response = requests.get(
            MAILGUN_URL + "/domains/" + cfg.credentials.mailgun_domain,
            auth=cfg.credentials.mailgun(),
        )

        # Status code based checks
        if response.status_code == 404:
            return Result.error("mailgun", "domain not found")
        elif response.status_code == 401:
            return Result.error("mailgun", "invalid private key")
        elif response.status_code >= 500:
            return Result.error("mailgun", "internal server error")

        domain = response.json().get("domain")

        # Ensure the domain is not disabled
        if domain.get("is_disabled"):
            return Result.error("mailgun", "domain disabled")

        # Ensure the domain is properly configured
        state = domain.get("state")
        if state != "active":
            return Result.error(
                "mailgun",
                f'domain improperly configured (currently: "{state}")',
            )
    except requests.RequestException as e:
        return Result.error("mailgun", str(e))

    return Result.ok("mailgun")


def test_sheets(cfg: Config) -> Result:
    """
    Test authentication, check the sheet exists, and check the headers exist
    :param cfg: the configuration
    :return: status of the test
    """
    try:
        # Load the credentials
        gs = gspread.authorize(cfg.credentials.gcp())
    except (JSONDecodeError, KeyError, ValueError) as e:
        return Result.error("google_sheets", f"unable to load credentials: {e}")

    try:
        # Open the sheet
        sheet = gs.open_by_url(cfg.sponsors.url)

        # Find the worksheet
        worksheet = sheet.worksheet(cfg.sponsors.sheet)

        # Check the headers exist
        values = worksheet.row_values(1)
        for header in cfg.sponsors.headers.__fields__.keys():
            if getattr(cfg.sponsors.headers, header) not in values:
                return Result.error("google_sheets", f"cannot find {header} column")
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 404:
            return Result.error("google_sheets", "sheet not found")

        error = e.response.json()
        return Result.error("google_sheets", error.get("message"))
    except gspread.exceptions.WorksheetNotFound:
        return Result.error("google_sheets", "worksheet not found")

    return Result.ok("google_sheets")


def test_docs(cfg: Config) -> Result:
    """
    Test authentication, check the doc exists, and check the placeholders exist
    :param cfg: the configuration
    :return: status of the test
    """
    try:
        # Load the credentials
        gd = gdoc.authorize(cfg.credentials.gcp())
    except (JSONDecodeError, KeyError, ValueError) as e:
        return Result.error("google_docs", f"unable to load credentials: {e}")

    try:
        # Open the document
        document = gd.open_by_url(cfg.template.url)

        # Check that placeholders are in document
        for key in cfg.template.placeholders.__fields__.keys():
            value = getattr(cfg.template.placeholders, key)
            if value not in document.text:
                return Result.error("google_docs", f'missing placeholder for "{key}"')
    except HttpError as e:
        if e.status_code == 404:
            return Result.error("google_docs", "document not found")
        elif e.status_code == 401 or e.status_code == 403:
            return Result.error("google_docs", "unauthorized")
        else:
            return Result.error(
                "google_docs",
                f"unable to get document: ({e.status_code}) {e._get_reason()}",
            )
    except gdoc.utils.NoValidIdFound:
        return Result.error("google_docs", "invalid document url")

    return Result.ok("google_docs")
