# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Union
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._generated._azure_communication_sms_service import AzureCommunicationSMSService
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str
from ._version import SDK_MONIKER


class OptOutsClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Opt-Outs gateway.

    This client provides operations to manage SMS opt-out lists.

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
    ) -> "OptOutsClient":
        """Create OptOutsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of OptOutsClient.
        :rtype: ~azure.communication.sms.OptOutsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/manage_opt_outs_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the OptOutsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    @distributed_trace
    def add_opt_out(
            self,
            request: Any,
            **kwargs: Any
    ) -> Any:
        """Add phone numbers to the opt-out list which shall stop receiving messages from a sender number.

        :param request: The opt-out request containing sender and recipient phone numbers.
        :type request: ~azure.communication.sms.models.OptOutRequest
        :return: OptOutResponse containing the result of the operation.
        :rtype: ~azure.communication.sms.models.OptOutResponse
        """
        response = self._sms_service_client.opt_outs.add(
            body=request,
            **kwargs
        )

        return response

    @distributed_trace
    def remove_opt_out(
            self,
            request: Any,
            **kwargs: Any
    ) -> Any:
        """Remove phone numbers from the opt-out list.

        :param request: The opt-out request containing sender and recipient phone numbers.
        :type request: ~azure.communication.sms.models.OptOutRequest
        :return: OptOutResponse containing the result of the operation.
        :rtype: ~azure.communication.sms.models.OptOutResponse
        """
        response = self._sms_service_client.opt_outs.remove(
            body=request,
            **kwargs
        )

        return response

    @distributed_trace
    def check_opt_out(
            self,
            request: Any,
            **kwargs: Any
    ) -> Any:
        """Check the opt-out status for a recipient phone number with a sender phone number.

        :param request: The opt-out request containing sender and recipient phone numbers.
        :type request: ~azure.communication.sms.models.OptOutRequest
        :return: OptOutResponse containing the opt-out status.
        :rtype: ~azure.communication.sms.models.OptOutResponse
        """
        response = self._sms_service_client.opt_outs.check(
            body=request,
            **kwargs
        )

        return response
