from enum import Enum
from pydantic import BaseModel


class Direction(str, Enum):
    """
    The text direction of the paragraph/section. If unset, default to `LEFT_TO_RIGHT` since paragraph/section
    direction is not inherited.
    """

    UNSPECIFIED = "CONTENT_DIRECTION_UNSPECIFIED"
    LEFT_TO_RIGHT = "LEFT_TO_RIGHT"
    RIGHT_TO_LEFT = "RIGHT_TO_LEFT"


class Dimension(BaseModel):
    """A magnitude in a single direction in the specified units"""

    magnitude: float = 0
    unit: "Unit"


class Unit(str, Enum):
    """The units for magnitude"""

    UNSPECIFIED = "UNIT_UNSPECIFIED"
    POINT = "PT"


Dimension.update_forward_refs()
