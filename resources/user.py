# resource = external representation of an entity
import hmac

from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity, get_jwt)
from flask_restful import Resource

from blacklist import BLACKLIST

from marshmallow import ValidationError
from models.user import UserModel
from schemas.user import UserSchema


FILED_REQUIRED = "{} required"
USER_NAME_ALREADY_EXISTS = "User with that username already exists"
USER_CREATED = 'User created successfully.'
USER_NOT_FOUND = 'User not found'
USER_DELETED = 'User deleted'
INVALID_CREDENTIALS = "Invalid credentials"
USER_LOGOUT = 'Successfully logged out'


user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            # already created a user model inside python
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username):
            return {'message': USER_NAME_ALREADY_EXISTS}, 400

        user.save_to_db()

        return {'message': USER_CREATED}, 200


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': USER_NOT_FOUND}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': USER_NOT_FOUND}, 404

        user.delete_from_db()
        return {'message': USER_DELETED}


class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400

        # find user in database
        user = UserModel.find_by_username(user_data.username)

        # check password
        if user and hmac.compare_digest(user.password, user_data.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)

            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        return {'message': INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        # jti is 'JWT ID', a unique identifier for a JWT
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': USER_LOGOUT}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)

        return {'access_token': new_token}
