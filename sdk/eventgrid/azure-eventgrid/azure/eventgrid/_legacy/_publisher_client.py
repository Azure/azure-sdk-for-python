#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, cast, Dict, List, Any, Union, Optional

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
    UserAgentPolicy,
)
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    map_error,
)
from azure.core.messaging import CloudEvent

from ._models import EventGridEvent
from ._helpers import (
    _get_authentication_policy,
    _is_cloud_event,
    _is_eventgrid_event_format,
    _eventgrid_data_typecheck,
    _build_request,
    _cloud_event_to_generated,
    _from_cncf_events,
)
from ._generated import (
    EventGridPublisherClient as EventGridPublisherClientImpl,
)
from ._policies import CloudEventDistributedTracingPolicy
from ._constants import DEFAULT_API_VERSION
from ._version import VERSION

if TYPE_CHECKING:
    from azure.core.credentials import (
        AzureKeyCredential,
        AzureSasCredential,
        TokenCredential,
    )

    from cloudevents.http.event import CloudEvent as CNCFCloudEvent

SendType = Union[
    CloudEvent,
    EventGridEvent,
    Dict,
    "CNCFCloudEvent",
    List[CloudEvent],
    List[EventGridEvent],
    List[Dict],
    List["CNCFCloudEvent"],
]

ListEventType = Union[List[CloudEvent], List[EventGridEvent], List[Dict]]


class EventGridPublisherClient(object):
    """EventGridPublisherClient publishes events to an EventGrid topic or domain.
    It can be used to publish either an EventGridEvent, a CloudEvent or a Custom Schema.

    :param str endpoint: The topic endpoint to send the events to.
    :param credential: The credential object used for authentication which
     implements SAS key authentication or SAS token authentication or a TokenCredential.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AzureSasCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Will default to the most recent Api Version. Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    :rtype: None

    .. admonition:: Example:

        .. literalinclude:: ../samples/basic/sync_samples/sample_authentication.py
            :start-after: [START client_auth_with_key_cred]
            :end-before: [END client_auth_with_key_cred]
            :language: python
            :dedent: 0
            :caption: Creating the EventGridPublisherClient with an endpoint and AzureKeyCredential.

        .. literalinclude:: ../samples/basic/sync_samples/sample_authentication.py
            :start-after: [START client_auth_with_sas_cred]
            :end-before: [END client_auth_with_sas_cred]
            :language: python
            :dedent: 0
            :caption: Creating the EventGridPublisherClient with an endpoint and AzureSasCredential.
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union["AzureKeyCredential", "AzureSasCredential", "TokenCredential"],
        *,
        api_version: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        self._endpoint = endpoint
        self._client = EventGridPublisherClientImpl(
            policies=EventGridPublisherClient._policies(credential, **kwargs), **kwargs
        )
        self._api_version = api_version if api_version is not None else DEFAULT_API_VERSION

    @staticmethod
    def _policies(
        credential: Union["AzureKeyCredential", "AzureSasCredential", "TokenCredential"],
        **kwargs: Any
    ) -> List[Any]:
        auth_policy = _get_authentication_policy(credential)
        sdk_moniker = "eventgrid/{}".format(VERSION)
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
            HttpLoggingPolicy(**kwargs),
        ]
        return policies

    @distributed_trace
    def send(self, events: SendType, *, channel_name: Optional[str] = None, **kwargs: Any) -> None: # pylint:disable=docstring-keyword-should-match-keyword-only
        """Sends events to a topic or a domain specified during the client initialization.

        A single instance or a list of dictionaries, CloudEvents or EventGridEvents are accepted.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_publish_eg_events_to_a_topic.py
                :start-after: [START publish_eg_event_to_topic]
                :end-before: [END publish_eg_event_to_topic]
                :language: python
                :dedent: 0
                :caption: Publishing an EventGridEvent.

            .. literalinclude:: ../samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py
                :start-after: [START publish_cloud_event_to_topic]
                :end-before: [END publish_cloud_event_to_topic]
                :language: python
                :dedent: 0
                :caption: Publishing a CloudEvent.

        Dict representation of respective serialized models is accepted as CloudEvent(s) or
        EventGridEvent(s) apart from the strongly typed objects.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_publish_eg_event_using_dict.py
                :start-after: [START publish_eg_event_dict]
                :end-before: [END publish_eg_event_dict]
                :language: python
                :dedent: 4
                :caption: Publishing a list of EventGridEvents using a dict-like representation.

            .. literalinclude:: ../samples/sync_samples/sample_publish_cloud_event_using_dict.py
                :start-after: [START publish_cloud_event_dict]
                :end-before: [END publish_cloud_event_dict]
                :language: python
                :dedent: 0
                :caption: Publishing a CloudEvent using a dict-like representation.

        When publishing a Custom Schema Event(s), dict-like representation is accepted.
        Either a single dictionary or a list of dictionaries can be passed.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_publish_custom_schema_to_a_topic.py
                :start-after: [START publish_custom_schema]
                :end-before: [END publish_custom_schema]
                :language: python
                :dedent: 4
                :caption: Publishing a Custom Schema event.

        **WARNING**: When sending a list of multiple events at one time, iterating over and sending each event
        will not result in optimal performance. For best performance, it is highly recommended to send
        a list of events.

        :param events: A single instance or a list of dictionaries/CloudEvent/EventGridEvent to be sent.
        :type events: ~azure.core.messaging.CloudEvent or ~azure.eventgrid.EventGridEvent or dict or
         List[~azure.core.messaging.CloudEvent] or List[~azure.eventgrid.EventGridEvent] or List[dict]
        :keyword str content_type: The type of content to be used to send the events.
         Has default value "application/json; charset=utf-8" for EventGridEvents,
         with "cloudevents-batch+json" for CloudEvents
        :keyword channel_name: Optional. Used to specify the name of event channel when publishing to partner.
        :paramtype channel_name: str or None
         namespaces with partner topic. For more details, visit
         https://learn.microsoft.com/azure/event-grid/partner-events-overview
        :rtype: None
        """
        if not isinstance(events, list):
            events = cast(ListEventType, [events])
        content_type = kwargs.pop("content_type", "application/json; charset=utf-8")
        if isinstance(events[0], CloudEvent) or _is_cloud_event(events[0]):
            try:
                events = [_cloud_event_to_generated(e, **kwargs) for e in events]
            except AttributeError:
                ## this is either a dictionary or a CNCF cloud event
                events = [_from_cncf_events(e) for e in events]
            content_type = "application/cloudevents-batch+json; charset=utf-8"
        elif isinstance(events[0], EventGridEvent) or _is_eventgrid_event_format(events[0]):
            for event in events:
                _eventgrid_data_typecheck(event)
        response = self._client.send_request(
            _build_request(
                self._endpoint, content_type, events, channel_name=channel_name, api_version=self._api_version
            ),
            **kwargs
        )
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
        }
        if response.status_code != 200:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

    def close(self) -> None:
        """Closes the EventGridPublisherClient session."""
        self._client.close()

    def __enter__(self) -> "EventGridPublisherClient":
        self._client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)
