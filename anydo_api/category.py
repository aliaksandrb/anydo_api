#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .resource import Resource
from .constants import CONSTANTS

__all__ = ['Category']

class Category(Resource):
    """
    `Category` is the class representing user category object.
    It wraps task-related JSON into class instances and
    responsible for categories management.
    """

    _reserved_attrs = ('user', 'data_dict', 'is_dirty')
    _endpoint = CONSTANTS.get('CATEGORIES_URL')

    def __init__(self, data_dict, user):
        super(Category, self).__init__(data_dict)
        self.user = user

    def session(self):
        """
        Chortcut to retrive user session for requests.
        """
        return self.user.session

#    @staticmethod
#    def _process_data_before_save(data_dict):
#        """
#        Changes the data send to the server via API before save in cases when needed.
#        """
#        result = data_dict.copy()
#        del result['lastUpdateDate']
#        del result['id']
#        print('----data to be sent', result)
#        return result

    @staticmethod
    def required_attributes():
        """
        Returns a set of required fields for valid task creation.
        This tuple is checked to prevent unnecessary API calls.

        Seems that :id and :title attributes are required for now, where
        :id is set automatically.
        """

        return {'name'}
#
#    @staticmethod
#    def filter_tasks(tasks_list, **filters):
#        """
#        Filters tasks by their status.
#        Returns a new filtered list.
#        """
#
#        result = tasks_list[:]
#        statuses = list(TASK_STATUSES)
#
#        if not filters.get('include_deleted', False): statuses.remove('DELETED')
#        if not filters.get('include_done', False): statuses.remove('DONE')
#        if not filters.get('include_checked', False): statuses.remove('CHECKED')
#        if not filters.get('include_unchecked', False): statuses.remove('UNCHECKED')
#
#        result = filter(lambda task: task['status'] in statuses, result)
#        return list(result)
#
#
    @classmethod
    def _create_callback(klass, resource_json, user):
      category = klass(data_dict=resource_json[0], user=user)

      return category
