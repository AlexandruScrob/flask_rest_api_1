# model = internal representation of an entity
from flask import request, url_for
from requests import Response, post

from db import db


# UserJSON = Dict[str, Union[int, str]]

MAILGUN_DOMAIN = "sandbox5f3364c574ac4c2aab7bf74b271e31db.mailgun.org"
MAILGUN_API_KEY = "31bcb17d53a98302058479048258bf07-2ac825a1-4c86950b"
FROM_TITLE = "Stores REST API"
FROM_EMAIL = ""


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def send_confirmation_email(self) -> Response:
        # http://127.0.0.1:5000 + /user_confirm/1
        link = request.url_root[:-1] +\
               url_for("userconfirm", user_id=self.id)

        return post(
            f"http:api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth={"api", MAILGUN_API_KEY},
            data={
                "from": f"{FROM_TITLE} <{FROM_EMAIL}>",
                "to": self.email,
                "subject": "Registration confirmation",
                "text": f"Please click the link to confirm your"
                        f" registration: {link}",
            },
        )
