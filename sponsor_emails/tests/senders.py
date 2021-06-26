import gspread
from json import JSONDecodeError
import typing as t

from .result import Result
from ..config import Config

TEST_NAME = "senders"


def senders(cfg: Config) -> Result:
    """
    Test authentication, check the sheet exists, and check the headers exist
    :param cfg: the configuration
    :return: status of the test
    """
    try:
        # Load the credentials
        gs = gspread.authorize(cfg.credentials.gcp())
    except (JSONDecodeError, KeyError, ValueError) as e:
        return Result.error(TEST_NAME, f"unable to load credentials: {e}")

    try:
        sheet = gs.open_by_url(cfg.senders.url)
        worksheet = sheet.worksheet(cfg.senders.sheet)

        # Check the column exist
        headers = worksheet.row_values(1)  # type: t.List[str]
        if cfg.senders.header not in headers:
            return Result.error(TEST_NAME, "header does not exist")
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 404:
            return Result.error(TEST_NAME, "sheet not found")

        error = e.response.json()
        return Result.error(TEST_NAME, error.get("message"))
    except gspread.exceptions.WorksheetNotFound:
        return Result.error(TEST_NAME, "worksheet not found")

    return Result.ok(TEST_NAME)
