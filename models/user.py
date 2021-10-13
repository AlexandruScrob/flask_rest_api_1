# model = internal representation of an entity
from flask import request, url_for
from requests import Response

from db import db
from libs.mailgun import Mailgun

# UserJSON = Dict[str, Union[int, str]]


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

        subject = "Registration confirmation"
        text = f"Please click the link to confirm your registration: {link}"
        html = f'<html>Please click the link to confirm your registration:" \
               f"<a href="{link}">{link}</a></html>'

        return Mailgun.send_email(self.email, subject, text, html)

