#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`anydo_api.resource`.

`Resource` class.
"""

import base64
import random
import six

from anydo_api import errors
from anydo_api import request

__all__ = ('Resource')

class Resource(object):
    """
    `Resource` is the class representing common wrapper around AnyDo json objects.

    It wraps task-related JSON into class instances with access interface.
    All actual models are inherit it.
    """

    _reserved_attrs = ('data_dict', 'is_dirty')
    _endpoint = ''

    def __init__(self, data_dict):
        """Constructor for generic Resource."""
        self.data_dict = data_dict
        self.is_dirty = False

    def __getitem__(self, key):
        """Access to resource data by indexes."""
        return self.data_dict[key]

    def __getattr__(self, attr):
        """Access to resource data by attributes."""
        try:
            result = self.data_dict[attr]
        except KeyError:
            raise errors.ModelAttributeError(attr + ' is not exist')

        return result

    def __setitem__(self, attr, new_value):
        """Set resource data values by indexes."""
        if attr in self.data_dict:
            old_value = self.data_dict[attr]

            if old_value != new_value:
                self.data_dict[attr] = new_value
                self.is_dirty = True
        else:
            raise errors.ModelAttributeError(attr + ' is not exist')

    def __setattr__(self, attr, new_value):
        """Assign resource data values as attribute values."""
        if attr not in self.get_reserved_attrs() and attr in self.data_dict:
            old_value = self.data_dict[attr]

            if old_value != new_value:
                self.data_dict[attr] = new_value
                self.__dict__['is_dirty'] = True
        else:
            super(Resource, self).__setattr__(attr, new_value)

    def save(self, alternate_endpoint=None):
        """
        Push updated attributes to the server.

        If nothing was changed we dont hit an API.
        """
        if self.is_dirty:
            processed_data = self._process_data_before_save(self.data_dict)

            request.put(
                url=alternate_endpoint or (self.get_endpoint() + '/' + self['id']),
                json=processed_data,
                session=self.session()
            )

            self.is_dirty = False

        return self

    def destroy(self, alternate_endpoint=None):
        """Delete the tasks by remote API call."""
        request.delete(
            url=alternate_endpoint or (self.get_endpoint() + '/' + self['id']),
            json=self.data_dict,
            session=self.session()
        )

        return self

    delete = destroy

    #pylint: disable=no-self-use
    def session(self):
        """Shortcut to retrive object session for requests."""
        raise errors.MethodNotImplementedError('Need to be implemented in the class descendant')

    def refresh(self, alternate_endpoint=None):
        """Reload resource data from remote service."""
        self.data_dict = request.get(
            url=alternate_endpoint or (self.get_endpoint() + '/' + self['id']),
            session=self.session()
        )

        return self

    def get_endpoint(self):
        """Return instance endpoint for API calls."""
        return self._endpoint

    def get_reserved_attrs(self):
        """Return a tuple with reserved attributes, protected for internal usage."""
        return self._reserved_attrs

    @staticmethod
    def generate_uid():
        """Generate unique global id generator for new resources."""
        random_string = six.b('').join([six.int2byte(random.randint(0, 255)) for _ in range(0, 16)])
        result = base64.urlsafe_b64encode(random_string)
        try:
            result = result.decode('utf-8')
        except UnicodeDecodeError:
            pass

        return result

    @staticmethod
    def required_attributes():
        """
        Return a set of required fields for valid resource creation.

        This tuple is checked to prevent unnecessary API calls.
        """
        raise errors.MethodNotImplementedError('Need to be implemented in the class descendant')

    @classmethod
    def check_for_missed_fields(cls, fields):
        """
        Check task attributes for missed required.

        Raises exception with a list of all missed.
        """
        missed = cls.required_attributes() - set(fields.keys())
        size = len(missed)
        if size > 0:
            raise errors.ModelAttributeError('Missing required fields: {}!'.format(missed))

    @classmethod
    def create(cls, user, **fields):
        """Create new resource via API call."""
        cls.check_for_missed_fields(fields)

        json_data = fields.copy()
        json_data.update({'id': cls.generate_uid()})

        params = {
            'includeDeleted': 'false',
            'includeDone'   : 'false',
        }

        response_obj = request.post(
            url=cls._endpoint,
            session=user.session(),
            json=[json_data],
            params=params
        )

        return cls._create_callback(response_obj, user)

    @staticmethod
    def _process_data_before_save(data_dict):
        """
        Change the data send to the server via API before save in cases when needed.

        Is not obligatory.
        """
        return data_dict

    #pylint: disable=unused-argument
    @classmethod
    def _create_callback(cls, resource_json, user):
        """
        Callback method that is called automaticly after each successfull creation via remote API.

        Return an instance of the appropriate class.
        """
        raise errors.MethodNotImplementedError('Need to be implemented in the class descendant')
