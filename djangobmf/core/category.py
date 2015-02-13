#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils import six

from collections import OrderedDict

from .view import View


class CategoryMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(CategoryMetaclass, cls).__new__
        parents = [
            b for b in bases if
            isinstance(b, CategoryMetaclass)
            and not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class.
        new_cls = super_new(cls, name, bases, attrs)

        # validation
        # TODO add validation for name and slug

        # TODO remove me (old syntax)
        if hasattr(new_cls, 'Meta'):
            new_cls.name = getattr(new_cls.Meta, 'name', None)
            new_cls.slug = getattr(new_cls.Meta, 'slug', None)

        return new_cls


class Category(six.with_metaclass(CategoryMetaclass, object)):

    def __init__(self, *args):
        self.data = OrderedDict()
        self.models = []

        # the dashboards gets set during the registation
        self.dashboard = None  # auto

        for view in args:
            self.add_view(view)

        # we add a key to add a unique identifier
        # the key is equal to the slug (for now) but this
        # gives us the opportunity to add i18n urls later
        self.key = self.slug

    @classmethod
    def views(cls, *views):
        return cls, views

    def __bool__(self):
        return bool(self.data)

    def __nonzero__(self):
        return self.__bool__()

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        if isinstance(other, Category):
            return self.key == other.key
        else:
            return False

    def __iter__(self):
        return self.data.values().__iter__()

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, item):
        if isinstance(item, View):
            key = item.key
        else:
            key = item
        return key in self.data

    def add_view(self, view):
        """
        Adds a view to the category
        """
        if view not in self.data.values():
            if view.model not in self.models:
                self.models.append(view.model)
            self.data[view.key] = view

    def merge(self, other):
        """
        merges two categories
        """
        for view in other.data.values():
            self.add_view(view)
