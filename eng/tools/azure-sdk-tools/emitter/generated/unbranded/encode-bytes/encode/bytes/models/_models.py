# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from .._utils.model_base import Model as _Model, rest_field


class Base64BytesProperty(_Model):
    """Base64BytesProperty.

    :ivar value: Required.
    :vartype value: bytes
    """

    value: bytes = rest_field(visibility=["read", "create", "update", "delete", "query"], format="base64")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: bytes,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Base64urlArrayBytesProperty(_Model):
    """Base64urlArrayBytesProperty.

    :ivar value: Required.
    :vartype value: list[bytes]
    """

    value: list[bytes] = rest_field(visibility=["read", "create", "update", "delete", "query"], format="base64url")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[bytes],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Base64urlBytesProperty(_Model):
    """Base64urlBytesProperty.

    :ivar value: Required.
    :vartype value: bytes
    """

    value: bytes = rest_field(visibility=["read", "create", "update", "delete", "query"], format="base64url")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: bytes,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class DefaultBytesProperty(_Model):
    """DefaultBytesProperty.

    :ivar value: Required.
    :vartype value: bytes
    """

    value: bytes = rest_field(visibility=["read", "create", "update", "delete", "query"], format="base64")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: bytes,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
