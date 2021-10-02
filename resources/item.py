from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()

    # TODO all other args not defined in parser are erased
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank')

    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='Every item requires a store_id')

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()

        return {'message': 'Item not found'}, 404

    @jwt_required(refresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": f"An item with name "
                               f"'{name}' already exists "}, 400

        # TODO force=true you don't need the content type header
        #  silent=True -> doesn't give an error
        # data = request.get_json()

        data = Item.parser.parse_args()

        item = ItemModel(name, data['price'], data['store_id'])

        try:
            item.save_to_db()
        except Exception as ex:
            return {"message": f"An error occurred while "
                               f"inserting the item: {ex}"}, 500

        return item.json(), 201

    @jwt_required()
    def delete(self, name):

        claims = get_jwt()

        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 401

        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    def put(self, name):
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
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = list(map(lambda x: x.json(), ItemModel.find_all()))

        if user_id:
            return {'items': items}, 200

        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if you log in'
        }, 200
