from flask import request
from flask_restful import Resource, reqparse
from marshmallow import ValidationError, EXCLUDE
from zombie.blueprints.item.models import ItemModel
from zombie.blueprints.item.schemas import ItemSchema


item_schema = ItemSchema(unknown=EXCLUDE)
multiple_item_schema = ItemSchema(many=True)

blank_error = "'{}' field cannot be blank. please specify this field"
item_not_found = "Item not found."
item_name_exists = "An item with name '{}' already exists."
item_error_inserting= "An error occurred while inserting the item."
item_deleted = "Item deleted."

class Item(Resource):
    @classmethod
    def get(cls):
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        name = data["name"]

        item = ItemModel.find_by_name(name)
        if item:
            return {"item": item_schema.dump(item)}, 200
        return {"message": item_not_found}, 404


    @classmethod
    def post(cls):
        item_json = request.get_json() if request.get_json() else dict(request.form)
        if not item_json:
            item_json = dict(request.args)

        if not item_json.get("name"):
            return {"message": blank_error.format("name")}, 400
        if not item_json.get("points"):
            return {"message": blank_error.format("points")}, 400


        name = item_json["name"]

        if ItemModel.find_by_name(name):
            return (
                {"message": item_name_exists.format(name)},
                400,
            )

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except Exception as e:
            return {"error": str(e), "message": item_error_inserting}, 500

        return item_schema.dump(item), 201


    @classmethod
    def delete(cls):
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        name = data["name"]

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": item_deleted}
        return {"message": item_not_found}, 404


class ItemList(Resource):
    @classmethod
    def get(cls):
        return multiple_item_schema.dump(ItemModel.find_all()), 200
