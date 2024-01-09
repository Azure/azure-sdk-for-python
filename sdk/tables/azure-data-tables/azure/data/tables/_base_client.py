# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from uuid import uuid4
from urllib.parse import parse_qs, quote, urlparse
from typing import Any, List, Optional, Mapping, Union
from typing_extensions import Self

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential, TokenCredential
from azure.core.utils import parse_connection_string
from azure.core.rest import HttpRequest
from azure.core.pipeline.transport import HttpTransport
from azure.core.pipeline.policies import (
    RedirectPolicy,
    ContentDecodePolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
    CustomHookPolicy,
    RequestIdPolicy,
)

from ._generated import AzureTable
from ._common_conversion import _is_cosmos_endpoint, _get_account
from ._shared_access_signature import QueryStringConstants
from ._constants import (
    DEFAULT_COSMOS_ENDPOINT_SUFFIX,
    DEFAULT_STORAGE_ENDPOINT_SUFFIX,
)
from ._error import RequestTooLargeError, TableTransactionError, _decode_error, _validate_tablename_error
from ._models import LocationMode
from ._authentication import _configure_credential
from ._policies import (
    CosmosPatchTransformPolicy,
    StorageHeadersPolicy,
    StorageHosts,
    TablesRetryPolicy,
)
from ._sdk_moniker import SDK_MONIKER

_SUPPORTED_API_VERSIONS = ["2019-02-02", "2019-07-07", "2020-12-06"]
# cspell:disable-next-line
_DEV_CONN_STRING = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1"  # pylint: disable=line-too-long


def get_api_version(api_version: Optional[str], default: str) -> str:
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = "\n".join(_SUPPORTED_API_VERSIONS)
        raise ValueError(f"Unsupported API version '{api_version}'. Please select from:\n{versions}")
    return api_version or default


class TablesBaseClient:  # pylint: disable=too-many-instance-attributes
    """Base class for TableClient

    :ivar str account_name: The name of the Tables account.
    :ivar str scheme: The scheme component in the full URL to the Tables account.
    :ivar str url: The storage endpoint.
    :ivar str api_version: The service API version.
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential, too-many-statements
        self,
        endpoint: str,
        *,
        credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, TokenCredential]] = None,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        :param str endpoint: A URL to an Azure Tables account.
        :keyword credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
            AzureSasCredential (azure-core), or a TokenCredential implementation from azure-identity.
        :paramtype credential:
            ~azure.core.credentials.AzureNamedKeyCredential or
            ~azure.core.credentials.AzureSasCredential or
            ~azure.core.credentials.TokenCredential or None
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

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)

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
            RedirectPolicy(**kwargs),
            StorageHosts(**kwargs),
            TablesRetryPolicy(**kwargs),
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]

    def _batch_send(self, table_name: str, *reqs: HttpRequest, **kwargs) -> List[Mapping[str, Any]]:
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
        response = self._client.send_request(request, stream=True, **kwargs)
        if response.status_code == 413:
            raise _decode_error(
                response, error_message="The transaction request was too large", error_type=RequestTooLargeError
            )
        if response.status_code != 202:
            decoded = _decode_error(response)
            _validate_tablename_error(decoded, table_name)
            raise decoded

        # The parts() method is defined on the back-compat mixin, not the protocol.
        parts = list(response.parts())  # type: ignore[attr-defined]
        error_parts = [p for p in parts if not 200 <= p.status_code < 300]
        if any(error_parts):
            if error_parts[0].status_code == 413:
                raise _decode_error(
                    response, error_message="The transaction request was too large", error_type=RequestTooLargeError
                )
            decoded = _decode_error(response=error_parts[0], error_type=TableTransactionError)
            _validate_tablename_error(decoded, table_name)
            raise decoded
        return [extract_batch_part_metadata(p) for p in parts]

    def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._client.close()


class TransportWrapper(HttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.

    :param transport: The Http Transport instance
    :type transport: ~azure.core.pipeline.transport.HttpTransport
    """

    def __init__(self, transport):
        self._transport = transport

    def send(self, request, **kwargs):
        return self._transport.send(request, **kwargs)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args):  # pylint: disable=arguments-differ
        pass


def parse_connection_str(
    conn_str: str,
    credential: Optional[Union[AzureNamedKeyCredential, AzureSasCredential, TokenCredential]],
    keyword_args: Any,
):
    if conn_str.lower() == "usedevelopmentstorage=true":
        conn_str = _DEV_CONN_STRING
    conn_settings = parse_connection_string(conn_str)
    primary = None
    secondary = None
    # TODO: kwarg "endpoint_type" may not necessary as we can tell the type from endpoint itself
    endpoint_type = keyword_args.pop("endpoint_type", None)
    if not credential:
        try:
            credential = AzureNamedKeyCredential(name=conn_settings["accountname"], key=conn_settings["accountkey"])
        except KeyError as exc:
            sas_token = conn_settings.get("sharedaccesssignature", None)
            if not sas_token:
                raise ValueError("Connection string missing required connection details.") from exc
            credential = AzureSasCredential(sas_token)
    primary = conn_settings.get("tableendpoint")
    secondary = conn_settings.get("tablesecondaryendpoint")
    if not primary:
        if secondary:
            raise ValueError("Connection string specifies only secondary endpoint.")
        try:
            primary = f"{conn_settings['defaultendpointsprotocol']}://{conn_settings['accountname']}.table.{conn_settings['endpointsuffix']}"  # pylint: disable=line-too-long
            secondary = f"{conn_settings['accountname']}-secondary.table.{conn_settings['endpointsuffix']}"
        except KeyError:
            pass

    if not primary:
        if endpoint_type and endpoint_type == "cosmos":
            endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
        else:
            endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
        try:
            primary = f"https://{conn_settings['accountname']}.table.{conn_settings.get('endpointsuffix', endpoint_suffix)}"  # pylint: disable=line-too-long
        except KeyError as exc:
            raise ValueError("Connection string missing required connection details.") from exc

    if "secondary_hostname" not in keyword_args:
        keyword_args["secondary_hostname"] = secondary

    return primary, credential


def extract_batch_part_metadata(response_part):
    metadata = {}
    if "Etag" in response_part.headers:
        metadata["etag"] = response_part.headers["Etag"]
    return metadata


def format_query_string(sas_token, credential):
    query_str = "?"
    if sas_token and isinstance(credential, AzureSasCredential):
        raise ValueError(
            "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        )
    if sas_token and not credential:
        query_str += sas_token
    elif credential:
        return "", credential
    return query_str.rstrip("?&"), None


def parse_query(query_str):
    sas_values = QueryStringConstants.to_list()
    parsed_query = {k: v[0] for k, v in parse_qs(query_str).items()}
    sas_params = [f"{k}={quote(v, safe='')}" for k, v in parsed_query.items() if k in sas_values]
    sas_token = None
    if sas_params:
        sas_token = "&".join(sas_params)

    snapshot = parsed_query.get("snapshot") or parsed_query.get("sharesnapshot")
    return snapshot, sas_token
