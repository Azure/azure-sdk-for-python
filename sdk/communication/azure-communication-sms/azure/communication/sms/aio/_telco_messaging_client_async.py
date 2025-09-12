# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._sms_client_async import SmsClient
from ._delivery_reports_client_async import DeliveryReportsClient
from ._opt_outs_client_async import OptOutsClient
from .._shared.utils import parse_connection_str


class TelcoMessagingClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A unified async client to interact with Azure Communication Services Telco Messaging operations.

    This client provides access to SMS, delivery reports, and opt-out management operations
    through organized async sub-clients.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword str api_version:
        The API version to use for requests. If not specified, the default API version will be used.
    :keyword Any kwargs: Additional arguments to pass to the sub-clients.

    :ivar sms: SMS operations client
    :vartype sms: ~azure.communication.sms.aio.SmsClient
    :ivar delivery_reports: Delivery reports operations client
    :vartype delivery_reports: ~azure.communication.sms.aio.DeliveryReportsClient
    :ivar opt_outs: Opt-out management operations client
    :vartype opt_outs: ~azure.communication.sms.aio.OptOutsClient

    .. admonition:: Example:

        .. literalinclude:: ../samples/telco_messaging_comprehensive_sample_async.py
            :start-after: [START create_telco_messaging_client_async]
            :end-before: [END create_telco_messaging_client_async]
            :language: python
            :dedent: 4
            :caption: Creating an async TelcoMessagingClient

        .. literalinclude:: ../samples/telco_messaging_comprehensive_sample_async.py
            :start-after: [START send_sms_with_delivery_reports_async]
            :end-before: [END send_sms_with_delivery_reports_async]
            :language: python
            :dedent: 4
            :caption: Sending SMS and checking delivery reports asynchronously

        .. literalinclude:: ../samples/telco_messaging_comprehensive_sample_async.py
            :start-after: [START manage_opt_outs_async]
            :end-before: [END manage_opt_outs_async]
            :language: python
            :dedent: 4
            :caption: Managing opt-out lists asynchronously
    """

    def __init__(
            self,
            endpoint: str,
            credential: Union[AsyncTokenCredential, AzureKeyCredential],
            *,
            api_version: Optional[str] = None,
            **kwargs: Any
    ) -> None:
        """Initialize the async TelcoMessagingClient.

        :param str endpoint:
            The endpoint url for Azure Communication Service resource.
        :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
            The credential we use to authenticate against the service.
        :keyword str api_version:
            The API version to use for requests. If not specified, the default API version will be used.
        :keyword Any kwargs: Additional arguments to pass to the sub-clients.
        """
        # Initialize async sub-clients with the same endpoint and credential
        self.sms = SmsClient(endpoint, credential, api_version=api_version, **kwargs)
        self.delivery_reports = DeliveryReportsClient(endpoint, credential, api_version=api_version, **kwargs)
        self.opt_outs = OptOutsClient(endpoint, credential, api_version=api_version, **kwargs)

    async def __aenter__(self) -> "TelcoMessagingClient":
        """Enter the async context manager."""
        await self.sms.__aenter__()
        await self.delivery_reports.__aenter__()
        await self.opt_outs.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        """Exit the async context manager."""
        await self.sms.__aexit__(*args)
        await self.delivery_reports.__aexit__(*args)
        await self.opt_outs.__aexit__(*args)

    async def close(self) -> None:
        """Close all sub-clients."""
        await self.sms.close()
        await self.delivery_reports.close()
        await self.opt_outs.close()

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            *,
            api_version: Optional[str] = None,
            **kwargs: Any
    ) -> "TelcoMessagingClient":
        """Create async TelcoMessagingClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :keyword str api_version:
            The API version to use for requests. If not specified, the default API version will be used.
        :returns: Instance of async TelcoMessagingClient.
        :rtype: ~azure.communication.sms.aio.TelcoMessagingClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/telco_messaging_sample_async.py
                :start-after: [START auth_from_connection_string_async]
                :end-before: [END auth_from_connection_string_async]
                :language: python
                :dedent: 8
                :caption: Creating the async TelcoMessagingClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), api_version=api_version, **kwargs)
