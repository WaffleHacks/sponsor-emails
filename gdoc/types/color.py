from pydantic import BaseModel
import typing as t


class OptionalColor(BaseModel):
    """A color that can be either fully opaque or fully transparent"""

    color: t.Optional["Color"]


class Color(BaseModel):
    """A solid color"""

    rgbColor: t.Optional["RgbColor"]


class RgbColor(BaseModel):
    """An RGB color"""

    red: float = 0
    blue: float = 0
    green: float = 0


OptionalColor.update_forward_refs()
Color.update_forward_refs()
