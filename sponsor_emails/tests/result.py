from click import style
from enum import Enum
from pydantic import BaseModel
import typing as t


class Status(str, Enum):
    ok = style("OK", fg="green")
    error = style("ERROR", fg="red", bold=True)


class Result(BaseModel):
    status: Status
    component: str
    error_message: t.Optional[str]

    @classmethod
    def ok(cls, component: str) -> "Result":
        return cls(status=Status.ok, component=component)

    @classmethod
    def error(cls, component: str, error: str) -> "Result":
        return cls(
            status=Status.error,
            component=component,
            error_message=style(error, fg="yellow"),
        )

    def __str__(self):
        error = f"\n\t{self.error_message}" if self.error_message else ""
        return f"{self.status.value}: {self.component}{error}"
