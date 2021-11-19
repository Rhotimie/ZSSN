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
infected_survivor= "You have been marked infected hence your record is not accessible"
infection_flagger_error = "You can't flag another survivor because your detail is invalid"
infection_flagger_is_infected = "You can't flag another survivor because you are infected"
infected_survivor_already_marked= "The survivor has been marked infected already"
survivor_already_flagged_by_you= "The survivor has already been flagged by you"
self_flagging = "You are not allowed to flag yourself"

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

        if survivor.is_infected:
            return {"message": infected_survivor}, 400

        return survivor_schema.dump(survivor), 200

    @classmethod
    def put(cls,):
        """
        Update survivor location
        A survivor must have the ability to update their last location, storing the new 
        latitude/longitude pair in the base (no need to track locations, just replacing 
        the previous one is enough).
        """
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        survivor_name = data["name"]

        survivor = SurvivorModel.find_by_identity(survivor_name)
        if not survivor:
            return {"message": survivor_not_found.format(survivor_name)}, 404

        if survivor.is_infected:
            return {"message": infected_survivor}, 400

        survivor.update_activity_tracking(request.remote_addr)

        return survivor_schema.dump(survivor), 200

    @classmethod
    def delete(cls,):
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        survivor_name = data["name"]

        survivor = SurvivorModel.find_by_identity(survivor_name)

        if not survivor:
            return {"message": survivor_not_found.format(survivor_name)}, 404

        if survivor.is_infected:
            return {"message": infected_survivor}, 400

        survivor.delete_from_db()

        return {"message": survivor_deleted}, 200

class FlagSurvivor(Resource):
    @classmethod
    def put(cls,):
        """
            Flag survivor as infected
            In a chaotic situation like that, it's inevitable that a survivor may get 
            contaminated by the virus. When this happens, we need to flag the survivor as 
            infected.
            An infected survivor cannot trade with others, can't access/manipulate their 
            inventory, nor be listed in the reports (infected people are kinda dead anyway, 
            see the item on reports below).
            A survivor is marked as infected when at least three other survivors 
            report their contamination.
            When a survivor is infected, their inventory items become inaccessible (they 
            cannot trade with others).
        """
        data = request.get_json() if request.get_json() else dict(request.form)
        if not data:
            data = dict(request.args)

        if not data.get("name"):
            return {"message": blank_error.format("name")}, 400

        if not data.get("survivor_id"):
            return {"message": blank_error.format("survivor_id")}, 400

        survivor_name = data["name"]
        survivor_id = data["survivor_id"]

        infection_flagger = SurvivorModel.find_by_id(survivor_id)
        survivor = SurvivorModel.find_by_identity(survivor_name)

        if not infection_flagger:
            return {"message": infection_flagger_error}, 404

        if not survivor:
            return {"message": survivor_not_found.format(survivor_name)}, 404

        if infection_flagger.is_infected:
            return {"message": infection_flagger_is_infected}, 400

        if survivor.is_infected:
            return {"message": infected_survivor_already_marked}, 400

        if survivor.id == infection_flagger.is_infected:
            return {"message": self_flagging}, 400

        if infection_flagger.id in survivor.survivor_flag_list:
            return {"message": survivor_already_flagged_by_you}, 400

        survivor.survivor_flag_list += [infection_flagger.id]
        survivor.increase_infection_flag_count()

        return survivor_schema.dump(survivor), 200



class SurvivorList(Resource):
    @classmethod
    def get(cls):
        return multiple_survivors_schema.dump(SurvivorModel.find_all()), 200





