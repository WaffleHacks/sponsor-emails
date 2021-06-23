import re

URL_ID_RE = re.compile(r"/document/d/([a-zA-Z0-9-_]+)")


class NoValidIdFound(Exception):
    """No valid id found in URL."""


def extract_document_id(url: str) -> str:
    """
    Extract the content id from a Google Docs/Sheets URL
    :param url: the full google docs url
    :return: the id of the content
    """
    url_id = URL_ID_RE.search(url)
    if url_id:
        return url_id.group(1)

    raise NoValidIdFound
