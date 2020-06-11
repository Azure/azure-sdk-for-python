# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
Provides generic utility classes for the :class:`parse.Parser` class.
"""

from __future__ import absolute_import
from collections import namedtuple
import parse
import six


# -- HELPER-CLASS: For format part in a Field.
# REQUIRES: Python 2.6 or newer.
# pylint: disable=redefined-builtin, too-many-arguments
FormatSpec = namedtuple("FormatSpec",
                        ["type", "width", "zero", "align", "fill", "precision"])

def make_format_spec(type=None, width="", zero=False, align=None, fill=None,
                     precision=None):
    return FormatSpec(type, width, zero, align, fill, precision)
# pylint: enable=redefined-builtin

class Field(object):
    """
    Provides a ValueObject for a Field in a parse expression.

    Examples:
        * "{}"
        * "{name}"
        * "{:format}"
        * "{name:format}"

    Format specification: [[fill]align][0][width][.precision][type]
    """
    # pylint: disable=redefined-builtin
    ALIGN_CHARS = '<>=^'

    def __init__(self, name="", format=None):
        self.name = name
        self.format = format
        self._format_spec = None

    def set_format(self, format):
        self.format = format
        self._format_spec = None

    @property
    def has_format(self):
        return bool(self.format)

    @property
    def format_spec(self):
        if not self._format_spec and self.format:
            self._format_spec = self.extract_format_spec(self.format)
        return self._format_spec

    def __str__(self):
        name = self.name or ""
        if self.has_format:
            return "{%s:%s}" % (name, self.format)
        return "{%s}" % name

    def __eq__(self, other):
        if isinstance(other, Field):
            format1 = self.format or ""
            format2 = other.format or ""
            return (self.name == other.name) and (format1 == format2)
        elif isinstance(other, six.string_types):
            return str(self) == other
        else:
            raise ValueError(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def make_format(format_spec):
        """Build format string from a format specification.

        :param format_spec:     Format specification (as FormatSpec object).
        :return: Composed format (as string).
        """
        fill = ''
        align = ''
        zero = ''
        width = format_spec.width
        if format_spec.align:
            align = format_spec.align[0]
            if format_spec.fill:
                fill = format_spec.fill[0]
        if format_spec.zero:
            zero = '0'

        precision_part = ""
        if format_spec.precision:
            precision_part = ".%s" % format_spec.precision

        # -- FORMAT-SPEC: [[fill]align][0][width][.precision][type]
        return "%s%s%s%s%s%s" % (fill, align, zero, width,
                                 precision_part, format_spec.type)


    @classmethod
    def extract_format_spec(cls, format):
        """Pull apart the format: [[fill]align][0][width][.precision][type]"""
        # -- BASED-ON: parse.extract_format()
        # pylint: disable=redefined-builtin, unsubscriptable-object
        if not format:
            raise ValueError("INVALID-FORMAT: %s (empty-string)" % format)

        orig_format = format
        fill = align = None
        if format[0] in cls.ALIGN_CHARS:
            align = format[0]
            format = format[1:]
        elif len(format) > 1 and format[1] in cls.ALIGN_CHARS:
            fill = format[0]
            align = format[1]
            format = format[2:]

        zero = False
        if format and format[0] == '0':
            zero = True
            format = format[1:]

        width = ''
        while format:
            if not format[0].isdigit():
                break
            width += format[0]
            format = format[1:]

        precision = None
        if format.startswith('.'):
            # Precision isn't needed but we need to capture it so that
            # the ValueError isn't raised.
            format = format[1:]  # drop the '.'
            precision = ''
            while format:
                if not format[0].isdigit():
                    break
                precision += format[0]
                format = format[1:]

        # the rest is the type, if present
        type = format
        if not type:
            raise ValueError("INVALID-FORMAT: %s (without type)" % orig_format)
        return FormatSpec(type, width, zero, align, fill, precision)


class FieldParser(object):
    """
    Utility class that parses/extracts fields in parse expressions.
    """

    @classmethod
    def parse(cls, text):
        if not (text.startswith('{') and text.endswith('}')):
            message = "FIELD-SCHEMA MISMATCH: text='%s' (missing braces)" % text
            raise ValueError(message)

        # first: lose the braces
        text = text[1:-1]
        if ':' in text:
            # -- CASE: Typed field with format.
            name, format_ = text.split(':')
        else:
            name = text
            format_ = None
        return Field(name, format_)

    @classmethod
    def extract_fields(cls, schema):
        """Extract fields in a parse expression schema.

        :param schema: Parse expression schema/format to use (as string).
        :return: Generator for fields in schema (as Field objects).
        """
        # -- BASED-ON: parse.Parser._generate_expression()
        for part in parse.PARSE_RE.split(schema):
            if not part or part == '{{' or part == '}}':
                continue
            elif part[0] == '{':
                # this will be a braces-delimited field to handle
                yield cls.parse(part)

    @classmethod
    def extract_types(cls, schema):
        """Extract types (names) for typed fields (with format/type part).

        :param schema: Parser schema/format to use.
        :return: Generator for type names (as string).
        """
        for field in cls.extract_fields(schema):
            if field.has_format:
                yield field.format_spec.type
