from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required

from security import authenticate, identity


app = Flask(__name__)
app.secret_key = 'alex'
api = Api(app)

jwt = JWT(app, authenticate, identity)  # auth endpoint

items = []


class Item(Resource):
    @jwt_required()
    def get(self, name):
        item = filter(lambda x: x['name'] == name, items)
        first_item = next(item, None)

        return {'item': first_item}, 200 if first_item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {"message": f"An item with name '{name}' already exists "}, 400

        # TODO force=true you don't need the content type header
        #  silent=True -> doesn't give an error
        data = request.get_json()

        item = {'name': name, 'price': data['price']}
        items.append(item)
        return item, 201


class ItemList(Resource):
    def get(self):
        return {'items': items}


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')


app.run(port=5000, debug=True)
