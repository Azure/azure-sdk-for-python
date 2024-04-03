# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, overload, Mapping, Any
from azure.core.messaging import CloudEvent
from ._models import (
    ReceiveDetails as InternalReceiveDetails,
    ReceiveResult as InternalReceiveResult,
    BrokerProperties as InternalBrokerProperties,
    AcknowledgeOptions as InternalAcknowledgeOptions,
    AcknowledgeResult as InternalAcknowledgeResult,
    FailedLockToken,
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
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(  # pylint: disable=useless-super-delegation
        self, *args: Any, **kwargs: Any
    ) -> None:
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
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__( # pylint: disable=useless-super-delegation
        self, *args: Any, **kwargs: Any
    ) -> None:
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
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__( # pylint: disable=useless-super-delegation
        self, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

class Result(InternalAcknowledgeResult):
    """Details of the operation response.

    All required parameters must be populated in order to send to server.

    :ivar failed_lock_tokens: Array of FailedLockToken for failed cloud events. Each
     FailedLockToken includes the lock token along with the related error information (namely, the
     error code and description). Required.
    :vartype failed_lock_tokens: list[~azure.eventgrid.models.FailedLockToken]
    :ivar succeeded_lock_tokens: Array of lock tokens for the successfully renewed locks. Required.
    :vartype succeeded_lock_tokens: list[str]
    """

    @overload
    def __init__(
        self,
        *,
        failed_lock_tokens: List["FailedLockToken"],
        succeeded_lock_tokens: List[str],
    ): ...

    def __init__( # pylint: disable=useless-super-delegation
        self, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

class Options(InternalAcknowledgeOptions):
    """Array of lock tokens for the corresponding received Cloud Events.

    All required parameters must be populated in order to send to server.

    :ivar lock_tokens: Array of lock tokens. Required.
    :vartype lock_tokens: list[str]
    """

    @overload
    def __init__(
        self,
        *,
        lock_tokens: List[str],
    ): ...

    def __init__( # pylint: disable=useless-super-delegation
        self, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

__all__: List[str] = [
    "ReceiveDetails",
    "ReceiveResult",
    "BrokerProperties",
    "Options",
    "Result",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
