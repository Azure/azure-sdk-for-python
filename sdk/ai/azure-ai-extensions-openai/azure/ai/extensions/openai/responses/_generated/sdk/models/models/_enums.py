# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Compatibility enum module for TypedDict generation.

TypedDict mode emits enum-like aliases in ``types.py`` but older emitter
builds can still import this module from generated type hints.
"""


class _EnumMemberFallback(str):
    @property
    def value(self) -> str:
        return str(self)


def _member_value(enum_name: str, member_name: str) -> str:
    if enum_name == "ResponseStreamEventType":
        return member_name.lower().replace("_", ".")
    return member_name.lower()


class _EnumFallbackMeta(type):
    def __getattr__(cls, name: str) -> _EnumMemberFallback:
        return _EnumMemberFallback(_member_value(cls.__name__, name))


class _EnumFallback(str, metaclass=_EnumFallbackMeta):
    """Fallback object for enum names referenced by generated code."""


def __getattr__(name: str) -> type[_EnumFallback]:
    return type(name, (_EnumFallback,), {})
