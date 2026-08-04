# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``@experimental`` marker for the preview Voice submodule.

The Voice Live Bridge public surface is still in preview. Marking each public
class with :func:`experimental` records that intent for API review tooling and
adds a note to the rendered documentation, and emits a one-time log warning the
first time an experimental type is instantiated.
"""

import functools
import inspect
import logging
from typing import Callable, Type, TypeVar, Union, overload

_LOGGER = logging.getLogger(__name__)

_CLASS_MESSAGE = "This is an experimental class, and may change at any time."
_METHOD_MESSAGE = "This is an experimental method, and may change at any time."

_warned: set = set()

T = TypeVar("T")


@overload
def experimental(wrapped: Type[T]) -> Type[T]: ...


@overload
def experimental(wrapped: Callable[..., T]) -> Callable[..., T]: ...


def experimental(wrapped: Union[Type[T], Callable[..., T]]) -> Union[Type[T], Callable[..., T]]:
    """Mark a class or function as an experimental (preview) public API.

    :param wrapped: The class or function to mark as experimental.
    :type wrapped: Union[Type[T], Callable[..., T]]
    :return: The same class or function, annotated as experimental.
    :rtype: Union[Type[T], Callable[..., T]]
    """
    if isinstance(wrapped, type):
        return _decorate_class(wrapped)
    if inspect.isfunction(wrapped):
        return _decorate_function(wrapped)
    return wrapped


def _warn_once(name: str, message: str) -> None:
    if name not in _warned:
        _warned.add(name)
        _LOGGER.warning("%s: %s", name, message)


def _prepend_note(doc: Union[str, None], message: str) -> str:
    note = ".. note::    {}\n\n".format(message)
    return note + doc if doc else note


def _decorate_class(cls: Type[T]) -> Type[T]:
    cls.__doc__ = _prepend_note(cls.__doc__, _CLASS_MESSAGE)
    # Only wrap an ``__init__`` the class defines itself as a real Python function.
    # Classes without their own ``__init__`` (e.g. exception subclasses) inherit a
    # C-level slot wrapper; wrapping that with ``functools.wraps`` would set
    # ``__wrapped__`` to a ``wrapper_descriptor``, which breaks source-inspecting
    # tools such as the APIView stub generator (``inspect.getfile`` raises
    # ``TypeError`` on it). The docstring note above still marks the class.
    original_init = cls.__dict__.get("__init__")
    if inspect.isfunction(original_init):

        @functools.wraps(original_init)
        def _init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            _warn_once(cls.__name__, _CLASS_MESSAGE)
            original_init(self, *args, **kwargs)

        cls.__init__ = _init  # type: ignore[method-assign]
    return cls


def _decorate_function(func: Callable[..., T]) -> Callable[..., T]:
    func.__doc__ = _prepend_note(func.__doc__, _METHOD_MESSAGE)

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        _warn_once(func.__qualname__, _METHOD_MESSAGE)
        return func(*args, **kwargs)

    return _wrapper
