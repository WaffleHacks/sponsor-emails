class MailGunException(Exception):
    """A generic MailGun exception"""

    def __init__(self, status: int):
        self.status = status


class DomainNotFoundException(MailGunException):
    """The specified domain could not be found"""


class UnauthorizedException(MailGunException):
    """The requester private key is invalid or is not allowed to access the domain"""
