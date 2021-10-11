import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST

from ma import ma
from db import db
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.user import (UserRegister, User, UserLogin, TokenRefresh,
                            UserLogout)


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# try to get the heroku postgressql db or get the local one
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_VALID_URL',
                                                       'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_AUTH_URL_RULE'] = '/login'

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

# config JWT auth key name to be 'email instead of default 'username
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

app.secret_key = 'alex'
api = Api(app)


jwt = JWTManager(app)  # /auth


# NOTE: Remove this function when deploying on Heroku
@app.before_first_request
def create_tables():
    db.create_all()


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:  # Instead of hard-coding, read from a config file or db
        return {'is_admin': True}

    return {'is_admin': False}


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(_decrypted_head, _decrypted_body):
    return _decrypted_body['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback(_decrypted_header, _decrypted_body):
    return jsonify({
        'description': 'the token has expired',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed',
        'error': 'invalid_token',
        'error_msg': str(error)
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token',
        'error': 'authorization_required',
        'error_msg': str(error)
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(_decrypted_header, _decrypted_body):
    return jsonify({
        'description': 'The token is not fresh',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(_decrypted_header, _decrypted_body):
    return jsonify({
        'description': 'The token has been revoked',
        'error': 'token_revoked'
    }), 401


api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')


if __name__ == '__main__':
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
