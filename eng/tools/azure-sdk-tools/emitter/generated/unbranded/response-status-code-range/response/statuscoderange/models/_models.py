# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from .._utils.model_base import Model as _Model, rest_field


class DefaultError(_Model):
    """DefaultError.

    :ivar code: Required.
    :vartype code: str
    """

    code: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        code: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ErrorInRange(_Model):
    """ErrorInRange.

    :ivar code: Required.
    :vartype code: str
    :ivar message: Required.
    :vartype message: str
    """

    code: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    message: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        code: str,
        message: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class NotFoundError(_Model):
    """NotFoundError.

    :ivar code: Required.
    :vartype code: str
    :ivar resource_id: Required.
    :vartype resource_id: str
    """

    code: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    resource_id: str = rest_field(name="resourceId", visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        code: str,
        resource_id: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Standard4XXError(_Model):
    """Standard4XXError.

    :ivar code: Required.
    :vartype code: str
    """

    code: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        code: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
