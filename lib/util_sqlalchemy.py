import imp
import click
from datetime import datetime
from sqlalchemy import func, or_, and_
from flask import abort
from marshmallow import Schema, fields
from lib.util_datetime import tzware_datetime, AwareDateTime
from zombie.extensions import db
from sqlalchemy import text, asc, desc, String
from lib.util_json import convert_None_to_empty_string, write_to_file, read_from_file
from lib.util_sort import grouper
from lib.util_sort import grouper, un_grouper
import ray
from ray.util import ActorPool
import modin.pandas as pd


class ResourceMixin(object):
    # Keep track when records are created and updated.
    created_on = db.Column(AwareDateTime(),
            default=tzware_datetime)
    updated_on = db.Column(AwareDateTime(),
            default=tzware_datetime,
            onupdate=tzware_datetime)
    is_active = db.Column(db.Boolean(), default=True)


    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'created_on'

        if direction not in ('asc', 'desc'):
            direction = 'asc'

        return field, direction

    @classmethod
    def order_values_text_apply(cls, field_direction_tuple):
        """
        Verify the field and direction data types apply appropriate sorting algorithm respectively.

        :param field: Field name and Direction
        :type field: tuple
        :return: str for String data type field data
        """
        field = field_direction_tuple[0]
        direction = field_direction_tuple[1]
        all_columns = cls.__table__.columns._all_columns
        for col in all_columns:
            if col.name == field:
                if isinstance(col.type, String):
                    return text('{0} {1}'.format(field, direction))
                else:
                    return asc(col) if direction == 'asc' else desc(col)

        return text('{0} {1}'.format(field, direction))


    @classmethod
    def get_bulk_action_ids(cls, scope, ids, omit_ids=[], query=''):
        """
        Determine which IDs are to be modified.

        :param scope: Affect all or only a subset of items
        :type scope: str
        :param ids: List of ids to be modified
        :type ids: list
        :param omit_ids: Remove 1 or more IDs from the list
        :type omit_ids: list
        :param query: Search query (if applicable)
        :type query: str
        :return: list
        """
        omit_ids = map(str, omit_ids) if omit_ids else None

        if scope == 'all_search_results':
            # Change the scope to go from selected ids to all search results.
            ids = cls.query.with_entities(cls.id).filter(cls.search(query))

            # SQLAlchemy returns back a list of tuples, we want a list of strs.
            ids = [str(item[0]) for item in ids]

        # Remove 1 or more items from the list, this could be useful in spots
        # where you may want to protect the current user from deleting themself
        # when bulk deleting user accounts.
        if omit_ids:
            ids = [id for id in ids if id not in omit_ids]

        return ids

    @classmethod
    def bulk_query(cls, ids):
        """
        fectch more than 1 model instances.

        :param ids: List of ids to be fetched
        :type ids: list
        :return: List of model instances
        """
        if ids:
            return cls.query.filter(cls.id.in_(ids))

        return None

    @classmethod
    def find_by_multiple_field(cls, session, kwargs):
        return session.query(cls).filter_by(**kwargs).first()


    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete 1 or more model instances.

        :param ids: List of ids to be deleted
        :type ids: list
        :return: Number of deleted instances
        """
        delete_count = cls.query.filter(
            cls.id.in_(ids)
        ).delete(synchronize_session=False)
        db.session.commit()

        return delete_count


    @classmethod
    def bulk_update(cls, ids, value_dict):
        """
        Update 1 or more model instances.

        :param ids: List of ids to be updated
        :type ids: list
        :return: Number of updated instances
        """
        update_count = cls.query.filter(
            cls.id.in_(ids)
        ).update(value_dict, synchronize_session=False)
        db.session.commit()

        return update_count

    @classmethod
    def group_and_count(cls, field):
        """
        Group results for a specific model and field.

        :param model: Name of the model
        :type model: SQLAlchemy model
        :param field: Name of the field to group on
        :type field: SQLAlchemy field
        :return: dict
        """
        count = func.count(field)
        query = db.session.query(count, field).group_by(field).all()

        return query

    @classmethod
    def find_by_created_on(cls, _date: str):
        """
        Find a model instance by date created.

        :return: Model instance
        """
        return cls.query.filter(func.DATE(cls.created_on) == _date).all()

    @classmethod
    def find_by_updated_on(cls, _date: str):
        """
        Find a model instance by date modified.

        :return: Model instance
        """
        return cls.query.filter(func.DATE(cls.updated_on) == _date).all()

    def save_to_db(self):
        """
        Save a model instance.

        :return: None
        """
        db.session.add(self)
        db.session.commit()
        return None
 

    @staticmethod
    def add_all(instance_list):
        """
        Save a model instance.

        :return: None
        """
        db.session.bulk_save_objects(instance_list) 
        db.session.commit()
        return None


    def delete_from_db(self):
        """
        Delete a model instance.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
        return None


    @classmethod
    def choice_query_select(cls,):
        return cls.query

    @classmethod
    def choice_query_select_by_field(cls, field, val):
        """
        run a filter base on a field value

        :return: Model instance
        """
        return cls.query.filter(getattr(cls, field) == val)


    @classmethod
    def choice_query_list(cls, field=None):
        """
        Query a model for all the instances

        :return: List of tuples of id and given field(with default name field)
        """
        if field:
            return [(b.id, getattr(b, field)) for b in cls.find_all()]

        return [(b.id, b.name) for b in cls.find_all()]


    def __str__(self):
        """
        Create a human readable version of a class instance.

        :return: self
        """
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()

        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in columns)
        return '<%s %s(%s)>' % (obj_id, self.__class__.__name__, values)

    def url(self):
        return f"/{self.__class__.__name__.lower()}/{self.id}"


    def to_dict(self,):
        columns = self.__table__.columns.keys()
        return {key: getattr(self, key) for key in columns}




