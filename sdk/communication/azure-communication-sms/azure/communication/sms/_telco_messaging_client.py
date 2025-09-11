# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union, Any
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._sms_client import SmsClient
from ._delivery_reports_client import DeliveryReportsClient
from ._opt_outs_client import OptOutsClient
from ._shared.utils import parse_connection_str


class TelcoMessagingClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A unified client to interact with Azure Communication Services Telco Messaging operations.

    This client provides access to SMS, delivery reports, and opt-out management operations
    through organized sub-clients.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[TokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword Any kwargs: Additional arguments to pass to the sub-clients.

    :ivar sms: SMS operations client
    :vartype sms: ~azure.communication.sms.SmsClient
    :ivar delivery_reports: Delivery reports operations client
    :vartype delivery_reports: ~azure.communication.sms.DeliveryReportsClient
    :ivar opt_outs: Opt-out management operations client
    :vartype opt_outs: ~azure.communication.sms.OptOutsClient
    """

    def __init__(
            self,
            endpoint: str,
            credential: Union[TokenCredential, AzureKeyCredential],
            **kwargs: Any
    ) -> None:
        """Initialize the TelcoMessagingClient.

        :param str endpoint:
            The endpoint url for Azure Communication Service resource.
        :param Union[TokenCredential, AzureKeyCredential] credential:
            The credential we use to authenticate against the service.
        :keyword Any kwargs: Additional arguments to pass to the sub-clients.
        """
        # Initialize sub-clients with the same endpoint and credential
        self.sms = SmsClient(endpoint, credential, **kwargs)
        self.delivery_reports = DeliveryReportsClient(endpoint, credential, **kwargs)
        self.opt_outs = OptOutsClient(endpoint, credential, **kwargs)

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            **kwargs: Any
    ) -> "TelcoMessagingClient":
        """Create TelcoMessagingClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of TelcoMessagingClient.
        :rtype: ~azure.communication.sms.TelcoMessagingClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/telco_messaging_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the TelcoMessagingClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)
