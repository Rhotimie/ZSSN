from flask import render_template, make_response, request, redirect, url_for, flash
from flask_restful import Resource, reqparse
from marshmallow import EXCLUDE
from zombie.blueprints.survivoritem.models import SurvivorItemModel
from zombie.blueprints.survivoritem.schemas import SurvivorItemSchema

survivor_item_schema = SurvivorItemSchema(unknown=EXCLUDE)
multiple_survivor_item_schema = SurvivorItemSchema(many=True)


blank_error = "'{}' field cannot be blank. please specify this field"
no_survivor_item = "Survivor item with id: {} does not exist"
survivor_item_deleted = "Order with id: {} has been deleted."

class SurvivorItem(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "id", type=int, required=True, help=blank_error.format("id"),
    )

    @classmethod
    def get(cls):
        data = SurvivorItem.parser.parse_args()

        id = data["id"]
        survivor_item = SurvivorItem.find_by_id(id)

        if survivor_item:
            return survivor_item_schema.dump(survivor_item), 200

        return (
            {"message": no_survivor_item.format(id)},
            404,
        )

    @classmethod
    def delete(cls):
        data = SurvivorItem.parser.parse_args()

        id = data["id"]

        survivor_item = SurvivorItemModel.find_by_id(id)

        if survivor_item:
            survivor_item.delete_from_db()
            return {"message": survivor_item_deleted.format(id)}
        return (
            {"message": no_survivor_item.format(id)},
            404,
        )

class SurvivorItemsList(Resource):
    @classmethod
    def get(cls):
        items_in_orders = multiple_survivor_item_schema.dump(SurvivorItemModel.find_all())
        return {"survivor items": items_in_orders}, 200


