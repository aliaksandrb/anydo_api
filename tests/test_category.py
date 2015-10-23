#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_category
----------------------------------

Tests for `category` class.
"""

import unittest
import json
import vcr as vcr_module
import time
import datetime

from .base import TestCase
from .test_helper import vcr, scrub_string

from anydo_api.task import Task
from anydo_api.category import Category
from anydo_api.errors import *


class TestCategory(TestCase):

    def __get_category(self, refresh=False):
        user = self.get_me()
        if refresh:
            with vcr.use_cassette('fixtures/vcr_cassettes/categories_refreshed.json'):
                category = user.categories(refresh=True)[0]
        else:
            with vcr.use_cassette('fixtures/vcr_cassettes/categories.json'):
                category = user.categories()[0]

        return category

    def test_user_has_access_to_its_categories(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/categories.json'):
            self.assertIsInstance(user.categories(), list)

    def test_user_categories_are_cached_and_not_require_additional_request(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/categories.json', record_mode='once'):
            user.categories()
            user.categories()

    def test_user_categories_could_be_refreshed_from_the_server(self):
        user = self.get_me()
        with self.assertRaises(vcr_module.errors.CannotOverwriteExistingCassetteException):
            with vcr.use_cassette('fixtures/vcr_cassettes/categories.json', record_mode='once'):
                user.tasks(refresh=True)
                user.tasks(refresh=True)

    def test_user_categories_are_wrapped_as_objects(self):
        category = self.__get_category()
        self.assertIsInstance(category, Category)

    def test_category_has_appropriate_attributes(self):
        category = self.__get_category()

        self.assertEqual('Personal', category.name)
        self.assertEqual(True, category.isDefault)

    def test_category_attributes_accessible_directly(self):
        category = self.__get_category()

        self.assertEqual('Personal', category['name'])
        self.assertEqual(True, category['isDefault'])


    def test_category_could_be_updated_successfully_by_index(self):
        user = self.get_me()
        new_name = 'Home'
        # lastUpdateDate should be the actual one
        with vcr.use_cassette('fixtures/vcr_cassettes/categories_before_update.json'):
            category = user.categories(refresh=True)[0]

        with vcr.use_cassette('fixtures/vcr_cassettes/category_update_valid.json'):
            category['name'] = new_name
            category.save()
            self.assertEqual(new_name, category['name'])

        with vcr.use_cassette('fixtures/vcr_cassettes/category_updated.json'):
            category = next((cat for cat in user.categories(refresh=True) if cat['id'] == category['id']), None)
            self.assertEqual(new_name, category['name'])

    def test_user_could_be_updated_successfully_by_attribute(self):
        user = self.get_me()
        new_name = 'Home'

        with vcr.use_cassette('fixtures/vcr_cassettes/categories_before_update.json'):
            category = user.categories(refresh=True)[0]

        with vcr.use_cassette('fixtures/vcr_cassettes/category_update_valid.json'):
            category.name = new_name
            category.save()
            self.assertEqual(new_name, category.name)

        with vcr.use_cassette('fixtures/vcr_cassettes/category_updated.json'):
            category = next((cat for cat in user.categories(refresh=True) if cat['id'] == category['id']), None)
            self.assertEqual(new_name, category.name)

    def test_can_not_set_unmapped_attributes(self):
        category = self.__get_category()
        with self.assertRaises(AttributeError):
            category['suppa-duppa'] = 1

    def test_unchanged_data_dont_hit_an_api(self):
        category = self.__get_category()
        with vcr.use_cassette('fixtures/vcr_cassettes/fake.json', record_mode='none'):
            name = category.name
            category['name'] = name[:]
            category.save()

    def test_category_creation_returns_category_instance(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/category_create_valid.json'):
            category = Category.create(user=self.get_me(),
                name='Test Category',
            )
            self.assertIsInstance(category, Category)
            self.assertEqual('Test Category', category['name'])

    def test_category_creation_checks_required_fields(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/fake.json', record_mode='none'):
            with self.assertRaises(AttributeError):
                Category.create(user=self.get_me(), isDefault=False)

    def test_category_creation_reraises_occured_errors(self):
        # Emulate Server Error bypassing internal validaitons for missed fields
        original = Category.required_attributes
        def fake(): return set()
        Category.required_attributes = staticmethod(fake)

        with vcr.use_cassette('fixtures/vcr_cassettes/category_create_invalid.json'):
            with self.assertRaises(InternalServerError):
                Category.create(user=self.get_me(), isDefault=False)
        Category.required_attributes = staticmethod(original)

    def test_category_could_be_deleted_permanently_after_creation(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/category_create_for_delete.json'):
            category = Category.create(user=user, name='Delete me')

        with vcr.use_cassette('fixtures/vcr_cassettes/categories_after_new_one_created.json'):
            categories = user.categories(refresh=True)
            self.assertTrue(category['id'] in map(lambda cat: cat['id'], categories))

        with vcr.use_cassette('fixtures/vcr_cassettes/category_destroy_valid.json'):
            category.destroy()

        with vcr.use_cassette('fixtures/vcr_cassettes/categories_after_new_one_deleted.json'):
            categories = user.categories(refresh=True)
            self.assertFalse(category['id'] in map(lambda cat: cat['id'], categories))

    def test_new_category_could_be_deleted_permanently_after_creation(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/category_create_for_delete2.json'):
            Category.create(user=user, name='Delete me2')

        with vcr.use_cassette('fixtures/vcr_cassettes/categories_after_new_one_created2.json'):
            category = user.categories(refresh=True)[-1]
            self.assertEqual('Delete me2', category['name'])

        with vcr.use_cassette('fixtures/vcr_cassettes/category_destroy_valid2.json'):
            category.destroy()

        with vcr.use_cassette('fixtures/vcr_cassettes/categories_after_new_one_deleted2.json'):
            categories = user.categories(refresh=True)
            self.assertFalse(category['id'] in map(lambda cat: cat['id'], categories))

    def test_category_delete_is_an_alias_to_destroy(self):
        self.assertTrue(Category.delete == Category.destroy)

#    def test_category_could_be_marked_as_default(self):
#        user = self.get_me()
#        with vcr.use_cassette('fixtures/vcr_cassettes/tasks_before_mark.json'):
#            task = user.tasks()[0]
#            self.assertEqual('UNCHECKED', task['status'])
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/task_mark_done.json'):
#            task.done()
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/tasks_after_done.json'):
#            task = next((t for t in user.tasks(refresh=True, include_done=True) if t['id'] == task['id']), None)
#            self.assertEqual('DONE', task['status'])
#


#    def test_no_need_to_refresh_tasks_after_creation(self):
#        user = self.get_me()
#        with vcr.use_cassette('fixtures/vcr_cassettes/tasks.json'):
#            initial_size = len(user.tasks())
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/task_create_valid.json'):
#            new_task = Task.create(user=user, title='New Task')
#
#        self.assertTrue(new_task in user.tasks())
#

#    def test_task_has_notes(self):
#        task = self.__get_task()
#        self.assertEqual([], task.notes())
#
#    def test_text_notes_could_be_added_to_task(self):
#        user = self.get_me()
#        note = 'first one'
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/task_create_new_for_notes.json'):
#            task = Task.create(user=user, title='I have notes')
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/task_add_some_notes.json'):
#            task.add_note(note)
#
#        self.assertTrue(note in task.notes())
#
#    def test_tasks_filtered_by_done_status_without_refresh(self):
#        user = self.get_me()
#        with vcr.use_cassette('fixtures/vcr_cassettes/tasks_with_done.json'):
#            user.tasks(refresh=True, include_done=True)
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/fake.json', record_mode='none'):
#            none_done_tasks = user.tasks(include_done=False)
#            self.assertEqual(None, next((task for task in none_done_tasks if task['status'] == 'DONE'), None))
#
#    def test_tasks_filtered_by_deleted_status_without_refresh(self):
#        user = self.get_me()
#        with vcr.use_cassette('fixtures/vcr_cassettes/tasks_with_deleted.json'):
#            user.tasks(refresh=True, include_deleted=True)
#
#        with vcr.use_cassette('fixtures/vcr_cassettes/fake.json', record_mode='none'):
#            none_deleted_tasks = user.tasks(include_deleted=False)
#            self.assertEqual(None, next((task for task in none_deleted_tasks if task['status'] == 'DELETED'), None))

#default: false
#id: "e1zedRTQlOiPzV7SoFezrA=="
#isDefault: false
#isDeleted: false
#lastUpdateDate: 1445519283000
#name: "zzzzzzz"
#sharedMembers: null

#TEST
#  "default": false,
#  "isDefault": false,
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
