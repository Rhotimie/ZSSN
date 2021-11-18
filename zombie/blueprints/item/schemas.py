from zombie.extensions import ma
from zombie.blueprints.item.models import ItemModel


class ItemSchema(ma.ModelSchema):
    class Meta:
        model = ItemModel
        dump_only = ("id",)
        include_fk = True

