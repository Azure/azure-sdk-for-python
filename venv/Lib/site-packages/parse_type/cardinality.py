# -*- coding: utf-8 -*-
"""
This module simplifies to build parse types and regular expressions
for a data type with the specified cardinality.
"""

# -- USE: enum34
from __future__ import absolute_import
from enum import Enum


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def pattern_group_count(pattern):
    """Count the pattern-groups within a regex-pattern (as text)."""
    return pattern.replace(r"\(", "").count("(")


# -----------------------------------------------------------------------------
# CLASS: Cardinality (Enum Class)
# -----------------------------------------------------------------------------
class Cardinality(Enum):
    """Cardinality enumeration class to simplify building regular expression
    patterns for a data type with the specified cardinality.
    """
    # pylint: disable=bad-whitespace
    __order__ = "one, zero_or_one, zero_or_more, one_or_more"
    one          = (None, 0)
    zero_or_one  = (r"(%s)?", 1)                 # SCHEMA: pattern
    zero_or_more = (r"(%s)?(\s*%s\s*(%s))*", 3)  # SCHEMA: pattern sep pattern
    one_or_more  = (r"(%s)(\s*%s\s*(%s))*",  3)  # SCHEMA: pattern sep pattern

    # -- ALIASES:
    optional = zero_or_one
    many0 = zero_or_more
    many  = one_or_more

    def __init__(self, schema, group_count=0):
        self.schema = schema
        self.group_count = group_count  #< Number of match groups.

    def is_many(self):
        """Checks for a more general interpretation of "many".

        :return: True, if Cardinality.zero_or_more or Cardinality.one_or_more.
        """
        return ((self is Cardinality.zero_or_more) or
                (self is Cardinality.one_or_more))

    def make_pattern(self, pattern, listsep=','):
        """Make pattern for a data type with the specified cardinality.

        .. code-block:: python

            yes_no_pattern = r"yes|no"
            many_yes_no = Cardinality.one_or_more.make_pattern(yes_no_pattern)

        :param pattern:  Regular expression for type (as string).
        :param listsep:  List separator for multiple items (as string, optional)
        :return: Regular expression pattern for type with cardinality.
        """
        if self is Cardinality.one:
            return pattern
        elif self is Cardinality.zero_or_one:
            return self.schema % pattern
        # -- OTHERWISE:
        return self.schema % (pattern, listsep, pattern)

    def compute_group_count(self, pattern):
        """Compute the number of regexp match groups when the pattern is provided
        to the :func:`Cardinality.make_pattern()` method.

        :param pattern: Item regexp pattern (as string).
        :return: Number of regexp match groups in the cardinality pattern.
        """
        group_count = self.group_count
        pattern_repeated = 1
        if self.is_many():
            pattern_repeated = 2
        return group_count + pattern_repeated * pattern_group_count(pattern)


# -----------------------------------------------------------------------------
# CLASS: TypeBuilder
# -----------------------------------------------------------------------------
class TypeBuilder(object):
    """Provides a utility class to build type-converters (parse_types) for parse.
    It supports to build new type-converters for different cardinality
    based on the type-converter for cardinality one.
    """
    anything_pattern = r".+?"
    default_pattern = anything_pattern

    @classmethod
    def with_cardinality(cls, cardinality, converter, pattern=None,
                         listsep=','):
        """Creates a type converter for the specified cardinality
        by using the type converter for T.

        :param cardinality: Cardinality to use (0..1, 0..*, 1..*).
        :param converter: Type converter (function) for data type T.
        :param pattern:  Regexp pattern for an item (=converter.pattern).
        :return: type-converter for optional<T> (T or None).
        """
        if cardinality is Cardinality.one:
            return converter
        # -- NORMAL-CASE
        builder_func = getattr(cls, "with_%s" % cardinality.name)
        if cardinality is Cardinality.zero_or_one:
            return builder_func(converter, pattern)
        # -- MANY CASE: 0..*, 1..*
        return builder_func(converter, pattern, listsep=listsep)

    @classmethod
    def with_zero_or_one(cls, converter, pattern=None):
        """Creates a type converter for a T with 0..1 times
        by using the type converter for one item of T.

        :param converter: Type converter (function) for data type T.
        :param pattern:  Regexp pattern for an item (=converter.pattern).
        :return: type-converter for optional<T> (T or None).
        """
        cardinality = Cardinality.zero_or_one
        if not pattern:
            pattern = getattr(converter, "pattern", cls.default_pattern)
        optional_pattern = cardinality.make_pattern(pattern)
        group_count = cardinality.compute_group_count(pattern)

        def convert_optional(text, m=None):
            # pylint: disable=invalid-name, unused-argument, missing-docstring
            if text:
                text = text.strip()
            if not text:
                return None
            return converter(text)
        convert_optional.pattern = optional_pattern
        convert_optional.regex_group_count = group_count
        return convert_optional

    @classmethod
    def with_zero_or_more(cls, converter, pattern=None, listsep=","):
        """Creates a type converter function for a list<T> with 0..N items
        by using the type converter for one item of T.

        :param converter: Type converter (function) for data type T.
        :param pattern:  Regexp pattern for an item (=converter.pattern).
        :param listsep:  Optional list separator between items (default: ',')
        :return: type-converter for list<T>
        """
        cardinality = Cardinality.zero_or_more
        if not pattern:
            pattern = getattr(converter, "pattern", cls.default_pattern)
        many0_pattern = cardinality.make_pattern(pattern, listsep)
        group_count = cardinality.compute_group_count(pattern)

        def convert_list0(text, m=None):
            # pylint: disable=invalid-name, unused-argument, missing-docstring
            if text:
                text = text.strip()
            if not text:
                return []
            return [converter(part.strip()) for part in text.split(listsep)]
        convert_list0.pattern = many0_pattern
        # OLD convert_list0.group_count = group_count
        convert_list0.regex_group_count = group_count
        return convert_list0

    @classmethod
    def with_one_or_more(cls, converter, pattern=None, listsep=","):
        """Creates a type converter function for a list<T> with 1..N items
        by using the type converter for one item of T.

        :param converter: Type converter (function) for data type T.
        :param pattern:  Regexp pattern for an item (=converter.pattern).
        :param listsep:  Optional list separator between items (default: ',')
        :return: Type converter for list<T>
        """
        cardinality = Cardinality.one_or_more
        if not pattern:
            pattern = getattr(converter, "pattern", cls.default_pattern)
        many_pattern = cardinality.make_pattern(pattern, listsep)
        group_count = cardinality.compute_group_count(pattern)

        def convert_list(text, m=None):
            # pylint: disable=invalid-name, unused-argument, missing-docstring
            return [converter(part.strip()) for part in text.split(listsep)]
        convert_list.pattern = many_pattern
        # OLD: convert_list.group_count = group_count
        convert_list.regex_group_count = group_count
        return convert_list

    # -- ALIAS METHODS:
    @classmethod
    def with_optional(cls, converter, pattern=None):
        """Alias for :py:meth:`with_zero_or_one()` method."""
        return cls.with_zero_or_one(converter, pattern)

    @classmethod
    def with_many(cls, converter, pattern=None, listsep=','):
        """Alias for :py:meth:`with_one_or_more()` method."""
        return cls.with_one_or_more(converter, pattern, listsep)

    @classmethod
    def with_many0(cls, converter, pattern=None, listsep=','):
        """Alias for :py:meth:`with_zero_or_more()` method."""
        return cls.with_zero_or_more(converter, pattern, listsep)
