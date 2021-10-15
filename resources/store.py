from flask_restful import Resource

from libs.strings import get_text
from models.store import StoreModel
from schemas.store import StoreSchema


store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.drump(store), 200

        return {'message': get_text("store_not_found")}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {'message': get_text("store_name_exists").format(name)}

        store = StoreModel(name=name)

        try:
            store.save_to_db()

        except Exception as ex:
            return {'message': get_text(
                "store_error_inserting").format(ex)}, 500

        return store_schema.drump(store), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)

        if store:
            store.delete_from_db()

        return {'message': get_text("store_deleted")}, 200


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {'stores': store_list_schema.dump(
            StoreModel.find_all())}, 200
