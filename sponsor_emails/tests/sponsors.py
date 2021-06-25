import gspread
from json import JSONDecodeError

from .result import Result
from .. import sheets
from ..config import Config

TEST_NAME = "sponsors"


def sponsors(cfg: Config) -> Result:
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
        # Open the worksheet
        sheet = gs.open_by_url(cfg.sponsors.url)
        worksheet = sheet.worksheet(cfg.sponsors.sheet)

        # Check the columns exist
        sheets.map_columns_to_headers(worksheet, cfg.sponsors.headers)
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 404:
            return Result.error(TEST_NAME, "sheet not found")

        error = e.response.json()
        return Result.error(TEST_NAME, error.get("message"))
    except gspread.exceptions.WorksheetNotFound:
        return Result.error(TEST_NAME, "worksheet not found")
    except sheets.MissingHeaderException as e:
        return Result.error(TEST_NAME, f'missing column header "{e.header}"')

    return Result.ok(TEST_NAME)
