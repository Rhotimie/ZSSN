import os
import math
import itertools
from statistics import mean
from collections import OrderedDict
from flask import current_app
from typing import Dict, List, Union
from zombie.extensions import db
from lib.util_sqlalchemy import ResourceMixin

ItemJSON = Dict[str, Union[int, str, float, List]]
ItemInStoreJSON = Dict[str, Union[int, float, List]]


class ItemModel(ResourceMixin, db.Model):
    StatusType = OrderedDict(
        [("Active", "1"), ("InActive", "2")]
    )
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    product_status  = db.Column(
        db.Enum(*StatusType, name="product_status", native_enum=False),
        index=True,
        nullable=False,
        server_default="Active",
    )

    def __str__(self,):
        """
        Create a human readable version of a class instance.

        :return: self
        """
        return "name: {}, points: {}".format(self.name, self.points)


    @classmethod
    def find_by_name(
        cls, name: str
    ) -> "ItemModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(
        cls, _id: int
    ) -> "ItemModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_product_status(
        cls, product_status: str
    ) -> "ItemModel":
        return cls.query.filter_by(product_status=product_status)

    @classmethod
    def find_all(cls) -> List["ItemModel"]:
        return cls.query.all()



