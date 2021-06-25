import requests


from .result import Result
from ..config import Config
from ..constants import MAILGUN_URL


def mailgun(cfg: Config) -> Result:
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
