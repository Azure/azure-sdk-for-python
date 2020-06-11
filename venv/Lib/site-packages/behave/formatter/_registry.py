# -*- coding: utf-8 -*-

import sys
import warnings
from behave.formatter.base import Formatter, StreamOpener
from behave.importer import LazyDict, LazyObject, parse_scoped_name, load_module
import six


# -----------------------------------------------------------------------------
# FORMATTER REGISTRY:
# -----------------------------------------------------------------------------
_formatter_registry = LazyDict()

def format_iter():
    return iter(_formatter_registry.keys())

def format_items(resolved=False):
    if resolved:
        # -- ENSURE: All formatter classes are loaded (and resolved).
        _formatter_registry.load_all(strict=False)
    return iter(_formatter_registry.items())

def register_as(name, formatter_class):
    """
    Register formatter class with given name.

    :param name:  Name for this formatter (as identifier).
    :param formatter_class:  Formatter class to register.

    .. since:: 1.2.5
        Parameter ordering starts with name.
    """
    if not isinstance(name, six.string_types):
        # -- REORDER-PARAMS: Used old ordering before behave-1.2.5 (2015).
        warnings.warn("Use parameter ordering: name, formatter_class (for: %s)"\
                      % formatter_class)
        _formatter_class = name
        name = formatter_class
        formatter_class = _formatter_class

    if isinstance(formatter_class, six.string_types):
        # -- SPEEDUP-STARTUP: Only import formatter_class when used.
        scoped_formatter_class_name = formatter_class
        formatter_class = LazyObject(scoped_formatter_class_name)
    assert (isinstance(formatter_class, LazyObject) or
            issubclass(formatter_class, Formatter))
    _formatter_registry[name] = formatter_class

def register(formatter_class):
    register_as(formatter_class.name, formatter_class)

def register_formats(formats):
    """Register many format items into the registry.

    :param formats:  List of format items (as: (name, class|class_name)).
    """
    for formatter_name, formatter_class_name in formats:
        register_as(formatter_name, formatter_class_name)

def load_formatter_class(scoped_class_name):
    """Load a formatter class by using its scoped class name.

    :param scoped_class_name:  Formatter module and class name (as string).
    :return: Formatter class.
    :raises: ValueError, if scoped_class_name is invalid.
    :raises: ImportError, if module cannot be loaded or class is not in module.
    """
    if ":" not in scoped_class_name:
        message = 'REQUIRE: "module:class", but was: "%s"' % scoped_class_name
        raise ValueError(message)
    module_name, class_name = parse_scoped_name(scoped_class_name)
    formatter_module = load_module(module_name)
    formatter_class = getattr(formatter_module, class_name, None)
    if formatter_class is None:
        raise ImportError("CLASS NOT FOUND: %s" % scoped_class_name)
    return formatter_class


def select_formatter_class(formatter_name):
    """Resolve the formatter class by:

      * using one of the registered ones
      * loading a user-specified formatter class (like: my.module_name:MyClass)

    :param formatter_name:  Name of the formatter or scoped name (as string).
    :return: Formatter class
    :raises: LookupError, if not found.
    :raises: ImportError, if a user-specific formatter class cannot be loaded.
    :raises: ValueError, if formatter name is invalid.
    """
    try:
        return _formatter_registry[formatter_name]
    except KeyError:
        # -- NOT-FOUND:
        if ":" not in formatter_name:
            raise
        # -- OTHERWISE: SCOPED-NAME, try to load a user-specific formatter.
        # MAY RAISE: ImportError
        return load_formatter_class(formatter_name)


def is_formatter_valid(formatter_name):
    """Checks if the formatter is known (registered) or loadable.

    :param formatter_name: Format(ter) name to check (as string).
    :return: True, if formatter is known or can be loaded.
    """
    try:
        formatter_class = select_formatter_class(formatter_name)
        return issubclass(formatter_class, Formatter)
    except (LookupError, ImportError, ValueError):
        return False


def make_formatters(config, stream_openers):
    """Build a list of formatter, used by a behave runner.

    :param config:  Configuration object to use.
    :param stream_openers: List of stream openers to use (for formatters).
    :return: List of formatters.
    :raises: LookupError/KeyError if a formatter class is unknown.
    :raises: ImportError, if a formatter class cannot be loaded/resolved.
    """
    # -- BUILD: Formatter list
    default_stream_opener = StreamOpener(stream=sys.stdout)
    formatter_list = []
    for i, name in enumerate(config.format):
        stream_opener = default_stream_opener
        if i < len(stream_openers):
            stream_opener = stream_openers[i]
        formatter_class = select_formatter_class(name)
        formatter_object = formatter_class(stream_opener, config)
        formatter_list.append(formatter_object)
    return formatter_list
