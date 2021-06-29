import gspread
import typing as t

from .config import SponsorsHeaders


class MissingHeaderException(Exception):
    """An expected header was missing"""

    def __init__(self, header: str):
        self.header = header


def index_to_label(index: int) -> str:
    """
    Map an column index to a label
    :param index: the index
    :return: the resulting label
    """
    letter = chr(65 + (index % 26))
    return letter * ((index // 26) + 1)


def map_columns_to_headers(
    worksheet: gspread.Worksheet, names: SponsorsHeaders
) -> SponsorsHeaders:
    """
    Map the column headers to columns
    :param worksheet: the worksheet to search
    :param names: the names of the columns from the config
    :return: a mapping from column to column name
    """
    mapping = {}

    headers = worksheet.row_values(1)  # type: t.List[str]
    for header in names.__fields__.keys():
        name = getattr(names, header)

        # Ensure the header exists
        if name not in headers:
            raise MissingHeaderException(header)

        # Get the column label
        mapping[header] = index_to_label(headers.index(name))

    return SponsorsHeaders.parse_obj(mapping)


def fetch_data(
    worksheet: gspread.Worksheet, columns: t.List[str], single: bool = False
) -> t.Dict[str, t.List[str]]:
    """
    Fetch the specified ranges of data and clean the values
    :param worksheet: the worksheet to fetch from
    :param columns: the columns of data to fetch
    :param single: only fetch a single row
    :return: cleaned data with an array per range
    """
    # Fetch the data
    row_count = 2 if single else worksheet.row_count
    ranges = [f"{column}2:{column}{row_count}" for column in columns]
    raw = worksheet.batch_get(ranges)

    # Clean the data
    cleaned = {}
    for i, raw_column in enumerate(raw):
        column = []
        for item in raw_column:
            if len(item) == 0:
                column.append(None)
            else:
                column.append(item[0])
        cleaned[columns[i]] = column

    return cleaned
