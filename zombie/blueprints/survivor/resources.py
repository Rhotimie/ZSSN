import traceback
from collections import Counter
from flask import request
from flask_restful import Resource, reqparse
from marshmallow import EXCLUDE
from zombie.blueprints.survivor.models import SurvivorModel
from zombie.blueprints.survivor.schemas import SurvivorSchema
from zombie.blueprints.survivoritem.models import SurvivorItemModel
from marshmallow import ValidationError


survivor_schema = SurvivorSchema(unknown=EXCLUDE)
multiple_survivors_schema = SurvivorSchema(many=True)

blank_error = "'{}' field cannot be blank. please specify this field"
survivor_not_found = "Survivor with name: {} does not exist"
survivor_deleted = "Survivor with corresponding Items has been deleted."
survivor_error_inserting= "An error occurred while inserting survivor."
survivor_name_exists = "Survivor with name '{}' already exists."
survivor_registered= "Survivor created successfully"


class SurvivorRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "item_ids",
        action='append',
        required=True,
        help=blank_error.format("item_ids"),
    )
    parser.add_argument(
        "name", type=str, required=True, help=blank_error.format("name"),
    )
    parser.add_argument(
        "age", type=int, required=True, help=blank_error.format("age"),
    )
    parser.add_argument(
        "gender", type=str, required=True, help=blank_error.format("gender"),
    )

    @classmethod
    def post(cls,):
        """
        dd survivors to the database
        A survivor must have a name, age, gender and last location (latitude, 
        longitude).
        A survivor also has an inventory of resources of their own property (which you 
        need to declare when upon the registration of the survivor).
        """
        data = (
            SurvivorRegister.parser.parse_args()
        )  # name + age + list of item ids  [1, 2, 3, 5, 5, 5]


        item_id_quantities = Counter(data["item_ids"])
        name = data["name"]
        age = data["age"]
        gender = data["gender"]

        survivor_json = {"name": name, "age": age, "gender": gender}

        # using marshmallow library begat the code below
        try:
            survivor = survivor_schema.load(survivor_json)    # creates dictionary
        except ValidationError as err:
            return err.messages, 400

        if SurvivorModel.find_by_identity(survivor.name):
            return {"message": survivor_name_exists.format(name)}, 400

        try:
            survivor.update_activity_tracking(request.remote_addr)
            survivor.save_to_db()
            SurvivorItemModel.save_survivor_items(survivor.id, item_id_quantities)
            return {"message": survivor_registered}, 201
        except:
            survivor.delete_from_db()
            traceback.print_exc()
            return {"message": survivor_error_inserting}, 500



class Survivors(Resource):
    @classmethod
    def get(cls,):
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        survivor_name = data["name"]

        survivor = SurvivorModel.find_by_identity(survivor_name)
        if not survivor:
            return {"message": survivor_not_found.format(survivor_name)}, 404
        return survivor_schema.dump(survivor), 200


    @classmethod
    def delete(cls,):
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        survivor_name = data["name"]

        survivors = SurvivorModel.find_by_identity(survivor_name)

        if not survivors:
            return {"message": survivor_not_found.format(survivor_name)}, 404

        survivors.delete_from_db()

        return {"message": survivor_deleted}, 200


class SurvivorList(Resource):
    @classmethod
    def get(cls):
        return multiple_survivors_schema.dump(SurvivorModel.find_all()), 200





