# resource = external representation of an entity
import hmac
import traceback

from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity, get_jwt)
from flask_restful import Resource

from blacklist import BLACKLIST

from marshmallow import ValidationError

from libs.mailgun import MailgunException
from libs.strings import get_text
from models.user import UserModel
from schemas.user import UserSchema
from models.confirmation import ConfirmationModel


user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            # already created a user model inside python
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_email(user.email):
            return {'message': get_text("user_email_exists")}, 400

        if UserModel.find_by_username(user.username):
            return {'message': get_text("user_username_exits")}, 400

        try:
            user.save_to_db()

            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()

            user.send_confirmation_email()
            return {"message": get_text("user_registered")}, 201

        except MailgunException as ex:
            user.delete_from_db()  # rollback
            return {"message": "Failed to register user: " + str(ex)}, 500

        except Exception as ex:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()
            return {"message": get_text(
                "user_error_creating") + ": " + str(ex)}, 500


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': get_text("user_not_found")}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': get_text("user_not_found")}, 404

        user.delete_from_db()
        return {'message': get_text("user_deleted")}


class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json, partial=("email", ))
        except ValidationError as err:
            return err.messages, 400

        # find user in database
        user = UserModel.find_by_username(user_data.username)

        # check password
        if (user and user.password and
                hmac.compare_digest(user.password, user_data.password)):
            confirmation = user.most_recent_confirmation

            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id,
                                                   fresh=True)
                refresh_token = create_refresh_token(user.id)

                return {
                           'access_token': access_token,
                           'refresh_token': refresh_token
                       }, 200
            return {"message": get_text(
                "user_not_confirmed").format(user.email)}, 400

        return {'message': get_text("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        # jti is 'JWT ID', a unique identifier for a JWT
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': get_text("user_logged_out")}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)

        return {'access_token': new_token}
