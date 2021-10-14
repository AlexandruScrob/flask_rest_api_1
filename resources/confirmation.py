import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailgunException
from resources.user import USER_NOT_FOUND
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema


confirmation_schema = ConfirmationSchema()


NOT_FOUND = "Confirmation reference not found"
EXPIRED = "The link has expired"
ALREADY_CONFIRMED = "Registration has already been confirmed"
RESEND_SUCCESSFUL = "Email confirmation successfully re-sent"
RESEND_FAIL = "Internal server error. Failed to resend confirmation email"


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """
        Return confirmation HTML page.
        :return:
        """
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {"message": NOT_FOUND}, 404

        if confirmation.expired:
            return {"message": EXPIRED}, 400

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html",
                            email=confirmation.user.email),
            200,
            headers
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """
        Returns confirmations for a given user. Use for testing
        :return:
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(
                        ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(cls, user_id: int):
        """
        Resend confirmation email
        :return:
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        try:
            confirmation = user.most_recent_confirmation

            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400

                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()

            return {"message": RESEND_SUCCESSFUL}, 201

        except MailgunException as ex:
            return {"message": str(ex)}, 500

        except Exception as ex:
            traceback.print_exc()
            return {"message": RESEND_FAIL + str(ex)}, 500
