# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.tracing.decorator import distributed_trace
from azure.communication.sms._generated.models import SendMessageRequest
from azure.communication.sms._generated.models import SendSmsResponse

from ._generated._azure_communication_sms_service import AzureCommunicationSMSService
from ._shared.policy import HMACCredentialsPolicy
from ._shared.utils import parse_connection_str
from ._version import SDK_MONIKER

class SmsClient(object):
    """A client to interact with the AzureCommunicationService Sms gateway.

    This client provides operations to send an SMS via a phone number.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param str credential:
        The credentials with which to authenticate. The value is an account
        shared access key
    """
    def __init__(
            self, endpoint, # type: str
            credential, # type: str
            **kwargs # type: Any
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

    @distributed_trace
    def send(self, from_phone_number, # type: ~azure.communication.sms.PhoneNumber
             to_phone_numbers, # type: list[~azure.communication.sms.PhoneNumber]
             message, # type: str
             **kwargs  #type: Any
        ): # type: (...) -> SendSmsResponse
        """Sends SMSs to phone numbers.

        :param from_phone_number: the sender of the SMS.
        :type from_phone_number: ~azure.communication.sms.PhoneNumber
        :param to_phone_numbers: the list of recipients of the SMS.
        :type to_phone_numbers: list[~azure.communication.sms.PhoneNumber]
        :param str message: The message in the SMS
        :keyword send_sms_options: the options object to configure delivery reporting.
        :type send_sms_options: ~azure.communication.sms.models.SendSmsOptions
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

        return self._sms_service_client.sms.send(request, **kwargs)
