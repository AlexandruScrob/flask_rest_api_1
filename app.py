from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from flask_migrate import Migrate

from marshmallow import ValidationError

from blacklist import BLACKLIST


load_dotenv(".env", verbose=True)


from ma import ma
from db import db
from oa import oauth

from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.user import (UserRegister, User, UserLogin, TokenRefresh,
                            UserLogout)
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, AvatarUpload, Avatar
from resources.github_login import GithubLogin, GithubAuthorize, SetPassword
from resources.order import Order

from libs.image_helper import IMAGE_SET


app = Flask(__name__)
# app.config['PROPAGATE_EXCEPTIONS'] = True
#
# try to get the heroku postgressql db or get the local one
# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     os.environ.get('DB_VALID_URL') or os.environ.get('DATABASE_URI')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_AUTH_URL_RULE'] = '/login'
#
# # config JWT to expire within half an hour
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)
#
# # config JWT auth key name to be 'email instead of default 'username
# # app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
#

app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
app.secret_key = app.config['APP_SECRET_KEY']
patch_request_class(app, 10 * 1024 * 1024)  # 10MB max size upload
configure_uploads(app, IMAGE_SET)

db.init_app(app)
oauth.init_app(app)
api = Api(app)

jwt = JWTManager(app)  # /auth
migrate = Migrate(app, db)  # should be after load_dotenv and other db configs


# NOTE: Remove this function when deploying on Heroku
@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


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
api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")
api.add_resource(GithubLogin, "/login/github")
api.add_resource(GithubAuthorize, "/login/github/authorized",
                 endpoint="github.authorize")
api.add_resource(SetPassword, "/user/password")
api.add_resource(Order, "/order")


if __name__ == '__main__':
    ma.init_app(app)
    app.run(port=5000)
