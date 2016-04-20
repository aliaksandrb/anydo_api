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

from tests.base import TestCase
from tests.test_helper import vcr, scrub_string

from anydo_api import errors
from anydo_api.category import Category
from anydo_api.task import Task


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

    def test_categories_do_not_include_deleted_by_defaut(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/categories.json'):
            self.assertIsNone(next((cat for cat in user.categories() if cat['isDeleted']), None))

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
        with self.assertRaises(errors.ModelAttributeError):
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
            with self.assertRaises(errors.ModelAttributeError):
                Category.create(user=self.get_me(), isDefault=False)

    def test_category_creation_reraises_occured_errors(self):
        # Emulate Server Error bypassing internal validaitons for missed fields
        original = Category.required_attributes
        def fake(): return set()
        Category.required_attributes = staticmethod(fake)

        with vcr.use_cassette('fixtures/vcr_cassettes/category_create_invalid.json'):
            with self.assertRaises(errors.InternalServerError):
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

    def test_user_knows_about_default_category(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/categories.json'):
            category = user.default_category()
        self.assertEqual(True, category.isDefault)

    def test_category_could_be_marked_as_default(self):
        user = self.get_me()
        with vcr.use_cassette('fixtures/vcr_cassettes/categories_current_default.json'):
            default_old = user.default_category()

        new_default = user.categories()[0] if user.categories()[0] != default_old else user.categories()[1]

        with vcr.use_cassette('fixtures/vcr_cassettes/category_new_default.json', record_mode='new_episodes'):
            new_default.mark_default()

        with vcr.use_cassette('fixtures/vcr_cassettes/category_after_default_was_changed.json'):
            user.categories(refresh=True)
            self.assertFalse(new_default['id'] == default_old['id'])

    def test_no_need_to_refresh_categories_after_creation(self):
        user = self.get_me()

        with vcr.use_cassette('fixtures/vcr_cassettes/categories.json'):
            initial_size = len(user.categories())

        with vcr.use_cassette('fixtures/vcr_cassettes/category_create_valid.json'):
            category = Category.create(user=user, name='Test Category')

        self.assertTrue(category in user.categories())

    def test_category_has_tasks(self):
        category = self.__get_category()
        with vcr.use_cassette('fixtures/vcr_cassettes/tasks.json'):
            self.assertTrue(len(category.tasks()) > 0)

    def test_category_could_be_added_to_category(self):
        category = self.__get_category()

        with vcr.use_cassette('fixtures/vcr_cassettes/task_create_valid.json'):
            task = Task.create(user=category.user,
                title='Task For Category',
                priority='Normal',
                status='UNCHECKED'
            )

        with vcr.use_cassette('fixtures/vcr_cassettes/category_move_task_to_category.json'):
            category.add_task(task)

        self.assertEqual(category, task.category())
        self.assertTrue(task in category.tasks())

    def test_category_could_be_removed_from_not_default_category(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/categories.json'):
            categories = self.get_me().categories()
        category = categories[0] if not categories[0].isDefault else categories[1]

        with vcr.use_cassette('fixtures/vcr_cassettes/task_create_valid.json'):
            task = Task.create(user=category.user,
                title='Task For Category',
                priority='Normal',
                status='UNCHECKED'
            )

        with vcr.use_cassette('fixtures/vcr_cassettes/category_move_task_to_category.json'):
            category.add_task(task)

        with vcr.use_cassette('fixtures/vcr_cassettes/category_remove_task_from_category.json'):
            category.remove_task(task)

        self.assertNotEqual(category, task.category())
        self.assertEqual(category.user.default_category(), task.category())
        self.assertFalse(task in category.tasks())

    def test_categories_could_be_filtered_by_deleted_status_with_refresh(self):
        user = self.get_me()

        with vcr.use_cassette('fixtures/vcr_cassettes/category_deleted_ones.json'):
            deleted = user.categories(refresh=True, include_deleted=True)

        self.assertTrue(len(deleted) > 0)

        with vcr.use_cassette('fixtures/vcr_cassettes/fake.json', record_mode='none'):
            deleted2 = user.categories(include_deleted=True)

        self.assertEqual(deleted, deleted2)
        self.assertTrue(len([cat for cat in deleted2 if cat['isDeleted']]) > 0)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
