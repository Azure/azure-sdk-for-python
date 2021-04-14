# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

from azure.core.pipeline.policies import BearerTokenCredentialPolicy, HttpLoggingPolicy
from azure.core.pipeline.transport import RequestsTransport

from .._generated_ledger import ConfidentialLedgerClient as _ConfidentialLedgerClient
from .credential import ConfidentialLedgerCertificateCredential

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from typing import Any, Union


class ApiVersion(str, Enum):
    """Confidential Ledger API versions supported by this package."""

    #: this is the default version
    V0_1 = "0.1-preview"


DEFAULT_VERSION = ApiVersion.V0_1


class ConfidentialLedgerClientBase(object):
    def __init__(self, endpoint, credential, ledger_certificate_path, **kwargs):
        # type: (str, Union[ConfidentialLedgerCertificateCredential, TokenCredential], str, Any) -> None

        client = kwargs.get("generated_client")
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return

        if not endpoint:
            raise ValueError("Expected endpoint to be a non-empty string")

        if not credential:
            raise ValueError("Expected credential to not be None")

        if not isinstance(ledger_certificate_path, str):
            raise TypeError("ledger_certificate_path must be a string")

        if ledger_certificate_path == "":
            raise ValueError(
                "If not None, ledger_certificate_path must be a non-empty string"
            )

        try:
            endpoint = endpoint.strip(" /")
            if not endpoint.startswith("https://"):
                self._endpoint = "https://" + endpoint
            else:
                self._endpoint = endpoint
        except AttributeError as e:
            raise ValueError("Confidential Ledger URL must be a string.") from e

        self.api_version = kwargs.pop("api_version", DEFAULT_VERSION)

        pipeline = kwargs.pop("pipeline", None)
        transport = kwargs.pop("transport", None)
        if transport is None:
            # Customize the transport layer to use client certificate authentication and validate
            # a self-signed TLS certificate.
            if isinstance(credential, ConfidentialLedgerCertificateCredential):
                kwargs["connection_cert"] = credential.certificate_path

            kwargs["connection_verify"] = ledger_certificate_path
            transport = RequestsTransport(**kwargs)

        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {
                "x-ms-keyvault-network-info",
                "x-ms-keyvault-region",
                "x-ms-keyvault-service-version",
            }
        )

        if not isinstance(credential, ConfidentialLedgerCertificateCredential):
            kwargs["authentication_policy"] = kwargs.pop(
                "authentication_policy",
                BearerTokenCredentialPolicy(
                    credential,
                    "https://confidential-ledger-ppe.azure.com/.default",
                    **kwargs
                ),
            )

        try:
            self._client = _ConfidentialLedgerClient(
                api_version=self.api_version,
                pipeline=pipeline,
                transport=transport,
                http_logging_policy=http_logging_policy,
                **kwargs
            )
            self._models = _ConfidentialLedgerClient.models(
                api_version=self.api_version
            )
        except NotImplementedError:
            raise NotImplementedError(
                "This package doesn't support API version '{}'. ".format(
                    self.api_version
                )
                + "Supported versions: {}".format(
                    ", ".join(v.value for v in ApiVersion)
                )
            )

    @property
    def endpoint(self):
        # type: () -> str
        """The URL this client is connected to."""
        return self._endpoint

    def __enter__(self):
        # type: () -> ConfidentialLedgerClientBase
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        # type: (Any) -> None
        self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.

        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
