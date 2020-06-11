# -*- coding: utf-8 -*-
"""
Importer module for lazy-loading/importing modules and objects.

REQUIRES: importlib (provided in Python2.7, Python3.2...)
"""

from __future__ import absolute_import
import importlib
from behave._types import Unknown

def parse_scoped_name(scoped_name):
    """
    SCHEMA: my.module_name:MyClassName
    EXAMPLE:
        behave.formatter.plain:PlainFormatter
    """
    scoped_name = scoped_name.strip()
    if "::" in scoped_name:
        # -- ALTERNATIVE: my.module_name::MyClassName
        scoped_name = scoped_name.replace("::", ":")
    module_name, object_name = scoped_name.rsplit(":", 1)
    return module_name, object_name

def load_module(module_name):
    return importlib.import_module(module_name)


class LazyObject(object):
    """
    Provides a placeholder for an object that should be loaded lazily.
    """

    def __init__(self, module_name, object_name=None):
        if ":" in module_name and not object_name:
            module_name, object_name = parse_scoped_name(module_name)
        assert ":" not in module_name
        self.module_name = module_name
        self.object_name = object_name
        self.resolved_object = None

    def __get__(self, obj=None, type=None):     # pylint: disable=redefined-builtin
        """
        Implement descriptor protocol,
        useful if this class is used as attribute.
        :return: Real object (lazy-loaded if necessary).
        :raise ImportError: If module or object cannot be imported.
        """
        __pychecker__ = "unusednames=obj,type"
        resolved_object = None
        if not self.resolved_object:
            # -- SETUP-ONCE: Lazy load the real object.
            module = load_module(self.module_name)
            resolved_object = getattr(module, self.object_name, Unknown)
            if resolved_object is Unknown:
                msg = "%s: %s is Unknown" % (self.module_name, self.object_name)
                raise ImportError(msg)
            self.resolved_object = resolved_object
        return resolved_object

    def __set__(self, obj, value):
        """Implement descriptor protocol."""
        __pychecker__ = "unusednames=obj"
        self.resolved_object = value

    def get(self):
        return self.__get__()


class LazyDict(dict):
    """
    Provides a dict that supports lazy loading of objects.
    A LazyObject is provided as placeholder for a value that should be
    loaded lazily.
    """

    def __getitem__(self, key):
        """
        Provides access to stored dict values.
        Implements lazy loading of item value (if necessary).
        When lazy object is loaded, its value with the dict is replaced
        with the real value.

        :param key:  Key to access the value of an item in the dict.
        :return: value
        :raises: KeyError if item is not found
        :raises: ImportError for a LazyObject that cannot be imported.
        """
        value = dict.__getitem__(self, key)
        if isinstance(value, LazyObject):
            # -- LAZY-LOADING MECHANISM: Load object and replace with lazy one.
            value = value.__get__()
            self[key] = value
        return value

    def load_all(self, strict=False):
        for key in self.keys():
            try:
                self.__getitem__(key)
            except ImportError:
                if strict:
                    raise
