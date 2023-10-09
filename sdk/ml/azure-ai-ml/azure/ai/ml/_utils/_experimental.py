# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
import inspect
import logging
import sys
from typing import Callable, Type, TypeVar, Union

from typing_extensions import ParamSpec

from azure.ai.ml.constants._common import (
    DOCSTRING_DEFAULT_INDENTATION,
    DOCSTRING_TEMPLATE,
    EXPERIMENTAL_CLASS_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
    EXPERIMENTAL_METHOD_MESSAGE,
)

_warning_cache = set()
module_logger = logging.getLogger(__name__)

TExperimental = TypeVar("TExperimental", bound=Union[Type, Callable])
P = ParamSpec("P")
T = TypeVar("T")


def experimental(wrapped: TExperimental) -> TExperimental:
    """Add experimental tag to a class or a method.

    :param wrapped: Either a Class or Function to mark as experimental
    :type wrapped: TExperimental
    :return: The wrapped class or method
    :rtype: TExperimental
    """
    if inspect.isclass(wrapped):
        return _add_class_docstring(wrapped)
    if inspect.isfunction(wrapped):
        return _add_method_docstring(wrapped)
    return wrapped


def _add_class_docstring(cls: Type[T]) -> Type[T]:
    """Add experimental tag to the class doc string.

    :return: The updated class
    :rtype: Type[T]
    """

    P2 = ParamSpec("P2")

    def _add_class_warning(func: Callable[P2, None]) -> Callable[P2, None]:
        """Add warning message for class __init__.

        :param func: The original __init__ function
        :type func: Callable[P2, None]
        :return: Updated __init__
        :rtype: Callable[P2, None]
        """

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


def _add_method_docstring(func: Callable[P, T] = None) -> Callable[P, T]:
    """Add experimental tag to the method doc string.

    :param func: The function to update
    :type func: Callable[P, T]
    :return: A wrapped method marked as experimental
    :rtype: Callable[P,T]
    """
    doc_string = DOCSTRING_TEMPLATE.format(EXPERIMENTAL_METHOD_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
    if func.__doc__:
        func.__doc__ = _add_note_to_docstring(func.__doc__, doc_string)
    else:
        # '>' is required. Otherwise the note section can't be generated
        func.__doc__ = doc_string + ">"

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        message = "Method {0}: {1} {2}".format(func.__name__, EXPERIMENTAL_METHOD_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
        if not _should_skip_warning() and not _is_warning_cached(message):
            module_logger.warning(message)
        return func(*args, **kwargs)

    return wrapped


def _add_note_to_docstring(doc_string: str, note: str) -> str:
    """Adds experimental note to docstring at the top and correctly indents original docstring.

    :param doc_string: The docstring
    :type doc_string: str
    :param note: The note to add to the docstring
    :type note: str
    :return: Updated docstring
    :rtype: str
    """
    indent = _get_indentation_size(doc_string)
    doc_string = doc_string.rjust(len(doc_string) + indent)
    return note + doc_string


def _get_indentation_size(doc_string: str) -> int:
    """Finds the minimum indentation of all non-blank lines after the first line.

    :param doc_string: The docstring
    :type doc_string: str
    :return: Minimum number of indentation of the docstring
    :rtype: int
    """
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
    _warning_cache.add(warning_msg)
    return False
