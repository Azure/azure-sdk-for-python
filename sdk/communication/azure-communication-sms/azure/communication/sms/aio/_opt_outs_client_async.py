# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Union, Optional, List
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from .._generated.aio._client import AzureCommunicationSMSService
from .._generated.models import OptOutRequest, OptOutRecipient, OptOutResponseItem
from .._models import OptOutResult, OptOutCheckResult
from .._shared.auth_policy_utils import get_authentication_policy
from .._shared.utils import parse_connection_str
from .._version import SDK_MONIKER


class OptOutsClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Opt-Outs gateway asynchronously.

    This client provides operations to manage SMS opt-out lists.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword str api_version:
        The API version to use for requests. If not specified, the default API version will be used.

    .. admonition:: Example:

        .. literalinclude:: ../samples/opt_outs_sample_async.py
            :start-after: [START create_opt_outs_client_async]
            :end-before: [END create_opt_outs_client_async]
            :language: python
            :dedent: 4
            :caption: Creating an OptOutsClient asynchronously

        .. literalinclude:: ../samples/opt_outs_sample_async.py
            :start-after: [START manage_opt_out_list_async]
            :end-before: [END manage_opt_out_list_async]
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
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")  # pylint: disable=raise-missing-from

        if not credential:
            raise ValueError("invalid credential from connection string.")

        self._endpoint = endpoint
        self._credential = credential  # Store credential for sub-clients
        self._authentication_policy = get_authentication_policy(endpoint, credential, decode_url=True, is_async=True)
        
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
        :rtype: ~azure.communication.sms.aio.OptOutsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/manage_opt_outs_sample_async.py
                :start-after: [START auth_from_connection_string_async]
                :end-before: [END auth_from_connection_string_async]
                :language: python
                :dedent: 8
                :caption: Creating the OptOutsClient from a connection string asynchronously.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), api_version=api_version, **kwargs)

    @distributed_trace_async
    async def add_opt_out(
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

            .. literalinclude:: ../samples/opt_outs_sample_async.py
                :start-after: [START add_opt_out_async]
                :end-before: [END add_opt_out_async]
                :language: python
                :dedent: 8
                :caption: Adding a phone number to opt-out list asynchronously.
        """
        # Convert single string to list
        if isinstance(to, str):
            to = [to]
        
        # Create OptOutRecipient objects for each recipient
        recipients = [OptOutRecipient(to=phone_number) for phone_number in to]
        
        request = OptOutRequest(from_property=from_, recipients=recipients)
        
        response = await self._sms_service_client.opt_outs.add(
            body=request,
            **kwargs
        )

        # Handle both dictionary responses (from tests) and model objects (from API)
        items = response.get('value', []) if isinstance(response, dict) else response.value

        return [
            OptOutResult(
                to=item.get('to', '') if isinstance(item, dict) else item.to,
                http_status_code=item.get('httpStatusCode', 0) if isinstance(item, dict) else item.http_status_code,
                error_message=item.get('errorMessage') if isinstance(item, dict) else item.error_message
            ) for item in items
        ]

    @distributed_trace_async
    async def remove_opt_out(
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

            .. literalinclude:: ../samples/opt_outs_sample_async.py
                :start-after: [START remove_opt_out_async]
                :end-before: [END remove_opt_out_async]
                :language: python
                :dedent: 8
                :caption: Removing a phone number from opt-out list asynchronously.
        """
        # Convert single string to list
        if isinstance(to, str):
            to = [to]
        
        # Create OptOutRecipient objects for each recipient
        recipients = [OptOutRecipient(to=phone_number) for phone_number in to]
        
        request = OptOutRequest(from_property=from_, recipients=recipients)
        
        response = await self._sms_service_client.opt_outs.remove(
            body=request,
            **kwargs
        )

        # Handle both dictionary responses (from tests) and model objects (from API)
        items = response.get('value', []) if isinstance(response, dict) else response.value

        return [
            OptOutResult(
                to=item.get('to', '') if isinstance(item, dict) else item.to,
                http_status_code=item.get('httpStatusCode', 0) if isinstance(item, dict) else item.http_status_code,
                error_message=item.get('errorMessage') if isinstance(item, dict) else item.error_message
            ) for item in items
        ]

    @distributed_trace_async
    async def check_opt_out(
            self,
            from_: str,
            to: Union[str, List[str]],
            **kwargs: Any
    ) -> List[OptOutCheckResult]:
        """Check the opt-out status for phone numbers.

        :param from_: The sender phone number to check opt-outs for.
        :type from_: str
        :param to: The recipient phone number(s) to check opt-out status for.
        :type to: Union[str, List[str]]
        :return: A list of OptOutCheckResult containing the opt-out status for each recipient.
        :rtype: List[~azure.communication.sms.models.OptOutCheckResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/opt_outs_sample_async.py
                :start-after: [START check_opt_out_async]
                :end-before: [END check_opt_out_async]
                :language: python
                :dedent: 8
                :caption: Checking opt-out status for phone numbers asynchronously.
        """
        # Convert single string to list
        if isinstance(to, str):
            to = [to]
        
        # Create OptOutRecipient objects for each recipient
        recipients = [OptOutRecipient(to=phone_number) for phone_number in to]
        
        request = OptOutRequest(from_property=from_, recipients=recipients)
        
        response = await self._sms_service_client.opt_outs.check(
            body=request,
            **kwargs
        )

        # Handle both dictionary responses (from tests) and model objects (from API)
        items = response.get('value', []) if isinstance(response, dict) else response.value

        return [
            OptOutCheckResult(
                to=item.get('to', '') if isinstance(item, dict) else item.to,
                http_status_code=item.get('httpStatusCode', 0) if isinstance(item, dict) else item.http_status_code,
                is_opted_out=item.get('isOptedOut', False) if isinstance(item, dict) else (item.is_opted_out or False),
                error_message=item.get('errorMessage') if isinstance(item, dict) else item.error_message
            ) for item in items
        ]

    async def __aenter__(self) -> "OptOutsClient":
        await self._sms_service_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._sms_service_client.__aexit__(*args)

    async def close(self) -> None:
        """Close the async client.
        
        This method should be called when the client is no longer needed.
        """
        await self._sms_service_client.close()
