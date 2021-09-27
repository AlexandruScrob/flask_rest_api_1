# resource = external representation of an entity

import sqlite3

from flask_restful import Resource, reqparse

from section6.models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()

    # TODO all other args not defined in parser are erased
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help='Username required')
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help='Password required')

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': "User with that username already exists"}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO users VALUES (NULL, ?, ?)"

        cursor.execute(query, (data['username'], data['password']))

        connection.commit()
        connection.close()

        return {'message': 'User created successfully.'}, 200
