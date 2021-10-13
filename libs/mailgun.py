import os
from typing import List
from requests import Response, post


FAILED_LOAD_API_KEY = "Failed to load Mailgun API Key"
FAILED_LOAD_DOMAIN = "Failed to load Mailgun Domain"
ERROR_SENDING_EMAIL = "Error in sending confirmation email"


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = "postmaster@sandbox5f3364c574ac4c2aab7bf74b271e31" \
                 "db.mailgun.org"

    @classmethod
    def send_email(cls, email: List[str], subject: str,
                   text: str, html: str) -> Response:

        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(FAILED_LOAD_API_KEY)

        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException(FAILED_LOAD_DOMAIN)

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html
            },
        )

        if response.status_code != 200:
            raise MailgunException(ERROR_SENDING_EMAIL)

        return response
