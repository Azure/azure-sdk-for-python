# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, TYPE_CHECKING, Union, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import _types, models as _models


class NewModel(_Model):
    """NewModel.

    :ivar new_prop: Required.
    :vartype new_prop: str
    :ivar enum_prop: Required. "newEnumMember"
    :vartype enum_prop: str or ~versioning.renamedfrom.models.NewEnum
    :ivar union_prop: Required. Is either a str type or a int type.
    :vartype union_prop: str or int
    """

    new_prop: str = rest_field(name="newProp", visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    enum_prop: Union[str, "_models.NewEnum"] = rest_field(
        name="enumProp", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. \"newEnumMember\""""
    union_prop: "_types.NewUnion" = rest_field(
        name="unionProp", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. Is either a str type or a int type."""

    @overload
    def __init__(
        self,
        *,
        new_prop: str,
        enum_prop: Union[str, "_models.NewEnum"],
        union_prop: "_types.NewUnion",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
