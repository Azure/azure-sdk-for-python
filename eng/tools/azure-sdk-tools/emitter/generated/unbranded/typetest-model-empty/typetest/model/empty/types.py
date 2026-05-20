# coding=utf-8

from typing_extensions import TypedDict


class EmptyInput(TypedDict, total=False):
    """Empty model used in operation parameters."""


class EmptyInputOutput(TypedDict, total=False):
    """Empty model used in both parameter and return type."""


class EmptyOutput(TypedDict, total=False):
    """Empty model used in operation return type."""
