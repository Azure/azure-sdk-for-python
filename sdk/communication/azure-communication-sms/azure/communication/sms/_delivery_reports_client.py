# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union, Any
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._generated._azure_communication_sms_service import AzureCommunicationSMSService
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str
from ._version import SDK_MONIKER


class DeliveryReportsClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Delivery Reports gateway.

    This client provides operations to retrieve delivery reports for SMS messages.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[TokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    """

    def __init__(
            self,
            endpoint: str,
            credential: Union[TokenCredential, AzureKeyCredential],
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
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._sms_service_client = AzureCommunicationSMSService(
            self._endpoint, authentication_policy=self._authentication_policy, sdk_moniker=SDK_MONIKER, **kwargs
        )

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            **kwargs: Any
    ) -> "DeliveryReportsClient":
        """Create DeliveryReportsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of DeliveryReportsClient.
        :rtype: ~azure.communication.sms.DeliveryReportsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/get_delivery_report_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the DeliveryReportsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    @distributed_trace
    def get_status(
            self,
            outgoing_message_id: str,
            **kwargs: Any
    ) -> Any:
        """Gets delivery report for a specific outgoing message.

        :param str outgoing_message_id: The identifier of the outgoing message.
        :return: DeliveryReport if the message was found, ErrorResponse if not found or error occurred.
        :rtype: Union[DeliveryReport, ErrorResponse]
        """
        response = self._sms_service_client.delivery_reports.get(
            outgoing_message_id=outgoing_message_id,
            **kwargs
        )

        return response
