# coding=utf-8
# pylint: disable=useless-super-delegation

import datetime
from typing import Any, Literal, Mapping, Optional, TYPE_CHECKING, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class BooleanLiteralProperty(_Model):
    """Model with boolean literal property.

    :ivar property: Property. Default value is True.
    :vartype property: bool
    """

    property: Optional[Literal[True]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property. Default value is True."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[Literal[True]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class BytesProperty(_Model):
    """Template type for testing models with optional property. Pass in the type of the property you
    are looking for.

    :ivar property: Property.
    :vartype property: bytes
    """

    property: Optional[bytes] = rest_field(visibility=["read", "create", "update", "delete", "query"], format="base64")
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[bytes] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CollectionsByteProperty(_Model):
    """Model with collection bytes properties.

    :ivar property: Property.
    :vartype property: list[bytes]
    """

    property: Optional[list[bytes]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="base64"
    )
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[list[bytes]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CollectionsModelProperty(_Model):
    """Model with collection models properties.

    :ivar property: Property.
    :vartype property: list[~typetest.property.optional.models.StringProperty]
    """

    property: Optional[list["_models.StringProperty"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[list["_models.StringProperty"]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class DatetimeProperty(_Model):
    """Model with a datetime property.

    :ivar property: Property.
    :vartype property: ~datetime.datetime
    """

    property: Optional[datetime.datetime] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="rfc3339"
    )
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[datetime.datetime] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class DurationProperty(_Model):
    """Model with a duration property.

    :ivar property: Property.
    :vartype property: ~datetime.timedelta
    """

    property: Optional[datetime.timedelta] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[datetime.timedelta] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatLiteralProperty(_Model):
    """Model with float literal property.

    :ivar property: Property. Default value is 1.25.
    :vartype property: float
    """

    property: Optional[float] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property. Default value is 1.25."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[float] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class IntLiteralProperty(_Model):
    """Model with int literal property.

    :ivar property: Property. Default value is 1.
    :vartype property: int
    """

    property: Optional[Literal[1]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property. Default value is 1."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[Literal[1]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PlainDateProperty(_Model):
    """Model with a plainDate property.

    :ivar property: Property.
    :vartype property: ~datetime.date
    """

    property: Optional[datetime.date] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[datetime.date] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PlainTimeProperty(_Model):
    """Model with a plainTime property.

    :ivar property: Property.
    :vartype property: ~datetime.time
    """

    property: Optional[datetime.time] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[datetime.time] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RequiredAndOptionalProperty(_Model):
    """Model with required and optional properties.

    :ivar optional_property: optional string property.
    :vartype optional_property: str
    :ivar required_property: required int property. Required.
    :vartype required_property: int
    """

    optional_property: Optional[str] = rest_field(
        name="optionalProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """optional string property."""
    required_property: int = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """required int property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: int,
        optional_property: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class StringLiteralProperty(_Model):
    """Model with string literal property.

    :ivar property: Property. Default value is "hello".
    :vartype property: str
    """

    property: Optional[Literal["hello"]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property. Default value is \"hello\"."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[Literal["hello"]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class StringProperty(_Model):
    """Template type for testing models with optional property. Pass in the type of the property you
    are looking for.

    :ivar property: Property.
    :vartype property: str
    """

    property: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class UnionFloatLiteralProperty(_Model):
    """Model with union of float literal property.

    :ivar property: Property. Is one of the following types: float
    :vartype property: float or float
    """

    property: Optional[float] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property. Is one of the following types: float"""

    @overload
    def __init__(
        self,
        *,
        property: Optional[float] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class UnionIntLiteralProperty(_Model):
    """Model with union of int literal property.

    :ivar property: Property. Is either a Literal[1] type or a Literal[2] type.
    :vartype property: int or int
    """

    property: Optional[Literal[1, 2]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Property. Is either a Literal[1] type or a Literal[2] type."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[Literal[1, 2]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class UnionStringLiteralProperty(_Model):
    """Model with union of string literal property.

    :ivar property: Property. Is either a Literal["hello"] type or a Literal["world"] type.
    :vartype property: str or str
    """

    property: Optional[Literal["hello", "world"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """Property. Is either a Literal[\"hello\"] type or a Literal[\"world\"] type."""

    @overload
    def __init__(
        self,
        *,
        property: Optional[Literal["hello", "world"]] = None,  # pylint: disable=redefined-builtin
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
