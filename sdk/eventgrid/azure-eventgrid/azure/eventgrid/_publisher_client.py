#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING

from azure.core import PipelineClient
from msrest import Deserializer, Serializer

import azure.eventgrid._constants 
if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any

from azure.eventgrid._models import CloudEvent, EventGridEvent
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid._generated._configuration import EventGridPublisherClientConfiguration
from azure.eventgrid._generated._event_grid_publisher_client import EventGridPublisherClient as EventGridPublisherClientImpl
from azure.eventgrid import _constants as constants

class EventGridPublisherClient(EventGridPublisherClientImpl):
    """EventGrid Python Publisher Client.

    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.

    :param str topic_hostname: The topic endpoint to send the events to.
    :param ~azure.core.credentials.AzureKeyCredential credential: The credential object used for authentication which
     implements SAS key authentication.
    """

    def __init__(
        self,
        topic_hostname,  # type: str
        credential,  # type: azure.core.credential.AzureKeyCredential
        **kwargs  # type: Any
    ):
        # type: (str, AzureKeyCredential, Any) -> None
        auth_policy = EventGridPublisherClient._get_authentication_policy(credential)
        super(EventGridPublisherClient, self).__init__(
            authentication_policy=auth_policy,
            **kwargs
        )
        self._topic_hostname = topic_hostname

    def publish_events(
        self,
        events,
        **kwargs
    ):
        # type: (Union[List[CloudEvent], List[EventGridEvent]], Any) -> None
        """Sends event data to topic hostname specified during client initialization.

        :param  events: A list of `CloudEvent` or `EventGridEvent` to be sent
        :type events: Union[List[models.CloudEvent], List[models.EventGridEvent]]
        :rtype: None
         """

        if isinstance(events[0], CloudEvent):
            response = self.publish_cloud_event_events(self._topic_hostname, events)
        elif isinstance(events[0], EventGridEvent):
            response = self.publish_event_grid_events(self._topic_hostname, events)
        else:
            print("Event schema is not correct. Please send as list of CloudEvent or list of EventGridEvent.")
        
        return response

    @classmethod
    def _get_authentication_policy(cls, credential):
        authentication_policy = None
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        if isinstance(credential, AzureKeyCredential):
            authentication_policy = AzureKeyCredentialPolicy(credential=credential, name=constants.EVENTGRID_KEY_HEADER)
        return authentication_policy
