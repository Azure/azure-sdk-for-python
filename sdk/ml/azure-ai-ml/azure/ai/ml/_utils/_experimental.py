# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
import logging
import inspect
import sys
from azure.ai.ml.constants import (
    DOCSTRING_TEMPLATE,
    DOCSTRING_DEFAULT_INDENTATION,
    EXPERIMENTAL_CLASS_MESSAGE,
    EXPERIMENTAL_METHOD_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
)

_warning_cache = set()
module_logger = logging.getLogger(__name__)


def experimental(wrapped):
    """Add experimental tag to a class or a method"""
    if inspect.isclass(wrapped):
        return _add_class_docstring(wrapped)
    elif inspect.isfunction(wrapped):
        return _add_method_docstring(wrapped)
    else:
        return wrapped


def _add_class_docstring(cls):
    """Add experimental tag to the class doc string"""

    def _add_class_warning(func=None):
        """Add warning message for class init"""

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            message = "Class {0}: {1} {2}".format(cls.__name__, EXPERIMENTAL_CLASS_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
            if not _should_skip_warning() and not _is_warning_cached(message):
                module_logger.warning(message)
            return func(*args, **kwargs)

        return wrapped

    doc_string = DOCSTRING_TEMPLATE.format(EXPERIMENTAL_CLASS_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
    if cls.__doc__:
        cls.__doc__ = _add_note_to_docstring(cls.__doc__, doc_string)
    else:
        cls.__doc__ = doc_string + ">"
    cls.__init__ = _add_class_warning(cls.__init__)
    return cls


def _add_method_docstring(func=None):
    """Add experimental tag to the method doc string"""
    doc_string = DOCSTRING_TEMPLATE.format(EXPERIMENTAL_METHOD_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
    if func.__doc__:
        func.__doc__ = _add_note_to_docstring(func.__doc__, doc_string)
    else:
        # '>' is required. Otherwise the note section can't be generated
        func.__doc__ = doc_string + ">"

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        message = "Method {0}: {1} {2}".format(func.__name__, EXPERIMENTAL_METHOD_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
        if not _should_skip_warning() and not _is_warning_cached(message):
            module_logger.warning(message)
        return func(*args, **kwargs)

    return wrapped


def _add_note_to_docstring(doc_string, note):
    """Adds experimental note to docstring at the top and
    correctly indents original docstring.
    """
    indent = _get_indentation_size(doc_string)
    doc_string = doc_string.rjust(len(doc_string) + indent)
    return note + doc_string


def _get_indentation_size(doc_string):
    """Finds the minimum indentation of all non-blank lines after the first line"""
    lines = doc_string.expandtabs().splitlines()
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    return indent if indent < sys.maxsize else DOCSTRING_DEFAULT_INDENTATION


def _should_skip_warning():
    skip_warning_msg = False

    # Cases where we want to suppress the warning:
    # 1. When converting from REST object to SDK object
    for frame in inspect.stack():
        if frame.function == "_from_rest_object":
            skip_warning_msg = True
            break

    return skip_warning_msg


def _is_warning_cached(warning_msg):

    # use cache to make sure we only print same warning message once under same session
    # this prevents duplicated warnings got printed when user does a loop call on a method or a class
    if warning_msg in _warning_cache:
        return True
    else:
        _warning_cache.add(warning_msg)
        return False
