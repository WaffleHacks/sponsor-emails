from googleapiclient.discovery import build
import typing as t

from .auth import convert_credentials
from .types import Document, SuggestionsViewMode
from .utils import extract_document_id


class Client(object):
    """A light-weight, typed wrapper around the Google Docs API"""

    def __init__(self, auth: t.Any):
        credentials = convert_credentials(auth)
        self.service = build("docs", "v1", credentials=credentials)

    def open(
        self,
        document_id: str,
        view_mode: SuggestionsViewMode = SuggestionsViewMode.DEFAULT_FOR_CURRENT_ACCESS,
    ) -> Document:
        """
        Open a document by its ID
        :param document_id: the document id
        :param view_mode: how to open the document
        :return: the document data
        """
        raw = (
            self.service.documents()
            .get(documentId=document_id, suggestionsViewMode=view_mode.value)
            .execute()
        )
        return Document.parse_obj(raw)

    def open_by_url(
        self,
        url: str,
        view_mode: SuggestionsViewMode = SuggestionsViewMode.DEFAULT_FOR_CURRENT_ACCESS,
    ) -> Document:
        """
        Open a document by its full URL
        :param url: the URL to the document
        :param view_mode: how to open the document
        :return: the document data
        """
        return self.open(extract_document_id(url), view_mode)
