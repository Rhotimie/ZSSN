# from marshmallow import Schema, fields
from zombie.extensions import ma
from zombie.blueprints.survivor.models import SurvivorModel


class SurvivorSchema(ma.ModelSchema):
    class Meta:
        model = SurvivorModel
        dump_only = ("id",)

