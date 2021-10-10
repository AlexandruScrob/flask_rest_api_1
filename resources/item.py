from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from models.item import ItemModel


BLANK_ERROR = "'{}' cannot be left blank."
ITEM_NOT_FOUND = 'Item not found.'
ITEM_NAME_ALREADY_EXISTS = "An item with name '{}' already exists."
ITEM_DELETED = 'Item deleted'
ITEM_EX_MESSAGE = "An error occurred while inserting the item: {}"


class Item(Resource):
    parser = reqparse.RequestParser()

    # TODO all other args not defined in parser are erased
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help=BLANK_ERROR.format("price"))

    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help=BLANK_ERROR.format("store_id"))

    @classmethod
    # @jwt_required()
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()

        return {'message': ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required(refresh=True)
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": ITEM_NAME_ALREADY_EXISTS.format(name)}, 400

        # TODO force=true you don't need the content type header
        #  silent=True -> doesn't give an error
        # data = request.get_json()

        data = Item.parser.parse_args()

        item = ItemModel(name, data['price'], data['store_id'])

        try:
            item.save_to_db()
        except Exception as ex:
            return {"message": ITEM_EX_MESSAGE.format(ex)}, 500

        return item.json(), 201

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        # claims = get_jwt()
        # if not claims['is_admin']:
        #     return {'message': 'Admin privilege required'}, 401

        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()

        return {'message': ITEM_DELETED}

    @classmethod
    def put(cls, name: str):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)

        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @classmethod
    # @jwt_required(optional=True)
    def get(cls):
        # user_id = get_jwt_identity()
        items = list(map(lambda x: x.json(), ItemModel.find_all()))

        # if user_id:
        return {'items': items}, 200

        # return {
        #     'items': [item['name'] for item in items],
        #     'message': 'More data available if you log in'
        # }, 200
