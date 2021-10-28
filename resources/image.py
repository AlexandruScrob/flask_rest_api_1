import traceback
import os

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity


from libs import image_helper
from libs.strings import get_text
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required()
    def post(self):
        """
        Used to upload an image file.
        It uses JWT to retrieve user information and then saves
        the image to the user's folder.
        If there is a filename conflict, it appends a number at the end.
        :return:
        """
        data = image_schema.load(request.files)  # {"image": FileStorage}
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"  # static/images/user_1

        try:
            image_path = image_helper.save_image(data['image'], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"message": get_text("image_uploaded").format(
                basename)}, 201

        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return {"message": get_text("image_illegal_extension").format(
                extension)}, 400


class Image(Resource):
    @classmethod
    @jwt_required()
    def get(cls, filename: str):
        """
        Returns the requested image if it exists.
        Looks up inside the logged in user's folder.
        :param filename:
        :return:
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.is_filename_safe(filename):
            return {"message": get_text(
                "image_illegal_filename").format(filename)}, 400

        try:
            return send_file(image_helper.get_path(filename, folder=folder))

        except FileNotFoundError:
            return {"message": get_text(
                "image_not_found").format(filename)}, 404

    @classmethod
    @jwt_required()
    def delete(cls, filename: str):
        """

        :param filename:
        :return:
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.is_filename_safe(filename):
            return {"message": get_text(
                "image_illegal_filename").format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"message": get_text(
                "image_deleted").format(filename)}, 200

        except FileNotFoundError:
            return {"message": get_text(
                "image_not_found").format(filename)}, 404

        except Exception as ex:
            traceback.print_exc()
            return {"message": get_text(
                "image_delete_failed").format(str(ex))}, 500


class AvatarUpload(Resource):
    @jwt_required()
    def put(self):
        """
        This endpoint is used to upload user avatars.
         All avatars are named after the user's ID.
        Uploading a new avatar overwrites the existing one.
        :return:
        """
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(
            filename, folder=folder)

        if avatar_path:
            try:
                os.remove(avatar_path)

            except Exception as ex:
                return {"message": get_text(
                    "avatar_delete_failed").format(str(ex))}, 500

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(
                data["image"], folder=folder, name=avatar
            )

            basename = image_helper.get_basename(avatar_path)
            return {"message": get_text(
                "avatar_uploaded").format(basename)}, 200

        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return {"message": get_text(
                "image_illegal_extension").format(extension)}, 400


class Avatar(Resource):
    @classmethod
    def get(cls, user_id: int):
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(
            filename, folder=folder)

        if avatar:
            return send_file(avatar)

        return {"message": get_text("avatar_not_found")}, 404
