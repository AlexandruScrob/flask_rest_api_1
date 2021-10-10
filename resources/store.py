from flask_restful import Resource
from models.store import StoreModel


STORE_NAME_ALREADY_EXISTS = "A store with name {} already exists."
STORE_NOT_FOUND = 'Store not found'
STORE_DELETED = "Store deleted"
STORE_EX_MESSAGE = "An error occurred while creating the store: {}"


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()

        return {'message': STORE_NOT_FOUND}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {'message': STORE_NAME_ALREADY_EXISTS.format(name)}

        store = StoreModel(name)

        try:
            store.save_to_db()

        except Exception as ex:
            return {'message': STORE_EX_MESSAGE.format(ex)}, 500

        return store.json(), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)

        if store:
            store.delete_from_db()

        return {'message': STORE_DELETED}


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {'stores': list(map(lambda x: x.json(),
                                   StoreModel.find_all()))}
