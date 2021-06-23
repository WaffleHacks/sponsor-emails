from click import style
from enum import Enum
from pydantic import BaseModel
import requests
import typing as t

from ..config import Config
from ..constants import MAILGUN_URL


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
    return [test_mailgun(cfg)]


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
