# coding=utf-8

from typing_extensions import Required, TypedDict


class InnerModel(TypedDict, total=False):
    """It is the model used by Resource model.

    :ivar name:
    :vartype name: str
    :ivar description:
    :vartype description: str
    """

    name: str
    description: str


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
    description: str
    map: dict[str, "InnerModel"]
    array: list["InnerModel"]
    intValue: int
    floatValue: float
    innerModel: "InnerModel"
    intArray: list[int]


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

    description: str
    map: dict[str, "InnerModel"]
    array: list["InnerModel"]
    intValue: int
    floatValue: float
    innerModel: "InnerModel"
    intArray: list[int]
