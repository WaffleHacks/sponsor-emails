from enum import Enum
from pydantic import BaseModel
import typing as t

from .color import OptionalColor
from .units import Direction, Dimension


class TextStyle(BaseModel):
    """
    The styling that can be applied to text. Unset fields must be inherited from the paragraph's style.
    """

    strikethrough: t.Optional[bool]
    bold: t.Optional[bool]
    italic: t.Optional[bool]
    smallCaps: t.Optional[bool]
    underline: t.Optional[bool]
    fontSize: t.Optional[Dimension]
    link: t.Optional["Link"]
    weightedFontFamily: t.Optional["WeightedFontFamily"]
    baselineOffset: t.Optional["BaselineOffset"]
    backgroundColor: t.Optional[OptionalColor]
    foregroundColor: t.Optional[OptionalColor]

    def merge(self, style: "TextStyle") -> "TextStyle":
        """
        Merge two text styles together
        :param style: the style to merge with
        :return: a new combined style
        """
        result = self.copy()  # type: TextStyle

        for field in self.__fields__.keys():
            if getattr(result, field) is None:
                new = getattr(style, field)
                setattr(result, field, new)

        return result

    def apply(self, text: str) -> str:
        """
        Apply the text style to a piece of text using HTML
        :param text: the text to apply the style to
        :return: the formatted text
        """
        result = text
        css = ""

        # Add HTML properties
        if self.underline:
            result = f"<u>{result}</u>"
        if self.italic:
            result = f"<i>{result}</i>"
        if self.bold:
            result = f"<b>{result}</b>"
        if self.strikethrough:
            result = f"<s>{result}</s>"
        if self.link:
            result = f'<a href="{self.link.href}" target="_blank">{result}</a>'
        if self.smallCaps:
            result = f"<small>{result}</small>"
        if self.baselineOffset == BaselineOffset.SUBSCRIPT:
            result = f"<sub>{result}</sub>"
        if self.baselineOffset == BaselineOffset.SUPERSCRIPT:
            result = f"<sup>{result}</sup>"

        # Add CSS properties
        if self.fontSize:
            css += f"font-size: {self.fontSize.magnitude};"
        if self.weightedFontFamily:
            css += (
                f"font-weight: {self.weightedFontFamily.weight};"
                f'font-family: "{self.weightedFontFamily.fontFamily}", serif;'
            )
        if self.foregroundColor:
            if self.foregroundColor.color:
                color = self.foregroundColor.color.rgbColor
                css += f"color: rgb({color.red},{color.blue},{color.green});"
        if self.backgroundColor:
            if self.backgroundColor.color:
                color = self.backgroundColor.color.rgbColor
                css += f"background-color: rgb({color.red},{color.blue},{color.green});"

        # Add the CSS to a span if needed
        if css != "":
            result = f'<span style="{css}">{result}</span>'

        return result


class ParagraphStyle(BaseModel):
    """
    Style that applies to a whole paragraph. Unset fields must be inherited from elsewhere in the document. Where
    styles are inherited from depends on where the paragraph style is defined:

    - on a `Paragraph`, it inherits from the named style type
    - on a named style, it inherits from the normal text named style
    - on the normal text named style, it inherits from the default style in the Docs editor
    """

    indentStart: t.Optional[Dimension]
    keepWithNext: t.Optional[bool]
    indentFirstLine: t.Optional[Dimension]
    borderBetween: t.Optional["ParagraphBorder"]
    spacingMode: t.Optional["SpacingMode"]
    avoidWidowAndOrphan: t.Optional[bool]
    namedStyleType: "NamedStyleType"
    borderLeft: t.Optional[dict]
    keepLinesTogether: t.Optional[bool]
    borderTop: t.Optional["ParagraphBorder"]
    spaceAbove: t.Optional[Dimension]
    spaceBelow: t.Optional[Dimension]
    direction: Direction = Direction.LEFT_TO_RIGHT
    headingId: t.Optional[str]
    borderRight: t.Optional["ParagraphBorder"]
    shading: t.Optional["Shading"]
    indentEnd: t.Optional[Dimension]
    alignment: t.Optional["Alignment"]
    borderBottom: t.Optional["ParagraphBorder"]
    lineSpacing: t.Optional[float]
    tabStops: t.Optional[t.List["TabStop"]]


class SectionStyle(BaseModel):
    """The styling that applies to a section."""

    columnSeparatorStyle: "ColumnSeparatorStyle"
    contentDirection: Direction = Direction.LEFT_TO_RIGHT
    sectionType: "SectionType"


class NamedStyle(BaseModel):
    """
    A named style. Paragraphs in the document can inherit their `TextStyle` and `ParagraphStyle` from this named style
    when they have the same named style type.
    """

    paragraphStyle: ParagraphStyle
    namedStyleType: "NamedStyleType"
    textStyle: TextStyle


class NamedStyleType(str, Enum):
    """The named style of the paragraph"""

    UNSPECIFIED = "NAMED_STYLE_TYPE_UNSPECIFIED"
    NORMAL_TEXT = "NORMAL_TEXT"
    TITLE = "TITLE"
    SUBTITLE = "SUBTITLE"
    HEADING_1 = "HEADING_1"
    HEADING_2 = "HEADING_2"
    HEADING_3 = "HEADING_3"
    HEADING_4 = "HEADING_4"
    HEADING_5 = "HEADING_5"
    HEADING_6 = "HEADING_6"


class ColumnSeparatorStyle(str, Enum):
    """
    The style of column separators. The style can be set even when there is one column in the section.
    """

    UNSPECIFIED = "COLUMN_SEPARATOR_STYLE_UNSPECIFIED"
    NONE = "NONE"
    BETWEEN_EACH_COLUMN = "BETWEEN_EACH_COLUMN"


class SectionType(str, Enum):
    """The type of section"""

    UNSPECIFIED = "SECTION_TYPE_UNSPECIFIED"
    CONTINUOUS = "CONTINUOUS"
    NEXT_PAGE = "NEXT_PAGE"


class Link(BaseModel):
    """
    A reference to another portion of a document or an external resource.
    """

    bookmarkId: t.Optional[str]
    headingId: t.Optional[str]
    url: t.Optional[str]

    @property
    def href(self) -> str:
        """Get the link"""
        if self.bookmarkId is not None:
            return self.bookmarkId
        elif self.headingId is not None:
            return self.headingId
        elif self.url is not None:
            return self.url
        else:
            return ""


class WeightedFontFamily(BaseModel):
    """Represents a font family and weight of text"""

    fontFamily: str
    weight: int


class BaselineOffset(str, Enum):
    """
    The text's vertical offset from its normal position. Text with `SUPERSCRIPT` or `SUBSCRIPT` baseline offsets is
    automatically rendered in a smaller font size, computed based on the `font_size`. The `font_size` itself is not
    affected by changes in this field.
    """

    UNSPECIFIED = "BASELINE_OFFSET_UNSPECIFIED"
    NONE = "NONE"
    SUPERSCRIPT = "SUPERSCRIPT"
    SUBSCRIPT = "SUBSCRIPT"


class SpacingMode(str, Enum):
    """The spacing mode for the paragraph"""

    UNSPECIFIED = "SPACING_MODE_UNSPECIFIED"
    NEVER_COLLAPSE = "NEVER_COLLAPSE"
    COLLAPSE_LISTS = "COLLAPSE_LISTS"


class Alignment(str, Enum):
    """The text alignment for this paragraph"""

    UNSPECIFIED = "ALIGNMENT_UNSPECIFIED"
    START = "START"
    CENTER = "CENTER"
    END = "END"
    JUSTIFIED = "JUSTIFIED"


class ParagraphBorder(BaseModel):
    """A border around a paragraph"""

    color: OptionalColor
    width: Dimension
    dashStyle: "DashStyle"
    padding: Dimension


class DashStyle(str, Enum):
    """The style of the border"""

    UNSPECIFIED = "DASH_STYLE_UNSPECIFIED"
    SOLID = "SOLID"
    DOT = "DOT"
    DASH = "DASH"


class Shading(BaseModel):
    """The background color of this paragraph shading"""

    backgroundColor: OptionalColor


class TabStop(BaseModel):
    """A tab stop within a paragraph"""

    alignment: Alignment
    offset: Dimension


SectionStyle.update_forward_refs()
ParagraphStyle.update_forward_refs()
ParagraphBorder.update_forward_refs()
NamedStyle.update_forward_refs()
TextStyle.update_forward_refs()
