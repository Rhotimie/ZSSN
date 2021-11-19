from time import time
from uuid import uuid4
from typing import List, Dict, Union
from lib.util_sqlalchemy import ResourceMixin
from zombie.extensions import db
from zombie.blueprints.item.models import ItemModel

item_id_not_found = "items with id: {} not found"

class SurvivorItemModel(ResourceMixin, db.Model):
    __tablename__ = "survivor_items"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    
    survivor_id = db.Column(db.Integer, db.ForeignKey("survivors.id"))
    survivor = db.relationship("SurvivorModel", back_populates="survivor_items")

    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    item = db.relationship("ItemModel")

    def __init__(self, survivor_id: int, item_id: int, **kwargs):
        super().__init__(**kwargs)
        self.survivor_id = survivor_id
        self.item_id = item_id

    def __repr__(self,):
        return "<survivor name: {}, item: {}, quantity: {}>".format(self.survivor_name, self.item_name, self.quantity,)

    @property
    def json(self,):
        return {
            "item": self.item_name,
            "quantity": self.quantity,
            "points": self.item_points
        }

    @property
    def survivor_name(self,):
        return self.survivor.name

    @property
    def item_name(self,) -> str:
        return self.item.name

    @property
    def item_points(self,) -> int:
        return self.item.points

    @classmethod
    def find_by_id(cls, _id: str) -> "SurvivorItemModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_item_id(
        cls, _item_id: int
    ) -> "SurvivorItemModel":
        return cls.query.filter_by(item_id=_item_id).all()


    @classmethod
    def find_by_survivor_id(
        cls, _survivor_id: int
    ) -> "SurvivorItemModel":
        return cls.query.filter_by(survivor_id=_survivor_id).all()


    @classmethod
    def find_by_item_id_survivor_id(
        cls, _item_id: int, _survivor_id: int
    ) -> "SurvivorItemModel": 
        return cls.query.filter_by(item_id=_item_id, survivor_id=_survivor_id).first()

    @classmethod
    def find_all(
        cls,
    ) -> List["SurvivorItemModel"]:
        return cls.query.all()


    @classmethod
    def save_survivor_items(cls, survivor_id: int, item_id_quantities: list) -> None:
        items = []
        not_found_item_ids = []
        for _id, count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)
            if not item:
                not_found_item_ids.append(_id)

            survivor_item = SurvivorItemModel(survivor_id, item.id, quantity=count)
            items.append(survivor_item)
            
        cls.add_all(items)
        if not_found_item_ids:
            return (
                {"message": item_id_not_found.format(not_found_item_ids)},
                404,
            )    
        return None

