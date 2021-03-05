# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING

import logging
from uuid import uuid4, UUID
from datetime import datetime
import six

try:
    from urllib.parse import parse_qs, quote
except ImportError:
    from urlparse import parse_qs  # type: ignore
    from urllib2 import quote  # type: ignore

from azure.core.configuration import Configuration
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import (
    HttpTransport,
    HttpRequest,
)
from azure.core.pipeline.policies import (
    RedirectPolicy,
    ContentDecodePolicy,
    BearerTokenCredentialPolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    AzureSasCredentialPolicy
)

from ._common_conversion import _to_utc_datetime
from ._shared_access_signature import QueryStringConstants
from ._constants import (
    STORAGE_OAUTH_SCOPE,
    SERVICE_HOST_BASE,
    CONNECTION_TIMEOUT,
    READ_TIMEOUT,
)
from ._models import LocationMode, BatchTransactionResult
from ._authentication import SharedKeyCredentialPolicy
from ._policies import (
    StorageHeadersPolicy,
    StorageContentValidation,
    StorageRequestHook,
    StorageResponseHook,
    StorageLoggingPolicy,
    StorageHosts,
    TablesRetryPolicy,
)
from ._models import BatchErrorException
from ._sdk_moniker import SDK_MONIKER

if TYPE_CHECKING:
    from typing import (  # pylint: disable=ungrouped-imports
        Union,
        Optional,
        Any,
        Iterable,
        Dict,
        List,
        Type,
        Tuple,
    )

_LOGGER = logging.getLogger(__name__)
_SERVICE_PARAMS = {
    "blob": {"primary": "BlobEndpoint", "secondary": "BlobSecondaryEndpoint"},
    "queue": {"primary": "QueueEndpoint", "secondary": "QueueSecondaryEndpoint"},
    "file": {"primary": "FileEndpoint", "secondary": "FileSecondaryEndpoint"},
    "dfs": {"primary": "BlobEndpoint", "secondary": "BlobEndpoint"},
    "table": {"primary": "TableEndpoint", "secondary": "TableSecondaryEndpoint"},
}


class StorageAccountHostsMixin(object):
    def __init__(
        self,
        parsed_url,  # type: Any
        service,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self._location_mode = kwargs.get("_location_mode", LocationMode.PRIMARY)
        self._hosts = kwargs.get("_hosts")
        self.scheme = parsed_url.scheme

        if service not in ["blob", "queue", "file-share", "dfs", "table"]:
            raise ValueError("Invalid service: {}".format(service))
        service_name = service.split("-")[0]
        account = parsed_url.netloc.split(".{}.core.".format(service_name))
        if "cosmos" in parsed_url.netloc:
            account = parsed_url.netloc.split(".{}.cosmos.".format(service_name))
        self.account_name = account[0] if len(account) > 1 else None
        secondary_hostname = None

        self.credential = format_shared_key_credential(account, credential)
        if self.scheme.lower() != "https" and hasattr(self.credential, "get_token"):
            raise ValueError("Token credential is only supported with HTTPS.")
        if hasattr(self.credential, "account_name"):
            self.account_name = self.credential.account_name
            secondary_hostname = "{}-secondary.{}.{}".format(
                self.credential.account_name, service_name, SERVICE_HOST_BASE
            )

        if not self._hosts:
            if len(account) > 1:
                secondary_hostname = parsed_url.netloc.replace(
                    account[0], account[0] + "-secondary"
                )
            if kwargs.get("secondary_hostname"):
                secondary_hostname = kwargs["secondary_hostname"]
            primary_hostname = (parsed_url.netloc + parsed_url.path).rstrip("/")
            self._hosts = {
                LocationMode.PRIMARY: primary_hostname,
                LocationMode.SECONDARY: secondary_hostname,
            }

        self.require_encryption = kwargs.get("require_encryption", False)
        self.key_encryption_key = kwargs.get("key_encryption_key")
        self.key_resolver_function = kwargs.get("key_resolver_function")

        self._configure_credential(self.credential)
        kwargs.setdefault("connection_timeout", CONNECTION_TIMEOUT)
        kwargs.setdefault("read_timeout", READ_TIMEOUT)

        self._policies = [
            StorageHeadersPolicy(**kwargs),
            ProxyPolicy(**kwargs),
            UserAgentPolicy(sdk_moniker=SDK_MONIKER, **kwargs),
            StorageContentValidation(),
            StorageRequestHook(**kwargs),
            self._credential_policy,
            ContentDecodePolicy(response_encoding="utf-8"),
            RedirectPolicy(**kwargs),
            StorageHosts(hosts=self._hosts, **kwargs),
            kwargs.get("retry_policy") or TablesRetryPolicy(**kwargs),
            StorageLoggingPolicy(**kwargs),
            StorageResponseHook(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self):
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._client.close()

    @property
    def url(self):
        """The full endpoint URL to this entity, including SAS token if used.

        This could be either the primary endpoint,
        or the secondary endpoint depending on the current :func:`location_mode`.
        """
        return self._format_url(self._hosts[self._location_mode])

    @property
    def _primary_endpoint(self):
        """The full primary endpoint URL.

        :type: str
        """
        return self._format_url(self._hosts[LocationMode.PRIMARY])

    @property
    def _primary_hostname(self):
        """The hostname of the primary endpoint.

        :type: str
        """
        return self._hosts[LocationMode.PRIMARY]

    @property
    def _secondary_endpoint(self):
        """The full secondary endpoint URL if configured.

        If not available a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :type: str
        :raise ValueError:
        """
        if not self._hosts[LocationMode.SECONDARY]:
            raise ValueError("No secondary host configured.")
        return self._format_url(self._hosts[LocationMode.SECONDARY])

    @property
    def _secondary_hostname(self):
        """The hostname of the secondary endpoint.

        If not available this will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.

        :type: str or None
        """
        return self._hosts[LocationMode.SECONDARY]

    @property
    def location_mode(self):
        """The location mode that the client is currently using.

        By default this will be "primary". Options include "primary" and "secondary".

        :type: str
        """

        return self._location_mode

    @location_mode.setter
    def location_mode(self, value):
        if self._hosts.get(value):
            self._location_mode = value
            self._client._config.url = self.url  # pylint: disable=protected-access
        else:
            raise ValueError("No host URL for location mode: {}".format(value))

    @property
    def api_version(self):
        """The version of the Storage API used for requests.

        :type: str
        """
        return self._client._config.version  # pylint: disable=protected-access

    def _format_query_string(
        self, sas_token, credential, snapshot=None, share_snapshot=None
    ):
        query_str = "?"
        if snapshot:
            query_str += "snapshot={}&".format(self.snapshot)
        if share_snapshot:
            query_str += "sharesnapshot={}&".format(self.snapshot)
        if sas_token and isinstance(credential, AzureSasCredential):
            raise ValueError(
                "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature.")
        if sas_token and not credential:
            query_str += sas_token
        elif is_credential_sastoken(credential):
            query_str += credential.lstrip("?")
            credential = None
        return query_str.rstrip("?&"), credential

    def _configure_credential(self, credential):
        # type: (Any, **Any) -> Tuple[Configuration, Pipeline]
        self._credential_policy = None
        if hasattr(credential, "get_token"):
            self._credential_policy = BearerTokenCredentialPolicy(
                credential, STORAGE_OAUTH_SCOPE
            )
        elif isinstance(credential, SharedKeyCredentialPolicy):
            self._credential_policy = credential
        elif isinstance(credential, AzureSasCredential):
            self._credential_policy = AzureSasCredentialPolicy(credential)
        elif credential is not None:
            raise TypeError("Unsupported credential: {}".format(credential))

    def _batch_send(
        self,
        entities,  # type: List[TableEntity]
        *reqs,  # type: List[HttpRequest]
        **kwargs
    ):
        # (...) -> List[HttpResponse]
        """Given a series of request, do a Storage batch call."""
        # Pop it here, so requests doesn't feel bad about additional kwarg
        raise_on_any_failure = kwargs.pop("raise_on_any_failure", True)
        policies = [StorageHeadersPolicy()]

        changeset = HttpRequest("POST", None)
        changeset.set_multipart_mixed(
            *reqs, policies=policies, boundary="changeset_{}".format(uuid4())
        )
        request = self._client._client.post(  # pylint: disable=protected-access
            url="https://{}/$batch".format(self._primary_hostname),
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": "3.0",
                "MaxDataServiceVersion": "3.0;NetFx",
            },
        )
        request.set_multipart_mixed(
            changeset,
            policies=policies,
            enforce_https=False,
            boundary="batch_{}".format(uuid4()),
        )

        pipeline_response = self._client._client._pipeline.run(request, **kwargs)  # pylint: disable=protected-access
        response = pipeline_response.http_response

        if response.status_code == 403:
            raise ClientAuthenticationError(
                message="There was an error authenticating with the service",
                response=response,
            )
        if response.status_code == 404:
            raise ResourceNotFoundError(
                message="The resource could not be found", response=response
            )
        if response.status_code != 202:
            raise BatchErrorException(
                message="There is a failure in the batch operation.",
                response=response,
                parts=None,
            )

        parts = response.parts()
        transaction_result = BatchTransactionResult(reqs, parts, entities)
        if raise_on_any_failure:
            if any(p for p in parts if not 200 <= p.status_code < 300):

                if any(p for p in parts if p.status_code == 404):
                    raise ResourceNotFoundError(
                        message="The resource could not be found", response=response
                    )

                raise BatchErrorException(
                    message="There is a failure in the batch operation.",
                    response=response,
                    parts=parts,
                )
        return transaction_result

    def _parameter_filter_substitution(  # pylint: disable=no-self-use
            self,
            parameters,  # type: dict[str,str]
            filter  # type: str  pylint: disable=redefined-builtin
    ):
        """Replace user defined parameter in filter
        :param parameters: User defined parameters
        :param filter: Filter for querying
        """
        if parameters:
            filter_strings = filter.split(' ')
            for index, word in enumerate(filter_strings):
                if word[0] == u'@':
                    val = parameters[word[1:]]
                    if val in [True, False]:
                        filter_strings[index] = str(val).lower()
                    elif isinstance(val, (float, six.integer_types)):
                        filter_strings[index] = str(val)
                    elif isinstance(val, datetime):
                        filter_strings[index] = "datetime'{}'".format(_to_utc_datetime(val))
                    elif isinstance(val, UUID):
                        filter_strings[index] = "guid'{}'".format(str(val))
                    else:
                        filter_strings[index] = "'{}'".format(val)
            return ' '.join(filter_strings)

        return filter


class TransportWrapper(HttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
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

    def __exit__(self, *args):
        pass


def format_shared_key_credential(account, credential):
    if isinstance(credential, six.string_types):
        if len(account) < 2:
            raise ValueError(
                "Unable to determine account name for shared key credential."
            )
        credential = {"account_name": account[0], "account_key": credential}
    if isinstance(credential, dict):
        if "account_name" not in credential:
            raise ValueError("Shared key credential missing 'account_name")
        if "account_key" not in credential:
            raise ValueError("Shared key credential missing 'account_key")
        return SharedKeyCredentialPolicy(**credential)
    return credential


def parse_connection_str(conn_str, credential, service, keyword_args):
    conn_str = conn_str.rstrip(";")
    conn_settings = [s.split("=", 1) for s in conn_str.split(";")]
    if any(len(tup) != 2 for tup in conn_settings):
        raise ValueError("Connection string is either blank or malformed.")
    conn_settings = dict(conn_settings)
    endpoints = _SERVICE_PARAMS[service]
    primary = None
    secondary = None
    if not credential:
        try:
            credential = {
                "account_name": conn_settings["AccountName"],
                "account_key": conn_settings["AccountKey"],
            }
        except KeyError:
            credential = conn_settings.get("SharedAccessSignature")
    if endpoints["primary"] in conn_settings:
        primary = conn_settings[endpoints["primary"]]
        if endpoints["secondary"] in conn_settings:
            secondary = conn_settings[endpoints["secondary"]]
    else:
        if endpoints["secondary"] in conn_settings:
            raise ValueError("Connection string specifies only secondary endpoint.")
        try:
            primary = "{}://{}.{}.{}".format(
                conn_settings["DefaultEndpointsProtocol"],
                conn_settings["AccountName"],
                service,
                conn_settings["EndpointSuffix"],
            )
            secondary = "{}-secondary.{}.{}".format(
                conn_settings["AccountName"], service, conn_settings["EndpointSuffix"]
            )
        except KeyError:
            pass

    if not primary:
        try:
            primary = "https://{}.{}.{}".format(
                conn_settings["AccountName"],
                service,
                conn_settings.get("EndpointSuffix", SERVICE_HOST_BASE),
            )
        except KeyError:
            raise ValueError("Connection string missing required connection details.")

    if "secondary_hostname" not in keyword_args:
        keyword_args["secondary_hostname"] = secondary

    return primary, credential


def parse_query(query_str):
    sas_values = QueryStringConstants.to_list()
    parsed_query = {k: v[0] for k, v in parse_qs(query_str).items()}
    sas_params = [
        "{}={}".format(k, quote(v, safe=""))
        for k, v in parsed_query.items()
        if k in sas_values
    ]
    sas_token = None
    if sas_params:
        sas_token = "&".join(sas_params)

    snapshot = parsed_query.get("snapshot") or parsed_query.get("sharesnapshot")
    return snapshot, sas_token


def is_credential_sastoken(credential):
    if not credential or not isinstance(credential, six.string_types):
        return False

    sas_values = QueryStringConstants.to_list()
    parsed_query = parse_qs(credential.lstrip("?"))
    if parsed_query and all([k in sas_values for k in parsed_query.keys()]):
        return True
    return False
