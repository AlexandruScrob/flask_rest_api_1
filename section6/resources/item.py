import sqlite3

from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from section6.models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()

    # TODO all other args not defined in parser are erased
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank')

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()

        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": f"An item with name "
                               f"'{name}' already exists "}, 400

        # TODO force=true you don't need the content type header
        #  silent=True -> doesn't give an error
        # data = request.get_json()

        data = Item.parser.parse_args()

        item = ItemModel(name, data['price'])

        try:
            item.insert()
        except Exception as ex:
            return {"message": f"An error occurred while "
                               f"inserting the item: {ex}"}, 500

        return item.json(), 201

    def delete(self, name):
        if not ItemModel.find_by_name(name):
            return {"message": f"An item with name "
                               f"'{name}' doesn't exist"}, 404

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "DELETE FROM items WHERE name=?"

        cursor.execute(query, (name, ))

        connection.commit()
        connection.close()

        return {'message': 'item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
        updated_item = ItemModel(name, data['price'])

        if item is None:
            try:
                updated_item.insert()
            except Exception as ex:
                return {"message": f"An error occurred while "
                                   f"inserting the item: {ex}"}, 500

        else:
            try:
                updated_item.update()
            except Exception as ex:
                return {"message": f"An error occurred while "
                                   f"updating the item: {ex}"}, 500

        return updated_item.json()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)

        items = [{'name': row[0], 'price': row[1]} for row in result]

        connection.close()

        return {"items": items}
