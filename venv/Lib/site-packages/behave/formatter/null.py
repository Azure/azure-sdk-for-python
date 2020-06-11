# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.formatter.base import Formatter

class NullFormatter(Formatter):
    """
    Provides formatter that does not output anything.
    Implements the NULL pattern for a formatter (similar like: /dev/null).
    """
    name = "null"
    description = "Provides formatter that does not output anything."
