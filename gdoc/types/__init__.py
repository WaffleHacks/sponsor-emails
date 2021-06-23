from enum import Enum
from pydantic import BaseModel
import typing as t

from .styling import ParagraphStyle, NamedStyle, SectionStyle, TextStyle


class Document(BaseModel):
    """The representation of a returned document"""

    title: str
    body: "Body"
    namedStyles: "NamedStyles"
    revisionId: str
    suggestionsViewMode: "SuggestionsViewMode"
    documentId: str


class SuggestionsViewMode(str, Enum):
    """
    The possible suggestions view modes.

    - `DEFAULT_FOR_CURRENT_ACCESS` uses `SUGGESTIONS_INLINE` if the requester has edit access,
      otherwise it uses `PREVIEW_WITHOUT_SUGGESTIONS`
    - `SUGGESTIONS_INLINE` has document suggestions inline and differentiated from base content
    - `PREVIEW_SUGGESTIONS_ACCEPTED` has a preview with all suggested changes accepted
    - `PREVIEW_WITHOUT_SUGGESTIONS` has a preview with all suggested change rejected
    """

    DEFAULT_FOR_CURRENT_ACCESS = "DEFAULT_FOR_CURRENT_ACCESS"
    SUGGESTIONS_INLINE = "SUGGESTIONS_INLINE"
    PREVIEW_SUGGESTIONS_ACCEPTED = "PREVIEW_SUGGESTIONS_ACCEPTED"
    PREVIEW_WITHOUT_SUGGESTIONS = "PREVIEW_WITHOUT_SUGGESTIONS"


class Body(BaseModel):
    """The body of a document"""

    content: t.List["StructuralElement"]


class StructuralElement(BaseModel):
    """An element of the document describing part of the structure"""

    startIndex: int = 0
    endIndex: int
    paragraph: t.Optional["Paragraph"]
    sectionBreak: t.Optional["SectionBreak"]


class Paragraph(BaseModel):
    """
    A type of structural element representing a paragraph. A paragraph is a range of content terminated by a newline.
    """

    elements: t.List["ParagraphElement"]
    paragraphStyle: ParagraphStyle


class ParagraphElement(BaseModel):
    """
    Content within a paragraph
    """

    startIndex: int
    endIndex: int
    textRun: "TextRun"


class TextRun(BaseModel):
    """
    A run of text within a paragraph element that all has the same styling
    """

    content: str
    textStyle: TextStyle


class SectionBreak(BaseModel):
    """
    A structural element representing a section break. A section is a range of content which has the same
    `SectionStyle`. A section break always represents the start of a new section, and the section style applies to the
    section after the section break. The document body always begins with a section break.
    """

    sectionStyle: SectionStyle


class NamedStyles(BaseModel):
    """
    The named styles. Paragraphs in the document can inherit their `TextStyle` and `ParagraphStyle` from these named
    styles.
    """

    styles: t.List[NamedStyle]


Document.update_forward_refs()
Body.update_forward_refs()
StructuralElement.update_forward_refs()
Paragraph.update_forward_refs()
ParagraphElement.update_forward_refs()
