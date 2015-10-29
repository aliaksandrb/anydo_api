#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import errors
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
        Shortcut to retrive user session for requests.
        """
        return self.user.session()

    def mark_default(self):
        """
        Shortcut to mark a category as default one locally.

        Marks previous default one as not default
        """
        previous = self.user.default_category()
        previous.default = False
        previous.isDefault = False
        previous.save()

        self.default = True
        self.isDefault = True
        self.save()
        return self

    def tasks(self):
        """
        Returns a list of the user tasks that belongs to selected category
        """
        tasks = self.user.tasks()
        return [task for task in tasks if task.categoryId == self['id']]

    def add_task(self, task):
        """
        Adds new task into category.
        Updates task and pushes changes remotly.
        """
        task.categoryId = self['id']
        task.save()

    def remove_task(self, task):
        """
        Removes a task from the category and move to default one.
        Updates task and pushes changes remotly.

        If category already default do nothing.
        """
        if task.category().isDefault:
            raise errors.ModelError('Can not remove task from default category')

        task.categoryId = self.user.default_category()['id']
        task.save()

    @staticmethod
    def required_attributes():
        """
        Returns a set of required fields for valid task creation.
        This tuple is checked to prevent unnecessary API calls.

        Seems that :id and :title attributes are required for now, where
        :id is set automatically.
        """

        return {'name'}

    @classmethod
    def _create_callback(klass, resource_json, user):
      """
      Callback method that is called automaticly after each successfull creation
      via remote API

      Returns an category instance.
      """
      category = klass(data_dict=resource_json[0], user=user)
      user.add_category(category)
      return category
