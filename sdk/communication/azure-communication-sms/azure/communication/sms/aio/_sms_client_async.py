# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.communication.sms._generated.models import SendMessageRequest
from azure.communication.sms._generated.models import SendSmsResponse

from .._generated.aio._azure_communication_sms_service import AzureCommunicationSMSService
from .._shared.policy import HMACCredentialsPolicy
from .._shared.utils import parse_connection_str
from .._version import SDK_MONIKER

class SmsClient(object):
    """A client to interact with the AzureCommunicationService Sms gateway asynchronously.

    This client provides operations to send an SMS via a phone number.

   :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param str credential:
        The credentials with which to authenticate. The value is an account
        shared access key
    """
    def __init__(
            self, endpoint,  # type: str
            credential,  # type: str
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "invalid credential from connection string.")

        self._endpoint = endpoint
        self._authentication_policy = HMACCredentialsPolicy(endpoint, credential)

        self._sms_service_client = AzureCommunicationSMSService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> SmsClient
        """Create SmsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of SmsClient.
        :rtype: ~azure.communication.SmsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sms_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the SmsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace_async()
    async def send(self, from_phone_number,  # type: str
             to_phone_numbers, # type: list[str]
             message,  # type: str
             **kwargs  # type: Any
             ):  # type: (...) -> SendSmsResponse
        """Sends SMSs to phone numbers.

        :param str from_phone_number: the sender of the SMS.
        :param list[str] to_phone_numbers: the list of recipients of the SMS.
        :param str message: The message in the SMS
        :keyword send_sms_options: the options object to configure delivery reporting.
        :type send_sms_options: ~azure.communication.sms.models.SendSmsOptions
        :keyword repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, the client can make the request multiple times with the same
         Repeatability-Request-ID and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-ID is an opaque string
         representing a client-generated, 36-character hexadecimal case-insensitive encoding of a UUID
         (GUID), identifier for the request.
        :type repeatability_request_id: str
        :keyword repeatability_first_sent: MUST be sent by clients to specify that a request is
         repeatable. Repeatability-First-Sent is used to specify the date and time at which the request
         was first created.eg- Tue, 26 Mar 2019 16:06:51 GMT.
        :type repeatability_first_sent: str
        :keyword repeatability_result: MUST be returned to clients for a request that is repeatable. This
         response header in the result of a repeatable request with one of the case-insensitive values
         accepted or rejected.
        :type repeatability_result: str
        :return: The response object with the message_id
        :rtype: SendMessageResponse: ~azure.communication.sms.models.SendMessageResponse
        """

        send_sms_options = kwargs.pop('send_sms_options', None)

        request = SendMessageRequest(
            from_property=from_phone_number,
            to=to_phone_numbers,
            message=message,
            send_sms_options=send_sms_options,
            **kwargs)

        return await self._sms_service_client.sms.send(request, **kwargs)

    async def __aenter__(self) -> "SMSClient":
        await self._sms_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self.close()

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.administration.aio.SMSClient` session.
        """
        await self._sms_service_client.__aexit__()
