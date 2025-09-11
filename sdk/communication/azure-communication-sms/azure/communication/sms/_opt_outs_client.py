# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Union, Optional, List
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._generated._azure_communication_sms_service import AzureCommunicationSMSService
from ._generated.models import OptOutRequest, OptOutRecipient, OptOutResponseItem
from ._models import OptOutResult, OptOutCheckResult
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
    :keyword str api_version:
        The API version to use for requests. If not specified, the default API version will be used.

    .. admonition:: Example:

        .. literalinclude:: ../samples/opt_outs_sample.py
            :start-after: [START create_opt_outs_client]
            :end-before: [END create_opt_outs_client]
            :language: python
            :dedent: 4
            :caption: Creating an OptOutsClient

        .. literalinclude:: ../samples/opt_outs_sample.py
            :start-after: [START manage_opt_out_list]
            :end-before: [END manage_opt_out_list]
            :language: python
            :dedent: 4
            :caption: Managing opt-out lists
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
    ) -> "OptOutsClient":
        """Create OptOutsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :keyword str api_version:
            The API version to use for requests. If not specified, the default API version will be used.
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

        return cls(endpoint, AzureKeyCredential(access_key), api_version=api_version, **kwargs)

    @distributed_trace
    def add_opt_out(
            self,
            from_: str,
            to: Union[str, List[str]],
            **kwargs: Any
    ) -> List[OptOutResult]:
        """Add phone numbers to the opt-out list which shall stop receiving messages from a sender number.

        :param str from_: The sender phone number.
        :param to: The recipient phone number(s) to add to the opt-out list.
        :type to: Union[str, List[str]]
        :return: A list of OptOutResult containing the result of the operation for each recipient.
        :rtype: List[~azure.communication.sms.models.OptOutResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/opt_outs_sample.py
                :start-after: [START add_opt_out]
                :end-before: [END add_opt_out]
                :language: python
                :dedent: 8
                :caption: Adding a phone number to opt-out list.
        """
        # Convert single string to list
        if isinstance(to, str):
            to = [to]
        
        # Create OptOutRecipient objects for each recipient
        recipients = [OptOutRecipient(to=phone_number) for phone_number in to]
        
        request = OptOutRequest(from_property=from_, recipients=recipients)
        
        response = self._sms_service_client.opt_outs.add(
            body=request.serialize(),
            **kwargs
        )

        return [
            OptOutResult(
                to=item["to"],
                http_status_code=item["httpStatusCode"],
                error_message=item.get("errorMessage")
            ) for item in response["value"]
        ]

    @distributed_trace
    def remove_opt_out(
            self,
            from_: str,
            to: Union[str, List[str]],
            **kwargs: Any
    ) -> List[OptOutResult]:
        """Remove phone numbers from the opt-out list.

        :param from_: The sender phone number to remove opt-outs for.
        :type from_: str
        :param to: The recipient phone number(s) to remove from opt-out list.
        :type to: Union[str, List[str]]
        :return: A list of OptOutResult containing the result of the operation for each recipient.
        :rtype: List[~azure.communication.sms.models.OptOutResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/opt_outs_sample.py
                :start-after: [START remove_opt_out]
                :end-before: [END remove_opt_out]
                :language: python
                :dedent: 8
                :caption: Removing a phone number from opt-out list.
        """
        # Convert single string to list
        if isinstance(to, str):
            to = [to]
        
        # Create OptOutRecipient objects for each recipient
        recipients = [OptOutRecipient(to=phone_number) for phone_number in to]
        
        request = OptOutRequest(from_property=from_, recipients=recipients)
        
        response = self._sms_service_client.opt_outs.remove(
            body=request.serialize(),
            **kwargs
        )

        return [
            OptOutResult(
                to=item["to"],
                http_status_code=item["httpStatusCode"],
                error_message=item.get("errorMessage")
            ) for item in response["value"]
        ]

    @distributed_trace
    def check_opt_out(
            self,
            from_: str,
            to: Union[str, List[str]],
            **kwargs: Any
    ) -> List[OptOutCheckResult]:
        """Check the opt-out status for a recipient phone number with a sender phone number.

        :param from_: The sender phone number to check opt-outs for.
        :type from_: str
        :param to: The recipient phone number(s) to check opt-out status for.
        :type to: Union[str, List[str]]
        :return: A list of OptOutCheckResult containing the opt-out status for each recipient.
        :rtype: List[~azure.communication.sms.models.OptOutCheckResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/opt_outs_sample.py
                :start-after: [START check_opt_out]
                :end-before: [END check_opt_out]
                :language: python
                :dedent: 8
                :caption: Checking opt-out status for a phone number.
        """
        # Convert single string to list
        if isinstance(to, str):
            to = [to]
        
        # Create OptOutRecipient objects for each recipient
        recipients = [OptOutRecipient(to=phone_number) for phone_number in to]
        
        request = OptOutRequest(from_property=from_, recipients=recipients)
        
        response = self._sms_service_client.opt_outs.check(
            body=request.serialize(),
            **kwargs
        )

        return [
            OptOutCheckResult(
                to=item["to"],
                http_status_code=item["httpStatusCode"],
                is_opted_out=item.get("isOptedOut", False),
                error_message=item.get("errorMessage")
            ) for item in response["value"]
        ]
