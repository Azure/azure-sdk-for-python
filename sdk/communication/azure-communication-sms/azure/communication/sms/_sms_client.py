# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List, Union, Any, Optional, TYPE_CHECKING
from uuid import uuid4
from azure.core.tracing.decorator import distributed_trace
from azure.communication.sms._generated.models import (
    SendMessageRequest,
    SmsRecipient,
    SmsSendOptions,
    MessagingConnectOptions,
    DeliveryReport,
)
from azure.communication.sms._models import SmsSendResult
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._generated._client import AzureCommunicationSMSService
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str, get_current_utc_time
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    from ._opt_outs_client import OptOutsClient


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
            endpoint: str,
            credential: Union[TokenCredential, AzureKeyCredential],
            *,
            api_version: Optional[str] = None,
            **kwargs: Any
    ) -> None:
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")  # pylint: disable=raise-missing-from

        if not credential:
            raise ValueError("invalid credential from connection string.")

        self._endpoint = endpoint
        self._credential = credential  # Store credential for sub-clients
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        
        # If api_version is provided, pass it to the service client
        service_kwargs = kwargs.copy()
        if api_version is not None:
            # The service client configuration will pick up api_version from kwargs
            service_kwargs['api_version'] = api_version
            
        self._sms_service_client = AzureCommunicationSMSService(
            self._endpoint, authentication_policy=self._authentication_policy, sdk_moniker=SDK_MONIKER, **service_kwargs
        )

    def get_opt_outs_client(self, **kwargs: Any) -> "OptOutsClient":
        """Get a client to interact with SMS opt-out management.

        :return: An OptOutsClient to manage SMS opt-out lists.
        :rtype: ~azure.communication.sms.OptOutsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/opt_outs_sample.py
                :start-after: [START get_opt_outs_client]
                :end-before: [END get_opt_outs_client]
                :language: python
                :dedent: 8
                :caption: Getting the opt-outs client to manage SMS opt-outs.
        """
        # Import here to avoid circular import
        from ._opt_outs_client import OptOutsClient
        
        return OptOutsClient(
            endpoint=self._endpoint,
            credential=self._credential,  # Re-use the same credential
            **kwargs
        )

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            *,
            api_version: Optional[str] = None,
            **kwargs: Any
    ) -> "SmsClient":
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
            messaging_connect_partner_name: Optional[str] = None,
            messaging_connect_partner_params: Optional[dict] = None,
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
        :keyword str messaging_connect_partner_name: Partner name for Messaging Connect.
         Must be provided together with messaging_connect_partner_params.
        :keyword dict messaging_connect_partner_params: Partner-specific parameters for Messaging Connect.
         This is a dictionary of key-value pairs that will be passed to the partner.
         For example: {"apiKey": "myapikey"} or {"customparam": 5, "anothercustomparam": True}.
         Must be provided together with messaging_connect_partner_name.
        :return: A list of SmsSendResult.
        :rtype: [~azure.communication.sms.models.SmsSendResult]
        :raises ValueError: If messaging_connect_partner_params is provided without messaging_connect_partner_name or vice versa.
        """
        if isinstance(to, str):
            to = [to]

        # Validate MessagingConnect fields
        if (messaging_connect_partner_params is None) != (messaging_connect_partner_name is None):
            raise ValueError(
                "Both messaging_connect_partner_name and messaging_connect_partner_params must be provided together, "
                "or both must be None."
            )

        # Create MessagingConnectOptions if both fields are provided
        messaging_connect = None
        if messaging_connect_partner_name is not None and messaging_connect_partner_params is not None:
            messaging_connect = MessagingConnectOptions(
                partner=messaging_connect_partner_name,
                partner_params=messaging_connect_partner_params
            )

        # Create SmsSendOptions with only non-None values
        sms_send_options_kwargs = {}
        if enable_delivery_report is not None:
            sms_send_options_kwargs["enable_delivery_report"] = enable_delivery_report
        if tag is not None:
            sms_send_options_kwargs["tag"] = tag
        if delivery_report_timeout_in_seconds is not None:
            sms_send_options_kwargs["delivery_report_timeout_in_seconds"] = delivery_report_timeout_in_seconds
        if messaging_connect is not None:
            sms_send_options_kwargs["messaging_connect"] = messaging_connect
            
        sms_send_options = SmsSendOptions(**sms_send_options_kwargs)

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

    @distributed_trace
    def get_delivery_report(
            self,
            outgoing_message_id: str,
            **kwargs: Any
    ) -> DeliveryReport:
        """Gets delivery report for a specific outgoing message.

        :param str outgoing_message_id: The identifier of the outgoing message.
        :return: DeliveryReport containing the delivery status information.
        :rtype: ~azure.communication.sms.models.DeliveryReport

        .. admonition:: Example:

            .. literalinclude:: ../samples/delivery_reports_sample.py
                :start-after: [START get_delivery_status]
                :end-before: [END get_delivery_status]
                :language: python
                :dedent: 8
                :caption: Getting delivery status for an SMS message.
        """
        response = self._sms_service_client.delivery_reports.get(
            outgoing_message_id=outgoing_message_id,
            **kwargs
        )

        # Handle both dictionary responses (from tests) and model objects (from API)
        if isinstance(response, dict):
            from azure.communication.sms._generated.models import DeliveryReport
            # Map dictionary keys to model parameter names
            mapped_response = {
                'delivery_status': response.get('deliveryStatus'),
                'delivery_status_details': response.get('deliveryStatusDetails'),
                'message_id': response.get('messageId'),
                'from_property': response.get('from'),
                'to': response.get('to'),
                'received_timestamp': response.get('receivedTimestamp'),
                'tag': response.get('tag'),
                'delivery_attempts': response.get('deliveryAttempts'),
                'messaging_connect_partner_message_id': response.get('messagingConnectPartnerMessageId')
            }
            # Remove None values to avoid constructor issues
            mapped_response = {k: v for k, v in mapped_response.items() if v is not None}
            return DeliveryReport(**mapped_response)
        
        # The response should already be a DeliveryReport object
        return response
