from marshmallow import pre_dump, post_dump
from zombie.extensions import ma
from zombie.blueprints.survivor.models import SurvivorModel


class SurvivorSchema(ma.ModelSchema):
    class Meta:
        model = SurvivorModel
        dump_only = ("id",)

        @pre_dump
        def _pre_dump(self, survivor: SurvivorModel):
            survivor.survivor_items = survivor.survivor_items_details
            return survivor
