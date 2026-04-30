# coding=utf-8

from .._utils.model_base import Model as _Model


class EmptyInput(_Model):
    """Empty model used in operation parameters."""


class EmptyInputOutput(_Model):
    """Empty model used in both parameter and return type."""


class EmptyOutput(_Model):
    """Empty model used in operation return type."""
