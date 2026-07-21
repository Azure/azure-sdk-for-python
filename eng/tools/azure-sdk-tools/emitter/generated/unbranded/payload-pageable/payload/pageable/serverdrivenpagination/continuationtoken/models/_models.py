# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, Optional, TYPE_CHECKING, overload

from ...._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .... import models as _models3


class RequestHeaderNestedResponseBodyResponseNestedItems(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """RequestHeaderNestedResponseBodyResponseNestedItems.

    :ivar pets: Required.
    :vartype pets: list[~payload.pageable.models.Pet]
    """

    pets: list["_models3.Pet"] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        pets: list["_models3.Pet"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RequestHeaderNestedResponseBodyResponseNestedNext(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """RequestHeaderNestedResponseBodyResponseNestedNext.

    :ivar next_token:
    :vartype next_token: str
    """

    next_token: Optional[str] = rest_field(name="nextToken", visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        next_token: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RequestQueryNestedResponseBodyResponseNestedItems(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """RequestQueryNestedResponseBodyResponseNestedItems.

    :ivar pets: Required.
    :vartype pets: list[~payload.pageable.models.Pet]
    """

    pets: list["_models3.Pet"] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        pets: list["_models3.Pet"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RequestQueryNestedResponseBodyResponseNestedNext(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """RequestQueryNestedResponseBodyResponseNestedNext.

    :ivar next_token:
    :vartype next_token: str
    """

    next_token: Optional[str] = rest_field(name="nextToken", visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        next_token: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
