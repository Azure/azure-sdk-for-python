# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Mapping, Any, overload
from ._models import ReceiveResponse as ReceiveResponseInternal, ReceiveDetails as ReceiveDetailsInternal, BrokerProperties
from azure.core.messaging import CloudEvent


class ReceiveDetails(ReceiveDetailsInternal):
    """Receive operation details per Cloud Event.

    All required parameters must be populated in order to send to Azure.

    :ivar broker_properties: The Event Broker details. Required.
    :vartype broker_properties: ~azuremessagingeventgrid.models.BrokerProperties
    :ivar event: Cloud Event details. Required.
    :vartype event: ~azure.core.messaging.CloudEvent
    """

    @overload
    def __init__(
        self,
        *,
        broker_properties: "BrokerProperties",
        event: "CloudEvent",
    ):
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


# class ReceiveResponse(ReceiveResponseInternal):
#     """Details of the Receive operation response.

#     All required parameters must be populated in order to send to Azure.

#     :ivar value: Array of receive responses, one per cloud event. Required.
#     :vartype value: list[~azuremessagingeventgrid.models.ReceiveDetails]
#     """

#     @overload
#     def __init__(
#         self,
#         *,
#         value: List["ReceiveDetails"],
#     ):
#         ...

#     @overload
#     def __init__(self, mapping: Mapping[str, Any]):
#         """
#         :param mapping: raw JSON to initialize the model.
#         :type mapping: Mapping[str, Any]
#         """

#     def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
#         super().__init__(*args, **kwargs)



__all__: List[str] = ["ReceiveDetails"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
