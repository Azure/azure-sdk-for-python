#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Sequence

from azure.core import PipelineClient
from msrest import Deserializer, Serializer

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from ._models import CloudEvent, EventGridEvent
from ._generated.event_grid_publisher_client._event_grid_publisher_client import EventGridPublisherClient as EventGridPublisherClientImpl
from . import _constants as constants

class EventGridPublisherClient(object):
    """EventGrid Python Publisher Client.

    :param str topic_hostname: The topic endpoint to send the events to.
    :param credential: The credential object used for authentication which implements SAS key authentication or SAS token authentication.
    :type credential: Union[~azure.core.credentials.AzureKeyCredential, ~azure.core.credentials.TokenCredential]
    """

    def __init__(
        self,
        topic_hostname,  # type: str
        credential,  # type: Union[azure.core.credential.AzureKeyCredential, azure.core.credential.TokenCredential]
        **kwargs  # type: Any
    ):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None
        auth_policy = EventGridPublisherClient._get_authentication_policy(credential)
        self._credential = credential
        self._topic_hostname = topic_hostname
        self._client = EventGridPublisherClientImpl(authentication_policy=auth_policy, **kwargs)

    def send(
        self,
        events,
        **kwargs
    ):
        # type: (Union[List[CloudEvent], List[EventGridEvent], List[CustomEvent], dict], Any) -> None
        """Sends event data to topic hostname specified during client initialization.

        :param  events: A list of CloudEvent/EventGridEvent/CustomEvent to be sent. If a dict is sent, it will be interpreted as a CloudEvent.
        :type events: Union[List[models.CloudEvent], List[models.EventGridEvent], List[models.CustomEvent], dict]
        :rtype: None
         """

        if isinstance(events[0], CloudEvent):
            self._client.publish_cloud_event_events(self._topic_hostname, events)
        elif isinstance(events[0], EventGridEvent):
            self._client.publish_event_grid_events(self._topic_hostname, events)
        else:
            print("Event schema is not correct. Please send as list of CloudEvent or list of EventGridEvent.")
    
    @classmethod
    def _get_authentication_policy(cls, credential):
        authentication_policy = None
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        if isinstance(credential, AzureKeyCredential):
            authentication_policy = AzureKeyCredentialPolicy(credential=credential, name=constants.EVENTGRID_KEY_HEADER)
        return authentication_policy
