# coding=utf-8
# pylint: disable=useless-super-delegation

import datetime
from typing import Any, Mapping, TYPE_CHECKING, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class BytesProperty(_Model):
    """Template type for testing models with nullable property. Pass in the type of the property you
    are looking for.

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: bytes
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: bytes = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"], format="base64"
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: bytes,
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

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: list[bytes]
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: list[bytes] = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"], format="base64"
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: list[bytes],
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

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: list[~typetest.property.nullable.models.InnerModel]
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: list["_models.InnerModel"] = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: list["_models.InnerModel"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CollectionsStringProperty(_Model):
    """Model with collection string properties.

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: list[str]
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: list[str] = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: list[str],
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

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: ~datetime.datetime
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: datetime.datetime = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"], format="rfc3339"
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: datetime.datetime,
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

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: ~datetime.timedelta
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: datetime.timedelta = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class InnerModel(_Model):
    """Inner model used in collections model property.

    :ivar property: Inner model property. Required.
    :vartype property: str
    """

    property: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Inner model property. Required."""

    @overload
    def __init__(
        self,
        *,
        property: str,  # pylint: disable=redefined-builtin
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
    """Template type for testing models with nullable property. Pass in the type of the property you
    are looking for.

    :ivar required_property: Required property. Required.
    :vartype required_property: str
    :ivar nullable_property: Property. Required.
    :vartype nullable_property: str
    """

    required_property: str = rest_field(
        name="requiredProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required property. Required."""
    nullable_property: str = rest_field(
        name="nullableProperty", visibility=["read", "create", "update", "delete", "query"]
    )
    """Property. Required."""

    @overload
    def __init__(
        self,
        *,
        required_property: str,
        nullable_property: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
