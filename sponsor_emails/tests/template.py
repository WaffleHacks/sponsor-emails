import gdoc
from googleapiclient.errors import HttpError
from json import JSONDecodeError

from .result import Result
from ..config import Config

TEST_NAME = "template"


def template(cfg: Config) -> Result:
    """
    Test authentication, check the doc exists, and check the placeholders exist
    :param cfg: the configuration
    :return: status of the test
    """
    try:
        # Load the credentials
        gd = gdoc.authorize(cfg.credentials.gcp())
    except (JSONDecodeError, KeyError, ValueError) as e:
        return Result.error(TEST_NAME, f"unable to load credentials: {e}")

    try:
        # Open the document
        document = gd.open_by_url(cfg.template.url)

        # Check that placeholders are in document
        for key in cfg.template.placeholders.__fields__.keys():
            value = getattr(cfg.template.placeholders, key)
            if value not in document.text:
                return Result.error(TEST_NAME, f'missing placeholder for "{key}"')
    except HttpError as e:
        if e.status_code == 404:
            return Result.error(TEST_NAME, "document not found")
        elif e.status_code == 401 or e.status_code == 403:
            return Result.error(TEST_NAME, "unauthorized")
        else:
            return Result.error(
                TEST_NAME,
                f"unable to get document: ({e.status_code}) {e._get_reason()}",
            )
    except gdoc.NoValidIdFound:
        return Result.error(TEST_NAME, "invalid document url")

    return Result.ok(TEST_NAME)
