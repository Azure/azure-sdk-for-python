# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, Optional, TYPE_CHECKING, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class InnerModel(_Model):
    """Dictionary inner model.

    :ivar property: Required string property. Required.
    :vartype property: str
    :ivar children:
    :vartype children: dict[str, ~typetest.dictionary.models.InnerModel]
    """

    property: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required string property. Required."""
    children: Optional[dict[str, "_models.InnerModel"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )

    @overload
    def __init__(
        self,
        *,
        property: str,  # pylint: disable=redefined-builtin
        children: Optional[dict[str, "_models.InnerModel"]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
