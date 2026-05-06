# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, Optional, TYPE_CHECKING, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class InnerModel(_Model):
    """It is the model used by Resource model.

    :ivar name:
    :vartype name: str
    :ivar description:
    :vartype description: str
    """

    name: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    description: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Resource(_Model):
    """Details about a resource.

    :ivar name: Required.
    :vartype name: str
    :ivar description:
    :vartype description: str
    :ivar map:
    :vartype map: dict[str, ~payload.jsonmergepatch.models.InnerModel]
    :ivar array:
    :vartype array: list[~payload.jsonmergepatch.models.InnerModel]
    :ivar int_value:
    :vartype int_value: int
    :ivar float_value:
    :vartype float_value: float
    :ivar inner_model:
    :vartype inner_model: ~payload.jsonmergepatch.models.InnerModel
    :ivar int_array:
    :vartype int_array: list[int]
    """

    name: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    description: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    map: Optional[dict[str, "_models.InnerModel"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    array: Optional[list["_models.InnerModel"]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    int_value: Optional[int] = rest_field(name="intValue", visibility=["read", "create", "update", "delete", "query"])
    float_value: Optional[float] = rest_field(
        name="floatValue", visibility=["read", "create", "update", "delete", "query"]
    )
    inner_model: Optional["_models.InnerModel"] = rest_field(
        name="innerModel", visibility=["read", "create", "update", "delete", "query"]
    )
    int_array: Optional[list[int]] = rest_field(
        name="intArray", visibility=["read", "create", "update", "delete", "query"]
    )

    @overload
    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        map: Optional[dict[str, "_models.InnerModel"]] = None,
        array: Optional[list["_models.InnerModel"]] = None,
        int_value: Optional[int] = None,
        float_value: Optional[float] = None,
        inner_model: Optional["_models.InnerModel"] = None,
        int_array: Optional[list[int]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ResourcePatch(_Model):
    """Details about a resource for patch operation.

    :ivar description:
    :vartype description: str
    :ivar map:
    :vartype map: dict[str, ~payload.jsonmergepatch.models.InnerModel]
    :ivar array:
    :vartype array: list[~payload.jsonmergepatch.models.InnerModel]
    :ivar int_value:
    :vartype int_value: int
    :ivar float_value:
    :vartype float_value: float
    :ivar inner_model:
    :vartype inner_model: ~payload.jsonmergepatch.models.InnerModel
    :ivar int_array:
    :vartype int_array: list[int]
    """

    description: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    map: Optional[dict[str, "_models.InnerModel"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    array: Optional[list["_models.InnerModel"]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    int_value: Optional[int] = rest_field(name="intValue", visibility=["read", "create", "update", "delete", "query"])
    float_value: Optional[float] = rest_field(
        name="floatValue", visibility=["read", "create", "update", "delete", "query"]
    )
    inner_model: Optional["_models.InnerModel"] = rest_field(
        name="innerModel", visibility=["read", "create", "update", "delete", "query"]
    )
    int_array: Optional[list[int]] = rest_field(
        name="intArray", visibility=["read", "create", "update", "delete", "query"]
    )

    @overload
    def __init__(
        self,
        *,
        description: Optional[str] = None,
        map: Optional[dict[str, "_models.InnerModel"]] = None,
        array: Optional[list["_models.InnerModel"]] = None,
        int_value: Optional[int] = None,
        float_value: Optional[float] = None,
        inner_model: Optional["_models.InnerModel"] = None,
        int_array: Optional[list[int]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
