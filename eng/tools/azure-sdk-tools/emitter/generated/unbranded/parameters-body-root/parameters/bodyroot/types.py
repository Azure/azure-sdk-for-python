# coding=utf-8

from typing_extensions import Required, TypedDict


class BodyRootModel(TypedDict, total=False):
    """BodyRootModel.

    :ivar category:
    :vartype category: str
    :ivar link_type:
    :vartype link_type: str
    :ivar was_successful:
    :vartype was_successful: bool
    """

    category: str
    linkType: str
    wasSuccessful: bool


class NestedParameterBody(TypedDict, total=False):
    """NestedParameterBody.

    :ivar body_root_parameters: Required.
    :vartype body_root_parameters: "BodyRootModel"
    """

    bodyRootParameters: Required["BodyRootModel"]
    """Required."""
