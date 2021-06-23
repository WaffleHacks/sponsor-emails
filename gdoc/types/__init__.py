from enum import Enum
from pydantic import BaseModel, PrivateAttr
import typing as t

from .styling import ParagraphStyle, NamedStyle, NamedStyleType, SectionStyle, TextStyle


class Document(BaseModel):
    """The representation of a returned document"""

    title: str
    body: "Body"
    namedStyles: "NamedStyles"
    revisionId: str
    suggestionsViewMode: "SuggestionsViewMode"
    documentId: str

    _text: t.Optional[str] = PrivateAttr(default=None)
    _html: t.Optional[str] = PrivateAttr(default=None)

    @property
    def text(self) -> str:
        """Get the document as plaintext"""
        if self._text is None:
            self.__extract_content()
        return self._text

    @property
    def html(self) -> str:
        """Get the document as HTML"""
        if self._html is None:
            self.__extract_content()
        return self._html

    def __extract_content(self):
        """
        Get the content from the document
        """
        text = ""
        html = ""

        styles = self.namedStyles.style_map

        for structural_element in self.body.content:
            # Ignore section breaks
            if structural_element.paragraph is None:
                continue

            # Get the parent style
            paragraph = structural_element.paragraph
            paragraph_style = styles[paragraph.paragraphStyle.namedStyleType]

            # Add the content
            html_segment = "<p>"
            for element in paragraph.elements:
                content = element.textRun.content
                text_style = element.textRun.textStyle.merge(paragraph_style.textStyle)

                text += content
                html_segment += text_style.apply(content).replace("\n", "<br>")

            html += html_segment + "</p>"

        self._text = text
        self._html = html


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

    _style_map: t.Dict[NamedStyleType, NamedStyle] = PrivateAttr(default={})

    @property
    def style_map(self) -> t.Dict[NamedStyleType, NamedStyle]:
        """A map from style type to style"""
        if len(self._style_map) == 0:
            for style in self.styles:
                self._style_map[style.namedStyleType] = style

        return self._style_map


Document.update_forward_refs()
Body.update_forward_refs()
StructuralElement.update_forward_refs()
Paragraph.update_forward_refs()
ParagraphElement.update_forward_refs()
