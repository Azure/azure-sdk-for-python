# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from uuid import uuid4
from urllib.parse import urlparse
from typing import Any, List, Mapping, Optional, Union
from typing_extensions import Self

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.transport import AsyncHttpTransport
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
from azure.core.rest import HttpRequest

from ._authentication_async import _configure_credential
from .._common_conversion import _is_cosmos_endpoint, _get_account
from .._constants import DEFAULT_STORAGE_ENDPOINT_SUFFIX
from .._generated.aio import AzureTable
from .._base_client import extract_batch_part_metadata, parse_query, format_query_string, get_api_version
from .._error import (
    RequestTooLargeError,
    TableTransactionError,
    _decode_error,
    _validate_tablename_error,
)
from .._models import LocationMode
from .._policies import CosmosPatchTransformPolicy, StorageHeadersPolicy, StorageHosts
from .._sdk_moniker import SDK_MONIKER
from ._policies_async import AsyncTablesRetryPolicy


class AsyncTablesBaseClient:  # pylint: disable=too-many-instance-attributes
    """Base class for async TableClient

    :ivar str account_name: The name of the Tables account.
    :ivar str scheme: The scheme component in the full URL to the Tables account.
    :ivar str url: The storage endpoint.
    :ivar str api_version: The service API version.
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential, too-many-statements
        self,
        endpoint: str,
        *,
        credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, AsyncTokenCredential]] = None,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
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
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError as exc:
            raise ValueError("Account URL must be a string.") from exc
        parsed_url = urlparse(endpoint.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {endpoint}")

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError("You need to provide either an AzureSasCredential or AzureNamedKeyCredential")
        self._query_str, credential = format_query_string(sas_token, credential)
        self._location_mode = kwargs.get("location_mode", LocationMode.PRIMARY)
        self.scheme = parsed_url.scheme
        self._cosmos_endpoint = _is_cosmos_endpoint(parsed_url)
        account, self.account_name = _get_account(parsed_url)

        secondary_hostname = None
        self.credential = credential
        if self.scheme.lower() != "https" and hasattr(self.credential, "get_token"):
            raise ValueError("Token credential is only supported with HTTPS.")
        if isinstance(self.credential, AzureNamedKeyCredential):
            self.account_name = self.credential.named_key.name
            endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
            secondary_hostname = f"{self.account_name}-secondary.table.{endpoint_suffix}"

        _hosts = kwargs.get("_hosts")
        if not _hosts:
            if len(account) > 1:
                secondary_hostname = parsed_url.netloc.replace(
                    account[0], account[0] + "-secondary"
                ) + parsed_url.path.replace(account[0], account[0] + "-secondary").rstrip("/")
            if kwargs.get("secondary_hostname"):
                secondary_hostname = kwargs["secondary_hostname"]
            primary_hostname = (parsed_url.netloc + parsed_url.path).rstrip("/")
            _hosts = {
                LocationMode.PRIMARY: primary_hostname,
                LocationMode.SECONDARY: secondary_hostname,
            }
        self._hosts = _hosts

        self._policies = self._configure_policies(hosts=self._hosts, **kwargs)
        if self._cosmos_endpoint:
            self._policies.insert(0, CosmosPatchTransformPolicy())

        self._client = AzureTable(self.url, policies=kwargs.pop("policies", self._policies), **kwargs)
        # Incompatible assignment when assigning a str value to a Literal type variable
        self._client._config.version = get_api_version(
            api_version, self._client._config.version
        )  # type: ignore[assignment]

    @property
    def url(self) -> str:
        """The full endpoint URL to this entity, including SAS token if used.

        This could be either the primary endpoint,
        or the secondary endpoint depending on the current :func:`location_mode`.

        :return: The full endpoint URL including SAS token if used.
        :rtype: str
        """
        return self._format_url(self._hosts[self._location_mode])

    @property
    def _primary_endpoint(self):
        """The full primary endpoint URL.

        :return: The full primary endpoint URL.
        :rtype: str
        """
        return self._format_url(self._hosts[LocationMode.PRIMARY])

    @property
    def _primary_hostname(self):
        """The hostname of the primary endpoint.

        :return: The hostname of the primary endpoint.
        :type: str
        """
        return self._hosts[LocationMode.PRIMARY]

    @property
    def _secondary_endpoint(self):
        """The full secondary endpoint URL if configured.

        If not available a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :return: The full secondary endpoint URL.
        :type: str
        :raise ValueError: If the secondary endpoint URL is not configured.
        """
        if not self._hosts[LocationMode.SECONDARY]:
            raise ValueError("No secondary host configured.")
        return self._format_url(self._hosts[LocationMode.SECONDARY])

    @property
    def _secondary_hostname(self):
        """The hostname of the secondary endpoint.

        If not available this will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :return: The hostname of the secondary endpoint.
        :type: str or None
        """
        return self._hosts[LocationMode.SECONDARY]

    @property
    def api_version(self) -> str:
        """The version of the Storage API used for requests.

        :return: The Storage API version.
        :type: str
        """
        return self._client._config.version  # pylint: disable=protected-access

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._client.close()

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.

        :param str hostname: The current location mode hostname.
        :returns: The full URL to the Tables account.
        :rtype: str
        """
        return f"{self.scheme}://{hostname}{self._query_str}"

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

    async def _batch_send(self, table_name: str, *reqs: HttpRequest, **kwargs: Any) -> List[Mapping[str, Any]]:
        # pylint:disable=docstring-should-be-keyword
        """Given a series of request, do a Storage batch call.

        :param table_name: The table name.
        :type table_name: str
        :param reqs: The HTTP request.
        :type reqs: ~azure.core.pipeline.rest.HttpRequest
        :return: A list of batch part metadata in response.
        :rtype: list[Mapping[str, Any]]
        """
        # Pop it here, so requests doesn't feel bad about additional kwarg
        policies = [StorageHeadersPolicy()]

        changeset = HttpRequest("POST", "")
        changeset.set_multipart_mixed(*reqs, policies=policies, boundary=f"changeset_{uuid4()}")
        request = HttpRequest(
            method="POST",
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

        response = await self._client.send_request(request, stream=True, **kwargs)
        await response.read()
        # TODO: Check for proper error model deserialization
        if response.status_code == 413:
            raise _decode_error(
                response, error_message="The transaction request was too large", error_type=RequestTooLargeError
            )
        if response.status_code != 202:
            decoded = _decode_error(response)
            _validate_tablename_error(decoded, table_name)
            raise decoded

        # The parts() method is defined on the back-compat mixin, not the protocol.
        parts_iter = response.parts()  # type: ignore[attr-defined]
        parts = []
        async for p in parts_iter:
            await p.read()
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
