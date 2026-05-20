# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, TYPE_CHECKING, Union, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import _types, models as _models


class ModelV2(_Model):
    """ModelV2.

    :ivar prop: Required.
    :vartype prop: str
    :ivar enum_prop: Required. "enumMemberV2"
    :vartype enum_prop: str or ~versioning.removed.models.EnumV2
    :ivar union_prop: Required. Is either a str type or a float type.
    :vartype union_prop: str or float
    """

    prop: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    enum_prop: Union[str, "_models.EnumV2"] = rest_field(
        name="enumProp", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. \"enumMemberV2\""""
    union_prop: "_types.UnionV2" = rest_field(
        name="unionProp", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. Is either a str type or a float type."""

    @overload
    def __init__(
        self,
        *,
        prop: str,
        enum_prop: Union[str, "_models.EnumV2"],
        union_prop: "_types.UnionV2",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelV3(_Model):
    """ModelV3.

    :ivar id: Required.
    :vartype id: str
    :ivar enum_prop: Required. Known values are: "enumMemberV1" and "enumMemberV2Preview".
    :vartype enum_prop: str or ~versioning.removed.models.EnumV3
    """

    id: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    enum_prop: Union[str, "_models.EnumV3"] = rest_field(
        name="enumProp", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. Known values are: \"enumMemberV1\" and \"enumMemberV2Preview\"."""

    @overload
    def __init__(
        self,
        *,
        id: str,  # pylint: disable=redefined-builtin
        enum_prop: Union[str, "_models.EnumV3"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
