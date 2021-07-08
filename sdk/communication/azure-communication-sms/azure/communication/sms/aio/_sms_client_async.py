# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from uuid import uuid4
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.communication.sms._generated.models import (
    SendMessageRequest,
    SmsRecipient,
    SmsSendOptions,
)
from azure.communication.sms._models import SmsSendResult

from .._generated.aio._azure_communication_sms_service import AzureCommunicationSMSService
from .._shared.utils import parse_connection_str, get_authentication_policy, get_current_utc_time
from .._version import SDK_MONIKER

class SmsClient(object):
    """A client to interact with the AzureCommunicationService Sms gateway asynchronously.

    This client provides operations to send an SMS via a phone number.

   :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param AsyncTokenCredential credential:
        The AsyncTokenCredential we use to authenticate against the service.
    """
    def __init__(
            self, endpoint,  # type: str
            credential,  # type: AsyncTokenCredential
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
        self._authentication_policy = get_authentication_policy(endpoint, credential, decode_url=True, is_async=True)

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
    async def send(self, from_, # type: str
             to, # type: Union[str, List[str]]
             message, # type: str
             **kwargs # type: Any
             ): # type: (...) -> [SmsSendResult]
        """Sends SMSs to phone numbers.

        :param str from_: The sender of the SMS.
        :param to: The single recipient or the list of recipients of the SMS.
        :type to: Union[str, List[str]]
        :param str message: The message in the SMS
        :keyword bool enable_delivery_report: Enable this flag to receive a delivery report for this
         message on the Azure Resource EventGrid.
        :keyword str tag: Use this field to provide metadata that will then be sent back in the corresponding
         Delivery Report.
        :return: A list of SmsSendResult.
        :rtype: [~azure.communication.sms.models.SmsSendResult]
        """

        if isinstance(to, str):
            to = [to]

        enable_delivery_report = kwargs.pop('enable_delivery_report', False)
        tag = kwargs.pop('tag', None)

        sms_send_options = SmsSendOptions(
            enable_delivery_report=enable_delivery_report,
            tag=tag
        )

        request = SendMessageRequest(
            from_property=from_,
            sms_recipients=[
                SmsRecipient(
                    to=p,
                    repeatability_request_id=str(uuid4()),
                    repeatability_first_sent=get_current_utc_time()
                ) for p in to
            ],
            message=message,
            sms_send_options=sms_send_options,
            **kwargs)

        return await self._sms_service_client.sms.send(
            request,
            cls=lambda pr, r, e: [
                SmsSendResult(
                    to=item.to,
                    message_id=item.message_id,
                    http_status_code=item.http_status_code,
                    successful=item.successful,
                    error_message=item.error_message
                ) for item in r.value
            ],
            **kwargs)

    async def __aenter__(self) -> "SMSClient":
        await self._sms_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self.close()

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.sms.aio.SmsClient` session.
        """
        await self._sms_service_client.__aexit__()
