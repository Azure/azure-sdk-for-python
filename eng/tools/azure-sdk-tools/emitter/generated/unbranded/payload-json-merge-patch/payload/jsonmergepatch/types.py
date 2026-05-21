# coding=utf-8

from typing import Optional
from typing_extensions import Required, TypedDict


class InnerModel(TypedDict, total=False):
    """It is the model used by Resource model.

    :ivar name:
    :vartype name: str
    :ivar description:
    :vartype description: str
    """

    name: Optional[str]
    description: Optional[str]


class Resource(TypedDict, total=False):
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

    name: Required[str]
    """Required."""
    description: Optional[str]
    map: Optional[dict[str, "InnerModel"]]
    array: Optional[list["InnerModel"]]
    intValue: Optional[int]
    floatValue: Optional[float]
    innerModel: Optional["InnerModel"]
    intArray: Optional[list[int]]


class ResourcePatch(TypedDict, total=False):
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

    description: Optional[str]
    map: Optional[dict[str, "InnerModel"]]
    array: Optional[list["InnerModel"]]
    intValue: Optional[int]
    floatValue: Optional[float]
    innerModel: Optional["InnerModel"]
    intArray: Optional[list[int]]
