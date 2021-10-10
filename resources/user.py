# resource = external representation of an entity
import hmac

from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity, get_jwt)
from flask_restful import Resource, reqparse

from blacklist import BLACKLIST
from models.user import UserModel

PARSER = reqparse.RequestParser()

# TODO all other args not defined in parser are erased
PARSER.add_argument('username',
                    type=str,
                    required=True,
                    help='Username required')
PARSER.add_argument('password',
                    type=str,
                    required=True,
                    help='Password required')


class UserRegister(Resource):
    def post(self):
        data = PARSER.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': "User with that username already exists"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': 'User created successfully.'}, 200


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        return user.json()

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        user.delete_from_db()
        return {'message': 'User deleted'}


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = PARSER.parse_args()

        # find user in database
        user = UserModel.find_by_username(data['username'])

        # check password
        if user and hmac.compare_digest(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)

            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        return {'message': "Invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        # jti is 'JWT ID', a unique identifier for a JWT
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out'}, 200


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)

        return {'access_token': new_token}
