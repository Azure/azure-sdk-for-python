# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, overload, Mapping, Any
from azure.core.messaging import CloudEvent
from .. import _model_base
from ._models import (
    ReceiveDetails as InternalReceiveDetails,
    ReceiveResult as InternalReceiveResult,
    BrokerProperties as InternalBrokerProperties,
)

class ReceiveDetails(InternalReceiveDetails):
    """Receive operation details per Cloud Event.

    All required parameters must be populated in order to send to Azure.

    :ivar broker_properties: The Event Broker details. Required.
    :vartype broker_properties: ~azure.eventgrid.models.BrokerProperties
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

    def __init__(
        self, *args: Any, **kwargs: Any
    ) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ReceiveResult(InternalReceiveResult):
    """Details of the Receive operation response.

    All required parameters must be populated in order to send to Azure.

    :ivar value: Array of receive responses, one per cloud event. Required.
    :vartype value: list[~azure.eventgrid.models.ReceiveDetails]
    """

    @overload
    def __init__(
        self,
        *,
        value: List["ReceiveDetails"],
    ):
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(
        self, *args: Any, **kwargs: Any
    ) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BrokerProperties(InternalBrokerProperties):
    """Properties of the Event Broker operation.

    All required parameters must be populated in order to send to Azure.

    :ivar lock_token: The token used to lock the event. Required.
    :vartype lock_token: str
    :ivar delivery_count: The attempt count for deliverying the event. Required.
    :vartype delivery_count: int
    """

    @overload
    def __init__(
        self,
        *,
        lock_token: str,
        delivery_count: int,
    ):
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(
        self, *args: Any, **kwargs: Any
    ) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


__all__: List[str] = [
    "ReceiveDetails",
    "ReceiveResult",
    "BrokerProperties",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
