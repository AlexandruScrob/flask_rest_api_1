from flask_restful import Resource
from models.store import StoreModel
from schemas.store import StoreSchema


STORE_NAME_ALREADY_EXISTS = "A store with name {} already exists."
STORE_NOT_FOUND = 'Store not found'
STORE_DELETED = "Store deleted"
STORE_EX_MESSAGE = "An error occurred while creating the store: {}"


store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.drump(store), 200

        return {'message': STORE_NOT_FOUND}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {'message': STORE_NAME_ALREADY_EXISTS.format(name)}

        store = StoreModel(name=name)

        try:
            store.save_to_db()

        except Exception as ex:
            return {'message': STORE_EX_MESSAGE.format(ex)}, 500

        return store_schema.drump(store), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)

        if store:
            store.delete_from_db()

        return {'message': STORE_DELETED}, 200


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {'stores': store_list_schema.dump(
            StoreModel.find_all())}, 200
