from flask import g, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_required
from flask_restful import Resource

from libs.strings import get_text
from models.user import UserModel
from oa import github
from resources.user import user_schema


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        return github().authorize_redirect(
            url_for("github.authorize", _external=True)
        )


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        resp = github().authorize_access_token()

        if resp is None or resp.get('access_token') is None:
            error_response = {
                "error": request.args["error"],
                "error_description": request.args["error_description"]
            }
            return error_response

        g.access_token = resp['access_token']
        github_user = github().get('user').json()
        github_username = github_user['login']

        user = UserModel.find_by_username(github_username)

        if not user:
            user = UserModel(username=github_username, password="",
                             email="")
            user.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        return {"access_token": access_token,
                "refresh_token": refresh_token}, 200


class SetPassword(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)  # username and new password
        user = UserModel.find_by_username(user_data.username)

        if not user:
            return {"message": get_text("user_not_found")}, 400

        user.password = user_data.password
        user.save_to_db()

        return {"message": get_text("user_password_updated")}, 201
