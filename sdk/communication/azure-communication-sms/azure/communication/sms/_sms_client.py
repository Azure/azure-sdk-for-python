# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List, Union, Any, Optional
from uuid import uuid4
from azure.core.tracing.decorator import distributed_trace
from azure.communication.sms._generated.models import (
    SendMessageRequest,
    SmsRecipient,
    SmsSendOptions,
    MessagingConnectOptions,
)
from azure.communication.sms._models import SmsSendResult
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._generated._azure_communication_sms_service import AzureCommunicationSMSService
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str, get_current_utc_time
from ._version import SDK_MONIKER


class SmsClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Sms gateway.

    This client provides operations to send an SMS via a phone number with support for
    advanced delivery options including delivery report timeouts and Messaging Connect
    partner networks.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[TokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword str api_version:
        The API version to use for requests. If not specified, the default API version will be used.

    .. admonition:: Example:

        .. literalinclude:: ../samples/send_sms_with_advanced_options_sample.py
            :start-after: [START send_sms_with_advanced_options]
            :end-before: [END send_sms_with_advanced_options]
            :language: python
            :dedent: 4
            :caption: Sending SMS with advanced delivery and partner options
    """

    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: Union[TokenCredential, AzureKeyCredential]
            *,
            api_version: Optional[str] = None,
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")  # pylint: disable=raise-missing-from

        if not credential:
            raise ValueError("invalid credential from connection string.")

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        
        # If api_version is provided, pass it to the service client
        service_kwargs = kwargs.copy()
        if api_version is not None:
            # The service client configuration will pick up api_version from kwargs
            service_kwargs['api_version'] = api_version
            
        self._sms_service_client = AzureCommunicationSMSService(
            self._endpoint, authentication_policy=self._authentication_policy, sdk_moniker=SDK_MONIKER, **service_kwargs
        )

    @classmethod
    def from_connection_string(
            cls,
            conn_str,  # type: str
            *,
            api_version: Optional[str] = None,
            **kwargs  # type: Any
    ):  # type: (...) -> SmsClient
        """Create SmsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :keyword str api_version:
            The API version to use for requests. If not specified, the default API version will be used.
        :returns: Instance of SmsClient.
        :rtype: ~azure.communication.sms.SmsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/send_sms_to_single_recipient_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the SmsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), api_version=api_version, **kwargs)

    @distributed_trace
    def send(
            self,
            from_: str,
            to: Union[str, List[str]],
            message: str,
            *,
            enable_delivery_report: bool = False,
            tag: Optional[str] = None,
            delivery_report_timeout_in_seconds: Optional[int] = None,
            messaging_connect_api_key: Optional[str] = None,
            messaging_connect_partner_name: Optional[str] = None,
            **kwargs: Any,
    ) -> List[SmsSendResult]:
        """Sends SMSs to phone numbers.

        :param str from_: The sender of the SMS.
        :param to: The single recipient or the list of recipients of the SMS.
        :type to: Union[str, List[str]]
        :param str message: The message in the SMS
        :keyword bool enable_delivery_report: Enable this flag to receive a delivery report for this
         message on the Azure Resource EventGrid.
        :keyword str tag: Use this field to provide metadata that will then be sent back in the corresponding
         Delivery Report.
        :keyword int delivery_report_timeout_in_seconds: Time to wait for a delivery report. After this time a
         delivery report with timeout error code is generated. Must be between 60 and 43200 seconds.
        :keyword str messaging_connect_api_key: API key for Messaging Connect Partner. 
         Must be provided together with messaging_connect_partner_name.
        :keyword str messaging_connect_partner_name: Partner name for Messaging Connect.
         Must be provided together with messaging_connect_api_key.
        :return: A list of SmsSendResult.
        :rtype: [~azure.communication.sms.models.SmsSendResult]
        :raises ValueError: If messaging_connect_api_key is provided without messaging_connect_partner_name or vice versa.
        """
        if isinstance(to, str):
            to = [to]

        # Validate MessagingConnect fields
        if (messaging_connect_api_key is None) != (messaging_connect_partner_name is None):
            raise ValueError(
                "Both messaging_connect_api_key and messaging_connect_partner_name must be provided together, "
                "or both must be None."
            )

        # Create MessagingConnectOptions if both fields are provided
        messaging_connect = None
        if messaging_connect_api_key is not None and messaging_connect_partner_name is not None:
            messaging_connect = MessagingConnectOptions(
                api_key=messaging_connect_api_key,
                partner=messaging_connect_partner_name
            )

        sms_send_options = SmsSendOptions(
            enable_delivery_report=enable_delivery_report, 
            tag=tag,
            delivery_report_timeout_in_seconds=delivery_report_timeout_in_seconds,
            messaging_connect=messaging_connect
        )

        request = SendMessageRequest(
            from_property=from_,
            sms_recipients=[
                SmsRecipient(
                    to=p, repeatability_request_id=str(uuid4()), repeatability_first_sent=get_current_utc_time()
                )
                for p in to
            ],
            message=message,
            sms_send_options=sms_send_options,
            **kwargs
        )

        response = self._sms_service_client.sms.send(
            request,
            **kwargs
        )

        return [
            SmsSendResult(
                to=item.to,
                message_id=item.message_id,
                http_status_code=item.http_status_code,
                successful=item.successful,
                error_message=item.error_message
            ) for item in response.value
        ]
