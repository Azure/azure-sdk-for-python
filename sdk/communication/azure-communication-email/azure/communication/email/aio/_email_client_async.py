# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from uuid import uuid4
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from typing import Union
from .._shared.utils import parse_connection_str, get_current_utc_time
from .._shared.policy import HMACCredentialsPolicy
from .._generated.aio._azure_communication_email_service import AzureCommunicationEmailService
from .._version import SDK_MONIKER
from .._generated.models import SendEmailResult, SendStatusResult, EmailMessage

class EmailClient(object): # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Email gateway asynchronously.

    This client provides operations to send an email and monitor its status.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    """
    """
    def __init__(
            self,
            endpoint: str,
            credential: Union[AsyncTokenCredential, AzureKeyCredential],
            **kwargs
        ) -> None:
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

        authentication_policy = HMACCredentialsPolicy(endpoint, credential)

        self._generated_client = AzureCommunicationEmailService(
            endpoint,
            authentication_policy=authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs
    ) -> 'EmailClient':
        """Create EmailClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of EmailClient.
        :rtype: ~azure.communication.EmailClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    @distributed_trace_async
    async def send(
        self,
        email_message: EmailMessage,
        **kwargs
    ) -> SendEmailResult:
        """Queues an email message to be sent to one or more recipients.

        :param email_message: The message payload for sending an email.
        :type email_message: ~azure.communication.email.models.EmailMessage
        :return: SendEmailResult
        :rtype: ~azure.communication.email.models.SendEmailResult
        """

        return await self._generated_client.email.send(
            repeatability_request_id=uuid4(),
            repeatability_first_sent=get_current_utc_time(),
            email_message=email_message,
            **kwargs
        )

    @distributed_trace_async
    async def get_send_status(
        self,
        message_id: str,
        **kwargs
    ) -> SendStatusResult:
        """Gets the status of a message sent previously.

        :param message_id: System generated message id (GUID) returned from a previous call to send email
        :type message_id: str
        :return: SendStatusResult
        :rtype: ~azure.communication.email.models.SendStatusResult
        """

        return await self._generated_client.email.get_send_status(
            message_id=message_id,
            **kwargs
        )

    async def __aenter__(self) -> "EmailClient":
        await self._generated_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._generated_client.__aexit__(*args)

    async def close(self) -> None:
        await self._generated_client.close()
