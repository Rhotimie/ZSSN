from zombie.extensions import ma
from zombie.blueprints.survivoritem.models import SurvivorItemModel


class SurvivorItemSchema(ma.ModelSchema):
    class Meta:
        model = SurvivorItemModel
        dump_only = ("id",)
        include_fk = True



