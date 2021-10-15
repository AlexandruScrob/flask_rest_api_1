from flask_restful import Resource
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from flask import request

from libs.strings import get_text
from models.item import ItemModel
from schemas.item import ItemSchema


item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    # @jwt_required()
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)

        if item:
            return item_schema.dump(item)

        return {'message': get_text("item_not_found")}, 404

    @classmethod
    @jwt_required(refresh=True)
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": get_text(
                "item_name_exists").format(name)}, 400

        # TODO force=true you don't need the content type header
        #  silent=True -> doesn't give an error
        # data = request.get_json()

        item_json = request.get_json()  # price, store_id
        item_json['name'] = name

        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400

        try:
            item.save_to_db()
        except Exception as ex:
            return {"message": get_text(
                "item_error_inserting").format(ex)}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        # claims = get_jwt()
        # if not claims['is_admin']:
        #     return {'message': 'Admin privilege required'}, 401

        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()

        return {'message': get_text("item_deleted")}

    @classmethod
    def put(cls, name: str):
        item_json = request.get_json()

        item = ItemModel.find_by_name(name)

        if item is None:
            item_json = request.get_json()  # price, store_id
            item_json['name'] = name

            item = item_schema.load(item_json)

        else:
            item.price = item_json['price']
            item.store_id = item_json['store_id']

        item.save_to_db()

        return item_schema.dump(item), 201


class ItemList(Resource):
    @classmethod
    # @jwt_required(optional=True)
    def get(cls):
        # user_id = get_jwt_identity()
        items = item_list_schema.dump(ItemModel.find_all())

        # if user_id:
        return {'items': items}, 200

        # return {
        #     'items': [item['name'] for item in items],
        #     'message': 'More data available if you log in'
        # }, 200
