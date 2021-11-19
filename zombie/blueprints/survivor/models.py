from collections import OrderedDict
from typing import Dict, List, Union
from sqlalchemy import or_
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.dialects.postgresql import ARRAY
from lib.util_sqlalchemy import ResourceMixin
from zombie.extensions import db
from zombie.blueprints.survivoritem.models import SurvivorItemModel
from lib.util_loc import ip_api

SurvivorJSON = Dict[str, Union[int, str, float, List]]
ItemForSurvivorJSON = Dict[str, Union[int, float, List]]

# Survivor Model
class SurvivorModel(ResourceMixin, db.Model):
    GENDER = OrderedDict(
        [("male", "M"), ("female", "F"), ("unknown", "U"),]
    )

    __tablename__ = "survivors"
    id = db.Column(db.Integer, primary_key=True)

    # personal details
    name = db.Column(db.String(128), unique=True, index=True, nullable=True)
    age = db.Column(db.Integer, nullable=False, default=0)
    gender  = db.Column(
        db.Enum(*GENDER, name="gender_types", native_enum=False),
        index=True,
        nullable=False,
        server_default="unknown",
    )
    
    # Activity tracking.
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_ip = db.Column(db.String(45))
    last_location = db.Column(MutableDict.as_mutable(db.JSON()))
    current_location = db.Column(MutableDict.as_mutable(db.JSON()))

    #track infected survivor
    is_infected = db.Column(db.Boolean(), nullable=False, server_default="0")
    infection_flag_count = db.Column(db.Integer, nullable=False, default=0)
    survivor_flag_list = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])

    # Relationships.
    survivor_items = db.relationship(
        "SurvivorItemModel", back_populates="survivor", cascade="all, delete-orphan"
    )

    def __str__(self,):
        """
        Create a human readable version of a class instance.

        :return: self
        """
        return "survivor name: {}, age: {}".format(self.name, self.age)


    @property
    def all_items(self) -> "SurvivorItemModel":
        return self.survivoritem.order_by(db.desc(SurvivorItemModel.id)).first()

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a survivor by their name.

        :param identity: name
        :type identity: str
        :return: Survivor instance
        """
        # # taking not of logging attempts
        return cls.query.filter(cls.name == identity).first()


    @classmethod
    def find_by_id(cls, _id: int) -> "SurvivorModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["SurvivorModel"]:
        return cls.query.filter_by(is_infected=False).all()

    def update_activity_tracking(self, ip_address, is_trade=False):
        """
        Update various fields on the survivor that's related to meta data on their
        account, such as the sign in count and ip address, etc..

        :param ip_address: IP address
        :type ip_address: str
        :return: SQLAlchemy commit results
        """

        self.last_sign_in_ip = self.current_sign_in_ip
        self.current_sign_in_ip = ip_address

        self.last_location = self.current_location
        self.current_location = ip_api(ip_address)
        if is_trade: self.save_to_db()

    def increase_infection_flag_count(self,):
        self.infection_flag_count += 1
        if self.infection_flag_count >= 3:
            self.is_infected = True
        self.save_to_db()

