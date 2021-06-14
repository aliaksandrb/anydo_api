#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`anydo_api.tag`.

`Tag` class.
"""

from anydo_api import request
from anydo_api.constants import CONSTANTS, TASK_STATUSES
from anydo_api.resource import Resource

__all__ = ('Tag')

class Tag(Resource):
    """
    `Tag` is the class representing user tag object

    It allows access of tag based objects
    """

    _endpoint = CONSTANTS.get('SYNC_URL')
    _reserved_attrs = ('user','data_dict',"is_dirty")

    def __init__(self, data_dict, user):
        "Constructor for Task"
        super(Tag, self).__init__(data_dict)
        self.user = user

    def session(self):
        """Shortcut to retrive user session for requests."""
        return self.user.session()

    def tasks(self):
        """Return a list of the user tasks that belongs to selected category."""
        tasks = self.user.tasks()
        tasks = [task for task in tasks if task['labels'] is not None]
        return [task for task in tasks if self.id in task['labels']]
