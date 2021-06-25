import gspread
from json import JSONDecodeError

from .result import Result
from ..config import Config


def sheets(cfg: Config) -> Result:
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
