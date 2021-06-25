import mailgun as mailgun_client
import requests

from .result import Result
from ..config import Config

TEST_NAME = "mailgun"


def mailgun(cfg: Config) -> Result:
    """
    Test authentication and check if the domain exists for MailGun
    :param cfg: the configuration
    :return: status of the test
    """
    try:
        mg = mailgun_client.authorize(
            cfg.credentials.mailgun(), cfg.credentials.mailgun_domain
        )
        info = mg.info()

        # Ensure the domain is not disabled
        if info.domain.is_disabled:
            return Result.error(TEST_NAME, "domain disabled")

        # Ensure the domain is properly configured
        if info.domain.state != "active":
            return Result.error(
                TEST_NAME,
                f'domain improperly configured (currently: "{info.domain.state}")',
            )
    except mailgun_client.DomainNotFoundException:
        return Result.error(TEST_NAME, "domain not found")
    except mailgun_client.UnauthorizedException:
        return Result.error(TEST_NAME, "invalid primary key")
    except mailgun_client.MailGunException as e:
        return Result.error(
            TEST_NAME, f"an internal server error ({e.status}) occurred"
        )
    except requests.RequestException as e:
        return Result.error(TEST_NAME, str(e))

    return Result.ok(TEST_NAME)
