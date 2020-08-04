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
from .shared_access_signature_credential import EventGridSharedAccessSignatureCredential
from ._signature_credential_policy import EventGridSharedAccessSignatureCredentialPolicy
from ._models import CloudEvent, EventGridEvent
from ._generated._event_grid_publisher_client import EventGridPublisherClient as EventGridPublisherClientImpl
from .shared_access_signature_credential import EventGridSharedAccessSignatureCredential
from . import _constants as constants

class EventGridPublisherClient(object):
    """EventGrid Python Publisher Client.

    :param str topic_hostname: The topic endpoint to send the events to.
    :param credential: The credential object used for authentication which implements SAS key authentication or SAS token authentication.
    :type credential: Union[~azure.core.credentials.AzureKeyCredential, azure.eventgrid.EventGridSharedAccessSignatureCredential]
    """

    def __init__(
        self,
        topic_hostname,  # type: str
        credential,  # type: Union[azure.core.credential.AzureKeyCredential, azure.eventgrid.EventGridSharedAccessSignatureCredential]
        **kwargs  # type: Any
    ):
        # type: (str, Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> None
        self._credential = credential
        self._topic_hostname = topic_hostname
        auth_policy = self._get_authentication_policy()
        self._client = EventGridPublisherClientImpl(authentication_policy=auth_policy, **kwargs)

    def send(
        self,
        events,
        **kwargs
    ):
        # type: (Union[List[CloudEvent], List[EventGridEvent], List[CustomEvent]], Any) -> None
        """Sends event data to topic hostname specified during client initialization.

        :param events: A list of CloudEvent/EventGridEvent/CustomEvent to be sent. If a dict is sent, it will be interpreted as a CloudEvent.
        :type events: Union[List[models.CloudEvent], List[models.EventGridEvent], List[models.CustomEvent]]
        :rtype: None
         """

        if all(isinstance(e, CloudEvent) for e in events):
            print("sending")
            print(events[0])
            print(CloudEvent.serialize(events[0]))
            self._client.publish_cloud_event_events(self._topic_hostname, events)
        elif all(isinstance(e, EventGridEvent) for e in events):
            self._client.publish_events(self._topic_hostname, events)
        else:
          raise Exception("Event schema is not correct. Please send as list of all CloudEvents, list of all EventGridEvents, or list of all CustomEvents.")

    def _get_authentication_policy(self):
        authentication_policy = None
        if self._credential is None:
            raise ValueError("Parameter 'self._credential' must not be None.")
        if isinstance(self._credential, AzureKeyCredential):
            authentication_policy = AzureKeyCredentialPolicy(credential=self._credential, name=constants.EVENTGRID_KEY_HEADER)
        if isinstance(self._credential, EventGridSharedAccessSignatureCredential):
            authentication_policy = EventGridSharedAccessSignatureCredentialPolicy(credential=self._credential, name=constants.EVENTGRID_TOKEN_HEADER)
        return authentication_policy
