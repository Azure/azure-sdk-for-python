# coding=utf-8

import datetime
import decimal
from typing import Any, Literal, TYPE_CHECKING, Union
from typing_extensions import Required, TypedDict

from .models._enums import ExtendedEnum

if TYPE_CHECKING:
    from .models import FixedInnerEnum, InnerEnum


class BooleanLiteralProperty(TypedDict, total=False):
    """Model with a boolean literal property.

    :ivar property: Property. Required. Default value is True.
    :vartype property: bool
    """

    property: Required[Literal[True]]
    """Property. Required. Default value is True."""


class BooleanProperty(TypedDict, total=False):
    """Model with a boolean property.

    :ivar property: Property. Required.
    :vartype property: bool
    """

    property: Required[bool]
    """Property. Required."""


class BytesProperty(TypedDict, total=False):
    """Model with a bytes property.

    :ivar property: Property. Required.
    :vartype property: bytes
    """

    property: Required[bytes]
    """Property. Required."""


class CollectionsIntProperty(TypedDict, total=False):
    """Model with collection int properties.

    :ivar property: Property. Required.
    :vartype property: list[int]
    """

    property: Required[list[int]]
    """Property. Required."""


class CollectionsModelProperty(TypedDict, total=False):
    """Model with collection model properties.

    :ivar property: Property. Required.
    :vartype property: list[~typetest.property.valuetypes.models.InnerModel]
    """

    property: Required[list["InnerModel"]]
    """Property. Required."""


class CollectionsStringProperty(TypedDict, total=False):
    """Model with collection string properties.

    :ivar property: Property. Required.
    :vartype property: list[str]
    """

    property: Required[list[str]]
    """Property. Required."""


class DatetimeProperty(TypedDict, total=False):
    """Model with a datetime property.

    :ivar property: Property. Required.
    :vartype property: ~datetime.datetime
    """

    property: Required[datetime.datetime]
    """Property. Required."""


class Decimal128Property(TypedDict, total=False):
    """Model with a decimal128 property.

    :ivar property: Property. Required.
    :vartype property: ~decimal.Decimal
    """

    property: Required[decimal.Decimal]
    """Property. Required."""


class DecimalProperty(TypedDict, total=False):
    """Model with a decimal property.

    :ivar property: Property. Required.
    :vartype property: ~decimal.Decimal
    """

    property: Required[decimal.Decimal]
    """Property. Required."""


class DictionaryStringProperty(TypedDict, total=False):
    """Model with dictionary string properties.

    :ivar property: Property. Required.
    :vartype property: dict[str, str]
    """

    property: Required[dict[str, str]]
    """Property. Required."""


class DurationProperty(TypedDict, total=False):
    """Model with a duration property.

    :ivar property: Property. Required.
    :vartype property: ~datetime.timedelta
    """

    property: Required[datetime.timedelta]
    """Property. Required."""


class EnumProperty(TypedDict, total=False):
    """Model with enum properties.

    :ivar property: Property. Required. Known values are: "ValueOne" and "ValueTwo".
    :vartype property: str or ~typetest.property.valuetypes.models.FixedInnerEnum
    """

    property: Required[Union[str, "FixedInnerEnum"]]
    """Property. Required. Known values are: \"ValueOne\" and \"ValueTwo\"."""


class ExtensibleEnumProperty(TypedDict, total=False):
    """Model with extensible enum properties.

    :ivar property: Property. Required. Known values are: "ValueOne" and "ValueTwo".
    :vartype property: str or ~typetest.property.valuetypes.models.InnerEnum
    """

    property: Required[Union[str, "InnerEnum"]]
    """Property. Required. Known values are: \"ValueOne\" and \"ValueTwo\"."""


class FloatLiteralProperty(TypedDict, total=False):
    """Model with a float literal property.

    :ivar property: Property. Required. Default value is 43.125.
    :vartype property: float
    """

    property: Required[float]
    """Property. Required. Default value is 43.125."""


class FloatProperty(TypedDict, total=False):
    """Model with a float property.

    :ivar property: Property. Required.
    :vartype property: float
    """

    property: Required[float]
    """Property. Required."""


class InnerModel(TypedDict, total=False):
    """Inner model. Will be a property type for ModelWithModelProperties.

    :ivar property: Required string property. Required.
    :vartype property: str
    """

    property: Required[str]
    """Required string property. Required."""


class IntLiteralProperty(TypedDict, total=False):
    """Model with a int literal property.

    :ivar property: Property. Required. Default value is 42.
    :vartype property: int
    """

    property: Required[Literal[42]]
    """Property. Required. Default value is 42."""


class IntProperty(TypedDict, total=False):
    """Model with a int property.

    :ivar property: Property. Required.
    :vartype property: int
    """

    property: Required[int]
    """Property. Required."""


class ModelProperty(TypedDict, total=False):
    """Model with model properties.

    :ivar property: Property. Required.
    :vartype property: ~typetest.property.valuetypes.models.InnerModel
    """

    property: Required["InnerModel"]
    """Property. Required."""


class NeverProperty(TypedDict, total=False):
    """Model with a property never. (This property should not be included)."""


class StringLiteralProperty(TypedDict, total=False):
    """Model with a string literal property.

    :ivar property: Property. Required. Default value is "hello".
    :vartype property: str
    """

    property: Required[Literal["hello"]]
    """Property. Required. Default value is \"hello\"."""


class StringProperty(TypedDict, total=False):
    """Model with a string property.

    :ivar property: Property. Required.
    :vartype property: str
    """

    property: Required[str]
    """Property. Required."""


class UnionEnumValueProperty(TypedDict, total=False):
    """Template type for testing models with specific properties. Pass in the type of the property you
    are looking for.

    :ivar property: Property. Required. ENUM_VALUE2.
    :vartype property: str or ~typetest.property.valuetypes.models.ENUM_VALUE2
    """

    property: Required[Literal[ExtendedEnum.ENUM_VALUE2]]
    """Property. Required. ENUM_VALUE2."""


class UnionFloatLiteralProperty(TypedDict, total=False):
    """Model with a union of float literal as property.

    :ivar property: Property. Required. Is one of the following types: float
    :vartype property: float or float
    """

    property: Required[float]
    """Property. Required. Is one of the following types: float"""


class UnionIntLiteralProperty(TypedDict, total=False):
    """Model with a union of int literal as property.

    :ivar property: Property. Required. Is either a Literal[42] type or a Literal[43] type.
    :vartype property: int or int
    """

    property: Required[Literal[42, 43]]
    """Property. Required. Is either a Literal[42] type or a Literal[43] type."""


class UnionStringLiteralProperty(TypedDict, total=False):
    """Model with a union of string literal as property.

    :ivar property: Property. Required. Is either a Literal["hello"] type or a Literal["world"]
     type.
    :vartype property: str or str
    """

    property: Required[Literal["hello", "world"]]
    """Property. Required. Is either a Literal[\"hello\"] type or a Literal[\"world\"] type."""


class UnknownArrayProperty(TypedDict, total=False):
    """Model with a property unknown, and the data is an array.

    :ivar property: Property. Required.
    :vartype property: any
    """

    property: Required[Any]
    """Property. Required."""


class UnknownDictProperty(TypedDict, total=False):
    """Model with a property unknown, and the data is a dictionnary.

    :ivar property: Property. Required.
    :vartype property: any
    """

    property: Required[Any]
    """Property. Required."""


class UnknownIntProperty(TypedDict, total=False):
    """Model with a property unknown, and the data is a int32.

    :ivar property: Property. Required.
    :vartype property: any
    """

    property: Required[Any]
    """Property. Required."""


class UnknownStringProperty(TypedDict, total=False):
    """Model with a property unknown, and the data is a string.

    :ivar property: Property. Required.
    :vartype property: any
    """

    property: Required[Any]
    """Property. Required."""
