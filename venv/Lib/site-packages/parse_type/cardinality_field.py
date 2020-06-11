# -*- coding: utf-8 -*-
"""
Provides support for cardinality fields.
A cardinality field is a type suffix for parse format expression, ala:

    "{person:Person?}"   #< Cardinality: 0..1 = zero or one  = optional
    "{persons:Person*}"  #< Cardinality: 0..* = zero or more = many0
    "{persons:Person+}"  #< Cardinality: 1..* = one  or more = many
"""

from __future__ import absolute_import
import six
from parse_type.cardinality import Cardinality, TypeBuilder


class MissingTypeError(KeyError):   # pylint: disable=missing-docstring
    pass

# -----------------------------------------------------------------------------
# CLASS: Cardinality (Field Part)
# -----------------------------------------------------------------------------
class CardinalityField(object):
    """Cardinality field for parse format expression, ala:

        "{person:Person?}"   #< Cardinality: 0..1 = zero or one  = optional
        "{persons:Person*}"  #< Cardinality: 0..* = zero or more = many0
        "{persons:Person+}"  #< Cardinality: 1..* = one  or more = many
    """

    # -- MAPPING SUPPORT:
    pattern_chars = "?*+"
    from_char_map = {
        '?': Cardinality.zero_or_one,
        '*': Cardinality.zero_or_more,
        '+': Cardinality.one_or_more,
    }
    to_char_map = dict([(value, key)  for key, value in from_char_map.items()])

    @classmethod
    def matches_type(cls, type_name):
        """Checks if a type name uses the CardinalityField naming scheme.

        :param type_name:  Type name to check (as string).
        :return: True, if type name has CardinalityField name suffix.
        """
        return type_name and type_name[-1] in CardinalityField.pattern_chars

    @classmethod
    def split_type(cls, type_name):
        """Split type of a type name with CardinalityField suffix into its parts.

        :param type_name:  Type name (as string).
        :return: Tuple (type_basename, cardinality)
        """
        if cls.matches_type(type_name):
            basename = type_name[:-1]
            cardinality = cls.from_char_map[type_name[-1]]
        else:
            # -- ASSUME: Cardinality.one
            cardinality = Cardinality.one
            basename = type_name
        return (basename, cardinality)

    @classmethod
    def make_type(cls, basename, cardinality):
        """Build new type name according to CardinalityField naming scheme.

        :param basename:  Type basename of primary type (as string).
        :param cardinality: Cardinality of the new type (as Cardinality item).
        :return: Type name with CardinalityField suffix (if needed)
        """
        if cardinality is Cardinality.one:
            # -- POSTCONDITION: assert not cls.make_type(type_name)
            return basename
        # -- NORMAL CASE: type with CardinalityField suffix.
        type_name = "%s%s" % (basename, cls.to_char_map[cardinality])
        # -- POSTCONDITION: assert cls.make_type(type_name)
        return type_name


# -----------------------------------------------------------------------------
# CLASS: CardinalityFieldTypeBuilder
# -----------------------------------------------------------------------------
class CardinalityFieldTypeBuilder(object):
    """Utility class to create type converters based on:

      * the CardinalityField naming scheme and
      * type converter for cardinality=1
    """

    listsep = ','

    @classmethod
    def create_type_variant(cls, type_name, type_converter):
        r"""Create type variants for types with a cardinality field.
        The new type converters are based on the type converter with
        cardinality=1.

        .. code-block:: python

            import parse

            @parse.with_pattern(r'\d+')
            def parse_number(text):
                return int(text)

            new_type = CardinalityFieldTypeBuilder.create_type_variant(
                                    "Number+", parse_number)
            new_type = CardinalityFieldTypeBuilder.create_type_variant(
                                    "Number+", dict(Number=parse_number))

        :param type_name:  Type name with cardinality field suffix.
        :param type_converter:  Type converter or type dictionary.
        :return: Type converter variant (function).
        :raises: ValueError, if type_name does not end with CardinalityField
        :raises: MissingTypeError, if type_converter is missing in type_dict
        """
        assert isinstance(type_name, six.string_types)
        if not CardinalityField.matches_type(type_name):
            message = "type_name='%s' has no CardinalityField" % type_name
            raise ValueError(message)

        primary_name, cardinality = CardinalityField.split_type(type_name)
        if isinstance(type_converter, dict):
            type_dict = type_converter
            type_converter = type_dict.get(primary_name, None)
            if not type_converter:
                raise MissingTypeError(primary_name)

        assert callable(type_converter)
        type_variant = TypeBuilder.with_cardinality(cardinality,
                                                    type_converter,
                                                    listsep=cls.listsep)
        type_variant.name = type_name
        return type_variant


    @classmethod
    def create_type_variants(cls, type_names, type_dict):
        """Create type variants for types with a cardinality field.
        The new type converters are based on the type converter with
        cardinality=1.

        .. code-block:: python

            # -- USE: parse_number() type converter function.
            new_types = CardinalityFieldTypeBuilder.create_type_variants(
                            ["Number?", "Number+"], dict(Number=parse_number))

        :param type_names: List of type names with cardinality field suffix.
        :param type_dict:  Type dictionary with named type converters.
        :return: Type dictionary with type converter variants.
        """
        type_variant_dict = {}
        for type_name in type_names:
            type_variant = cls.create_type_variant(type_name, type_dict)
            type_variant_dict[type_name] = type_variant
        return type_variant_dict

    # MAYBE: Check if really needed.
    @classmethod
    def create_missing_type_variants(cls, type_names, type_dict):
        """Create missing type variants for types with a cardinality field.

        :param type_names: List of type names with cardinality field suffix.
        :param type_dict:  Type dictionary with named type converters.
        :return: Type dictionary with missing type converter variants.
        """
        missing_type_names = [name for name in type_names
                              if name not in type_dict]
        return cls.create_type_variants(missing_type_names, type_dict)
