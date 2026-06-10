# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, Optional, TYPE_CHECKING, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class BodyRootModel(_Model):
    """BodyRootModel.

    :ivar category:
    :vartype category: str
    :ivar link_type:
    :vartype link_type: str
    :ivar was_successful:
    :vartype was_successful: bool
    """

    category: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    link_type: Optional[str] = rest_field(name="linkType", visibility=["read", "create", "update", "delete", "query"])
    was_successful: Optional[bool] = rest_field(
        name="wasSuccessful", visibility=["read", "create", "update", "delete", "query"]
    )

    @overload
    def __init__(
        self,
        *,
        category: Optional[str] = None,
        link_type: Optional[str] = None,
        was_successful: Optional[bool] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class NestedParameterBody(_Model):
    """NestedParameterBody.

    :ivar body_root_parameters: Required.
    :vartype body_root_parameters: ~parameters.bodyroot.models.BodyRootModel
    """

    body_root_parameters: "_models.BodyRootModel" = rest_field(
        name="bodyRootParameters", visibility=["read", "create", "update", "delete", "query"]
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        body_root_parameters: "_models.BodyRootModel",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
