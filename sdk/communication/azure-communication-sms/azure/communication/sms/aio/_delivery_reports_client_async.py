# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union, Any, Optional
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from .._generated.aio._azure_communication_sms_service import AzureCommunicationSMSService
from .._generated.models import DeliveryReport
from .._shared.auth_policy_utils import get_authentication_policy
from .._shared.utils import parse_connection_str
from .._version import SDK_MONIKER


class DeliveryReportsClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Delivery Reports gateway asynchronously.

    This client provides operations to retrieve delivery reports for SMS messages.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword str api_version:
        The API version to use for requests. If not specified, the default API version will be used.

    .. admonition:: Example:

        .. literalinclude:: ../samples/delivery_reports_sample_async.py
            :start-after: [START create_delivery_reports_client_async]
            :end-before: [END create_delivery_reports_client_async]
            :language: python
            :dedent: 4
            :caption: Creating a DeliveryReportsClient asynchronously

        .. literalinclude:: ../samples/delivery_reports_sample_async.py
            :start-after: [START get_delivery_status_async]
            :end-before: [END get_delivery_status_async]
            :language: python
            :dedent: 4
            :caption: Retrieving delivery report status asynchronously
    """

    def __init__(
            self,
            endpoint: str,
            credential: Union[AsyncTokenCredential, AzureKeyCredential],
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
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        
        # If api_version is provided, pass it to the service client
        service_kwargs = kwargs.copy()
        if api_version is not None:
            service_kwargs['api_version'] = api_version
            
        self._sms_service_client = AzureCommunicationSMSService(
            self._endpoint, authentication_policy=self._authentication_policy, sdk_moniker=SDK_MONIKER, **service_kwargs
        )

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            *,
            api_version: Optional[str] = None,
            **kwargs: Any
    ) -> "DeliveryReportsClient":
        """Create DeliveryReportsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :keyword str api_version:
            The API version to use for requests. If not specified, the default API version will be used.
        :returns: Instance of DeliveryReportsClient.
        :rtype: ~azure.communication.sms.aio.DeliveryReportsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/get_delivery_report_sample_async.py
                :start-after: [START auth_from_connection_string_async]
                :end-before: [END auth_from_connection_string_async]
                :language: python
                :dedent: 8
                :caption: Creating the DeliveryReportsClient from a connection string asynchronously.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), api_version=api_version, **kwargs)

    @distributed_trace_async
    async def get_status(
            self,
            outgoing_message_id: str,
            **kwargs: Any
    ) -> DeliveryReport:
        """Gets delivery report for a specific outgoing message.

        :param str outgoing_message_id: The identifier of the outgoing message.
        :return: DeliveryReport containing the delivery status information.
        :rtype: ~azure.communication.sms.models.DeliveryReport

        .. admonition:: Example:

            .. literalinclude:: ../samples/delivery_reports_sample_async.py
                :start-after: [START get_delivery_status_async]
                :end-before: [END get_delivery_status_async]
                :language: python
                :dedent: 8
                :caption: Getting delivery status for an SMS message asynchronously.
        """
        response = await self._sms_service_client.delivery_reports.get(
            outgoing_message_id=outgoing_message_id,
            **kwargs
        )

        # Convert the raw JSON response to a DeliveryReport object
        if isinstance(response, dict):
            return DeliveryReport.from_dict(response)
        
        # This shouldn't happen with the current API, but handle it for safety
        return DeliveryReport.from_dict(response)  # type: ignore

    async def __aenter__(self) -> "DeliveryReportsClient":
        await self._sms_service_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._sms_service_client.__aexit__(*args)

    async def close(self) -> None:
        """Close the async client.
        
        This method should be called when the client is no longer needed.
        """
        await self._sms_service_client.close()
