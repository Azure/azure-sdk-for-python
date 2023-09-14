# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, List, Mapping, Optional, Union
from uuid import uuid4

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    AsyncRedirectPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    ProxyPolicy,
    RequestIdPolicy,
    CustomHookPolicy,
    NetworkTraceLoggingPolicy,
)
from azure.core.pipeline.transport import (
    AsyncHttpTransport,
    HttpRequest,
)

from ._authentication_async import _configure_credential
from .._generated.aio import AzureTable
from .._base_client import AccountHostsMixin, get_api_version, extract_batch_part_metadata
from .._error import (
    RequestTooLargeError,
    TableTransactionError,
    _decode_error,
    _validate_tablename_error,
)
from .._policies import StorageHosts, StorageHeadersPolicy
from .._sdk_moniker import SDK_MONIKER
from ._policies_async import AsyncTablesRetryPolicy


class AsyncTablesBaseClient(AccountHostsMixin):
    """Base class for TableClient

    :ivar str account_name: The name of the Tables account.
    :ivar str scheme: The scheme component in the full URL to the Tables account.
    :ivar str url: The storage endpoint.
    :ivar str api_version: The service API version.
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self,
        endpoint: str,
        *,
        credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, AsyncTokenCredential]] = None,
        **kwargs,
    ) -> None:
        """Create TablesBaseClient from a Credential.

        :param str endpoint: A URL to an Azure Tables account.
        :keyword credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
            AzureSasCredential (azure-core), or an AsyncTokenCredential implementation from azure-identity.
        :paramtype credential:
            ~azure.core.credentials.AzureNamedKeyCredential or
            ~azure.core.credentials.AzureSasCredential or
            ~azure.core.credentials_async.AsyncTokenCredential or None
        :keyword api_version: Specifies the version of the operation to use for this request. Default value
            is "2019-02-02".
        :paramtype api_version: str or None
        """
        super(AsyncTablesBaseClient, self).__init__(endpoint, credential=credential, **kwargs)  # type: ignore
        self._client = AzureTable(self.url, policies=kwargs.pop("policies", self._policies), **kwargs)
        self._client._config.version = get_api_version(kwargs, self._client._config.version)  # type: ignore # pylint: disable=protected-access

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._client.close()

    def _configure_policies(self, **kwargs):
        credential_policy = _configure_credential(self.credential)
        return [
            RequestIdPolicy(**kwargs),
            StorageHeadersPolicy(**kwargs),
            UserAgentPolicy(sdk_moniker=SDK_MONIKER, **kwargs),
            ProxyPolicy(**kwargs),
            credential_policy,
            ContentDecodePolicy(response_encoding="utf-8"),
            AsyncRedirectPolicy(**kwargs),
            StorageHosts(**kwargs),
            AsyncTablesRetryPolicy(**kwargs),
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]

    async def _batch_send(self, table_name: str, *reqs: HttpRequest, **kwargs) -> List[Mapping[str, Any]]:
        # pylint:disable=docstring-should-be-keyword
        """Given a series of request, do a Storage batch call.

        :param table_name: The table name.
        :type table_name: str
        :param reqs: The HTTP request.
        :type reqs: ~azure.core.pipeline.transport.HttpRequest
        :return: A list of batch part metadata in response.
        :rtype: list[Mapping[str, Any]]
        """
        # Pop it here, so requests doesn't feel bad about additional kwarg
        policies = [StorageHeadersPolicy()]

        changeset = HttpRequest("POST", None)  # type: ignore
        changeset.set_multipart_mixed(*reqs, policies=policies, boundary=f"changeset_{uuid4()}")
        request = self._client._client.post(  # pylint: disable=protected-access
            url=f"{self.scheme}://{self._primary_hostname}/$batch",
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": "3.0",
                "MaxDataServiceVersion": "3.0;NetFx",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        request.set_multipart_mixed(
            changeset,
            policies=policies,
            enforce_https=False,
            boundary=f"batch_{uuid4()}",
        )

        pipeline_response = await self._client._client._pipeline.run(  # pylint: disable=protected-access
            request, **kwargs
        )
        response = pipeline_response.http_response
        # TODO: Check for proper error model deserialization
        if response.status_code == 413:
            raise _decode_error(
                response, error_message="The transaction request was too large", error_type=RequestTooLargeError
            )
        if response.status_code != 202:
            decoded = _decode_error(response)
            _validate_tablename_error(decoded, table_name)
            raise decoded

        parts_iter = response.parts()
        parts = []
        async for p in parts_iter:
            parts.append(p)
        error_parts = [p for p in parts if not 200 <= p.status_code < 300]
        if any(error_parts):
            if error_parts[0].status_code == 413:
                raise _decode_error(
                    response, error_message="The transaction request was too large", error_type=RequestTooLargeError
                )
            decoded = _decode_error(
                response=error_parts[0],
                error_type=TableTransactionError,
            )
            _validate_tablename_error(decoded, table_name)
            raise decoded
        return [extract_batch_part_metadata(p) for p in parts]


class AsyncTransportWrapper(AsyncHttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.

    :param async_transport: The async Http Transport instance.
    :type async_transport: ~azure.core.pipeline.transport.AsyncHttpTransport
    """

    def __init__(self, async_transport):
        self._transport = async_transport

    async def send(self, request, **kwargs):
        return await self._transport.send(request, **kwargs)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):  # pylint: disable=arguments-differ
        pass
