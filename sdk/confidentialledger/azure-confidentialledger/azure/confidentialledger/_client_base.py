# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import BearerTokenCredentialPolicy, HttpLoggingPolicy

from ._generated._generated_ledger.v0_1_preview import (
    ConfidentialLedgerClient as _ConfidentialLedgerClient,
)
from ._shared import ConfidentialLedgerCertificateCredential, DEFAULT_VERSION
from ._user_agent import USER_AGENT

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from typing import Any, Union


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
        except AttributeError:
            raise ValueError("Confidential Ledger URL must be a string.")

        self.api_version = kwargs.pop("api_version", DEFAULT_VERSION)

        if not kwargs.get("transport", None):
            # Customize the transport layer to use client certificate authentication and validate
            # a self-signed TLS certificate.
            if isinstance(credential, ConfidentialLedgerCertificateCredential):
                kwargs["connection_cert"] = credential.certificate_path

            kwargs["connection_verify"] = ledger_certificate_path

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
                    "https://confidential-ledger.azure.com/.default",
                    **kwargs
                ),
            )

        try:
            self._client = _ConfidentialLedgerClient(
                self._endpoint,
                api_version=self.api_version,
                http_logging_policy=http_logging_policy,
                sdk_moniker=USER_AGENT,
                **kwargs
            )
        except NotImplementedError:
            raise NotImplementedError(
                "This package doesn't support API version '{}'. ".format(
                    self.api_version
                )
                + "Supported versions: 0.1-preview"
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
