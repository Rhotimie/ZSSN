import os
from flask import Blueprint
from flask_restful import Api
from zombie.blueprints.survivor.resources import (
    SurvivorRegister,
    Survivors,
    SurvivorList,
    FlagSurvivor,
    TradeItems
)
from zombie.blueprints.item.resources import Item, ItemList
from zombie.blueprints.survivoritem.resources import SurvivorItem

from zombie.blueprints.insights.resources import (
    InfectedSurvivorsPercent, NonInfectedSurvivorsPercent,
    AverageResourcesBySurvivor, PointsLostToInfectedSurvivor
)


base_dir = os.getcwd()
static_fold = os.path.join(base_dir, "zombie", "static")
temp_fold = os.path.join(base_dir, "zombie", "templates")
api_bp = Blueprint("api", __name__, static_folder=static_fold, template_folder=temp_fold)
rest_api = Api(api_bp)

"""
CREATING ROUTES USING FLASK RESOURCES
"""
rest_api.add_resource(SurvivorRegister, "/register", endpoint="survivor-registration")
rest_api.add_resource(Survivors, "/survivor")
rest_api.add_resource(SurvivorList, "/survivors")
# Don't change what we have below
rest_api.add_resource(
    SurvivorItem,
    "/survivor_item",
    endpoint="survivor-item",
)
rest_api.add_resource(Item, "/item")
rest_api.add_resource(ItemList, "/items")
rest_api.add_resource(FlagSurvivor, "/flag_survivor")
rest_api.add_resource(TradeItems, "/trade")

# insights API
rest_api.add_resource(InfectedSurvivorsPercent, "/infected_survivors")
rest_api.add_resource(NonInfectedSurvivorsPercent, "/uninfected_survivors")
rest_api.add_resource(AverageResourcesBySurvivor, "/average_resource")
rest_api.add_resource(PointsLostToInfectedSurvivor, "/pointsloss")

