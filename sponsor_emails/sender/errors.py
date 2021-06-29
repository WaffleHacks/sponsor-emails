class SendException(Exception):
    """An exception occurring while attempting to send emails"""

    def __init__(self, message):
        self.message = message


class CredentialsException(SendException):
    """Failed to authenticate or load credentials"""


class NotFoundException(SendException):
    """Failed to find a document or sheet"""
