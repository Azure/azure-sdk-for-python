# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
r"""
Provides support to compose user-defined parse types.

Cardinality
------------

It is often useful to constrain how often a data type occurs.
This is also called the cardinality of a data type (in a context).
The supported cardinality are:

  * 0..1  zero_or_one,  optional<T>: T or None
  * 0..N  zero_or_more, list_of<T>
  * 1..N  one_or_more,  list_of<T> (many)


.. doctest:: cardinality

    >>> from parse_type import TypeBuilder
    >>> from parse import Parser

    >>> def parse_number(text):
    ...     return int(text)
    >>> parse_number.pattern = r"\d+"

    >>> parse_many_numbers = TypeBuilder.with_many(parse_number)
    >>> more_types = { "Numbers": parse_many_numbers }
    >>> parser = Parser("List: {numbers:Numbers}", more_types)
    >>> parser.parse("List: 1, 2, 3")
    <Result () {'numbers': [1, 2, 3]}>


Enumeration Type (Name-to-Value Mappings)
-----------------------------------------

An Enumeration data type allows to select one of several enum values by using
its name. The converter function returns the selected enum value.

.. doctest:: make_enum

    >>> parse_enum_yesno = TypeBuilder.make_enum({"yes": True, "no": False})
    >>> more_types = { "YesNo": parse_enum_yesno }
    >>> parser = Parser("Answer: {answer:YesNo}", more_types)
    >>> parser.parse("Answer: yes")
    <Result () {'answer': True}>


Choice (Name Enumerations)
-----------------------------

A Choice data type allows to select one of several strings.

.. doctest:: make_choice

    >>> parse_choice_yesno = TypeBuilder.make_choice(["yes", "no"])
    >>> more_types = { "ChoiceYesNo": parse_choice_yesno }
    >>> parser = Parser("Answer: {answer:ChoiceYesNo}", more_types)
    >>> parser.parse("Answer: yes")
    <Result () {'answer': 'yes'}>

"""

from __future__ import absolute_import
import inspect
import re
import enum
from parse_type.cardinality import pattern_group_count, \
    Cardinality, TypeBuilder as CardinalityTypeBuilder

__all__ = ["TypeBuilder", "build_type_dict", "parse_anything"]


class TypeBuilder(CardinalityTypeBuilder):
    """
    Provides a utility class to build type-converters (parse_types) for
    the :mod:`parse` module.
    """
    default_strict = True
    default_re_opts = (re.IGNORECASE | re.DOTALL)

    @classmethod
    def make_list(cls, item_converter=None, listsep=','):
        """
        Create a type converter for a list of items (many := 1..*).
        The parser accepts anything and the converter needs to fail on errors.

        :param item_converter:  Type converter for an item.
        :param listsep:  List separator to use (as string).
        :return: Type converter function object for the list.
        """
        if not item_converter:
            item_converter = parse_anything
        return cls.with_cardinality(Cardinality.many, item_converter,
                                    pattern=cls.anything_pattern,
                                    listsep=listsep)

    @staticmethod
    def make_enum(enum_mappings):
        """
        Creates a type converter for an enumeration or text-to-value mapping.

        :param enum_mappings: Defines enumeration names and values.
        :return: Type converter function object for the enum/mapping.
        """
        if (inspect.isclass(enum_mappings) and
                issubclass(enum_mappings, enum.Enum)):
            enum_class = enum_mappings
            enum_mappings = enum_class.__members__

        def convert_enum(text):
            if text not in convert_enum.mappings:
                text = text.lower()     # REQUIRED-BY: parse re.IGNORECASE
            return convert_enum.mappings[text]    #< text.lower() ???
        convert_enum.pattern = r"|".join(enum_mappings.keys())
        convert_enum.mappings = enum_mappings
        return convert_enum

    @staticmethod
    def _normalize_choices(choices, transform):
        assert transform is None or callable(transform)
        if transform:
            choices = [transform(value)  for value in choices]
        else:
            choices = list(choices)
        return choices

    @classmethod
    def make_choice(cls, choices, transform=None, strict=None):
        """
        Creates a type-converter function to select one from a list of strings.
        The type-converter function returns the selected choice_text.
        The :param:`transform()` function is applied in the type converter.
        It can be used to enforce the case (because parser uses re.IGNORECASE).

        :param choices: List of strings as choice.
        :param transform: Optional, initial transform function for parsed text.
        :return: Type converter function object for this choices.
        """
        # -- NOTE: Parser uses re.IGNORECASE flag
        #    => transform may enforce case.
        choices = cls._normalize_choices(choices, transform)
        if strict is None:
            strict = cls.default_strict

        def convert_choice(text):
            if transform:
                text = transform(text)
            if strict and text not in convert_choice.choices:
                values = ", ".join(convert_choice.choices)
                raise ValueError("%s not in: %s" % (text, values))
            return text
        convert_choice.pattern = r"|".join(choices)
        convert_choice.choices = choices
        return convert_choice

    @classmethod
    def make_choice2(cls, choices, transform=None, strict=None):
        """
        Creates a type converter to select one item from a list of strings.
        The type converter function returns a tuple (index, choice_text).

        :param choices: List of strings as choice.
        :param transform: Optional, initial transform function for parsed text.
        :return: Type converter function object for this choices.
        """
        choices = cls._normalize_choices(choices, transform)
        if strict is None:
            strict = cls.default_strict

        def convert_choice2(text):
            if transform:
                text = transform(text)
            if strict and text not in convert_choice2.choices:
                values = ", ".join(convert_choice2.choices)
                raise ValueError("%s not in: %s" % (text, values))
            index = convert_choice2.choices.index(text)
            return index, text
        convert_choice2.pattern = r"|".join(choices)
        convert_choice2.choices = choices
        return convert_choice2

    @classmethod
    def make_variant(cls, converters, re_opts=None, compiled=False, strict=True):
        """
        Creates a type converter for a number of type converter alternatives.
        The first matching type converter is used.

        REQUIRES: type_converter.pattern attribute

        :param converters: List of type converters as alternatives.
        :param re_opts:  Regular expression options zu use (=default_re_opts).
        :param compiled: Use compiled regexp matcher, if true (=False).
        :param strict:   Enable assertion checks.
        :return: Type converter function object.

        .. note::

            Works only with named fields in :class:`parse.Parser`.
            Parser needs group_index delta for unnamed/fixed fields.
            This is not supported for user-defined types.
            Otherwise, you need to use :class:`parse_type.parse.Parser`
            (patched version of the :mod:`parse` module).
        """
        # -- NOTE: Uses double-dispatch with regex pattern rematch because
        #          match is not passed through to primary type converter.
        assert converters, "REQUIRE: Non-empty list."
        if len(converters) == 1:
            return converters[0]
        if re_opts is None:
            re_opts = cls.default_re_opts

        pattern = r")|(".join([tc.pattern for tc in converters])
        pattern = r"("+ pattern + ")"
        group_count = len(converters)
        for converter in converters:
            group_count += pattern_group_count(converter.pattern)

        if compiled:
            convert_variant = cls.__create_convert_variant_compiled(converters,
                                                                    re_opts,
                                                                    strict)
        else:
            convert_variant = cls.__create_convert_variant(re_opts, strict)
        convert_variant.pattern = pattern
        convert_variant.converters = tuple(converters)
        convert_variant.regex_group_count = group_count
        return convert_variant

    @staticmethod
    def __create_convert_variant(re_opts, strict):
        # -- USE: Regular expression pattern (compiled on use).
        def convert_variant(text, m=None):
            # pylint: disable=invalid-name, unused-argument, missing-docstring
            for converter in convert_variant.converters:
                if re.match(converter.pattern, text, re_opts):
                    return converter(text)
            # -- pragma: no cover
            assert not strict, "OOPS-VARIANT-MISMATCH: %s" % text
            return None
        return convert_variant

    @staticmethod
    def __create_convert_variant_compiled(converters, re_opts, strict):
        # -- USE: Compiled regular expression matcher.
        for converter in converters:
            matcher = getattr(converter, "matcher", None)
            if not matcher:
                converter.matcher = re.compile(converter.pattern, re_opts)

        def convert_variant(text, m=None):
            # pylint: disable=invalid-name, unused-argument, missing-docstring
            for converter in convert_variant.converters:
                if converter.matcher.match(text):
                    return converter(text)
            # -- pragma: no cover
            assert not strict, "OOPS-VARIANT-MISMATCH: %s" % text
            return None
        return convert_variant


def build_type_dict(converters):
    """
    Builds type dictionary for user-defined type converters,
    used by :mod:`parse` module.
    This requires that each type converter has a "name" attribute.

    :param converters: List of type converters (parse_types)
    :return: Type converter dictionary
    """
    more_types = {}
    for converter in converters:
        assert callable(converter)
        more_types[converter.name] = converter
    return more_types

# -----------------------------------------------------------------------------
# COMMON TYPE CONVERTERS
# -----------------------------------------------------------------------------
def parse_anything(text, match=None, match_start=0):
    """
    Provides a generic type converter that accepts anything and returns
    the text (unchanged).

    :param text:  Text to convert (as string).
    :return: Same text (as string).
    """
    # pylint: disable=unused-argument
    return text
parse_anything.pattern = TypeBuilder.anything_pattern


# -----------------------------------------------------------------------------
# Copyright (c) 2012-2017 by Jens Engel (https://github/jenisys/parse_type)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
