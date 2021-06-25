from pydantic import BaseModel


class Domain(BaseModel):
    """
    All information about a domain. Only includes information that is retrieved by `sponsor_emails`.
    """

    domain: "Status"


class Status(BaseModel):
    """The current status of the domain"""

    is_disabled: bool
    state: str


Domain.update_forward_refs()
