#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, cast, Dict, List, Any, Union

from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline.policies import (
    RequestIdPolicy,
    HeadersPolicy,
    RedirectPolicy,
    RetryPolicy,
    ContentDecodePolicy,
    CustomHookPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy
)

from ._models import CloudEvent, EventGridEvent, CustomEvent
from ._helpers import (
    _get_topic_hostname_only_fqdn,
    _get_authentication_policy,
    _is_cloud_event,
    _eventgrid_data_typecheck
)
from ._generated._event_grid_publisher_client import EventGridPublisherClient as EventGridPublisherClientImpl
from ._policies import CloudEventDistributedTracingPolicy
from ._version import VERSION
from ._generated.models import CloudEvent as InternalCloudEvent, EventGridEvent as InternalEventGridEvent

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import AzureKeyCredential
    from ._shared_access_signature_credential import EventGridSharedAccessSignatureCredential
    SendType = Union[
        CloudEvent,
        EventGridEvent,
        CustomEvent,
        Dict,
        List[CloudEvent],
        List[EventGridEvent],
        List[CustomEvent],
        List[Dict]
    ]

ListEventType = Union[
    List[CloudEvent],
    List[EventGridEvent],
    List[CustomEvent],
    List[Dict]
]


class EventGridPublisherClient(object):
    """EventGrid Python Publisher Client.

    :param str topic_hostname: The topic endpoint to send the events to.
    :param credential: The credential object used for authentication which
     implements SAS key authentication or SAS token authentication.
    :type credential: ~azure.core.credentials.AzureKeyCredential or EventGridSharedAccessSignatureCredential
    """

    def __init__(self, topic_hostname, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> None
        topic_hostname = _get_topic_hostname_only_fqdn(topic_hostname)

        self._topic_hostname = topic_hostname
        self._client = EventGridPublisherClientImpl(
            policies=EventGridPublisherClient._policies(credential, **kwargs),
            **kwargs
            )

    @staticmethod
    def _policies(credential, **kwargs):
        # type: (Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> List[Any]
        auth_policy = _get_authentication_policy(credential)
        sdk_moniker = 'eventgrid/{}'.format(VERSION)
        policies = [
            RequestIdPolicy(**kwargs),
            HeadersPolicy(**kwargs),
            UserAgentPolicy(sdk_moniker=sdk_moniker, **kwargs),
            ProxyPolicy(**kwargs),
            ContentDecodePolicy(**kwargs),
            RedirectPolicy(**kwargs),
            RetryPolicy(**kwargs),
            auth_policy,
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            CloudEventDistributedTracingPolicy(),
            HttpLoggingPolicy(**kwargs)
        ]
        return policies

    @distributed_trace
    def send(self, events, **kwargs):
        # type: (SendType, Any) -> None
        """Sends event data to topic hostname specified during client initialization.

        :param events: A list or an instance of CloudEvent/EventGridEvent/CustomEvent to be sent.
        :type events: SendType
        :keyword str content_type: The type of content to be used to send the events.
         Has default value "application/json; charset=utf-8" for EventGridEvents,
         with "cloudevents-batch+json" for CloudEvents
        :rtype: None
        :raises: :class:`ValueError`, when events do not follow specified SendType.
         """
        if not isinstance(events, list):
            events = cast(ListEventType, [events])

        if all(isinstance(e, CloudEvent) for e in events) or all(_is_cloud_event(e) for e in events):
            try:
                events = [cast(CloudEvent, e)._to_generated(**kwargs) for e in events] # pylint: disable=protected-access
            except AttributeError:
                pass # means it's a dictionary
            kwargs.setdefault("content_type", "application/cloudevents-batch+json; charset=utf-8")
            self._client.publish_cloud_event_events(
                self._topic_hostname,
                cast(List[InternalCloudEvent], events),
                **kwargs
                )
        elif all(isinstance(e, EventGridEvent) for e in events) or all(isinstance(e, dict) for e in events):
            kwargs.setdefault("content_type", "application/json; charset=utf-8")
            for event in events:
                _eventgrid_data_typecheck(event)
            self._client.publish_events(self._topic_hostname, cast(List[InternalEventGridEvent], events), **kwargs)
        elif all(isinstance(e, CustomEvent) for e in events):
            serialized_events = [dict(e) for e in events] # type: ignore
            self._client.publish_custom_event_events(self._topic_hostname, cast(List, serialized_events), **kwargs)
        else:
            raise ValueError("Event schema is not correct.")
