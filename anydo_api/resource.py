#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import random

from . import errors
from . import request
from .constants import CONSTANTS

__all__ = ['Resource']

class Resource(object):
    """
    `Resource` is the class representing common wrapper around AnyDo json objects.
    It wraps task-related JSON into class instances with access interface.

    All actual models are inherit it.
    """

    _reserved_attrs = ('data_dict', 'is_dirty')

    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.is_dirty = False

    def __getitem__(self, key):
        return self.data_dict[key]

    def __getattr__(self, attr):
        try:
            result = self.data_dict[attr]
        except KeyError:
            raise errors.AttributeError(attr + ' is not exist')

        return result

    def __setitem__(self, attr, new_value):
        if attr in self.data_dict:
            old_value = self.data_dict[attr]

            if old_value != new_value:
                self.data_dict[attr] = new_value
                self.is_dirty = True
        else:
            raise errors.AttributeError(attr + ' is not exist')

    def __setattr__(self, attr, new_value):
        if attr not in self.__class__._reserved_attrs and attr in self.data_dict:
            old_value = self.data_dict[attr]

            if old_value != new_value:
                self.data_dict[attr] = new_value
                self.__dict__['is_dirty'] = True
        else:
            super(Resource, self).__setattr__(attr, new_value)

    def save(self, alternate_endpoint=None):
        """
        Pushes updated attributes to the server.
        If nothing was changed we dont hit an API.
        """

        if self.is_dirty:
            processed_data = self.__class__._process_data_before_save(self.data_dict)

            response_obj = request.put(
                url=alternate_endpoint or self.__class__._endpoint + '/' + self['id'],
                json=processed_data,
                session=self.session()
            )

            self.is_dirty = False

        return self

    def destroy(self, alternate_endpoint=None):
        """
        Deletes the tasks by remote API call
        """

        request.delete(
            url=alternate_endpoint or self.__class__._endpoint + '/' + self.id,
            json=self.data_dict,
            session=self.session()
        )

        return self

    delete = destroy

    def session(self):
        """
        Shortcut to retrive object session for requests.
        """
        raise errors.NotImplemented('Need to be implemented in the class descendant')

    def refresh(self):
        """
        Reload reource data from remote service.
        """
        self.data_dict = request.get(
            url=self.__class__._endpoint + '/' + self['id'],
            session=self.session()
        )

        return self

    @staticmethod
    def generate_uid():
        """
        Unique global id generator for new resources.
        """
        random_string = ''.join([chr(random.randint(0, 255)) for _ in range(0, 16)])
        try:
            random_string = random_string.encode('utf-8')
        except UnicodeDecodeError: pass

        result = base64.urlsafe_b64encode(random_string)
        try:
            result = result.decode('utf-8')
        except UnicodeDecodeError: pass

        return result

    @staticmethod
    def required_attributes():
        """
        Returns a set of required fields for valid resource creation.
        This tuple is checked to prevent unnecessary API calls.
        """
        raise errors.NotImplemented('Need to be implemented in the class descendant')

    @classmethod
    def check_for_missed_fields(klass, fields):
        """
        Checks task attributes for missed required.
        Raises exception with a list of all missed.
        """

        missed = klass.required_attributes() - set(fields.keys())
        if len(missed) > 0:
            raise errors.AttributeError('Missing required fields: {}!'.format(missed))

    @classmethod
    def create(klass, user, **fields):
        """
        Creates new resource via API call.
        """
        klass.check_for_missed_fields(fields)

        json_data = fields.copy()
        json_data.update({ 'id': klass.generate_uid() })

        params = {
            'includeDeleted': 'false',
            'includeDone'   : 'false',
        }

        response_obj = request.post(
            url=klass._endpoint,
            session=user.session(),
            json=[json_data],
            params=params
        )

        return klass._create_callback(response_obj, user)

    @staticmethod
    def _process_data_before_save(data_dict):
        """
        Changes the data send to the server via API before save in cases when needed.

        Is not obligatory.
        """

        return data_dict

    @classmethod
    def _create_callback(klass, resource_json, user):
        """
        Callback method that is called automaticly after each successfull creation
        via remote API

        Returns an instance of the appropriate class.
        """
        raise errors.NotImplemented('Need to be implemented in the class descendant')
