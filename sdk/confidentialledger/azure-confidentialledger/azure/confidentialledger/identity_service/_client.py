# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import HttpLoggingPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.core.tracing.decorator import distributed_trace

from ._models import LedgerIdentity

from .._generated._generated_identity.v0_1_preview import (
    ConfidentialLedgerIdentityServiceClient as _ConfidentialLedgerIdentityServiceClient,
)
from .._shared import DEFAULT_VERSION
from .._user_agent import USER_AGENT

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any


class ConfidentialLedgerIdentityServiceClient(object): # pylint: disable=client-accepts-api-version-keyword
    """Client for communicating with the Confidential Ledger Identity Service,
    which is used for retrieving identity information about a particular Confidential
    Ledger instance.

    :param identity_service_url: Base URL for the Identity Service.
    :type identity_service_url: str
    :param credential: Credential for connecting to the service. May be None, because no credential
        is currently required.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(self, identity_service_url, **kwargs):  # pylint: disable=missing-client-constructor-parameter-credential
        # type: (str, Any) -> None
        client = kwargs.get("generated_client")
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return

        try:
            identity_service_url = identity_service_url.strip(" /")
            if not identity_service_url.lower().startswith("https://"):
                self._identity_service_url = "https://" + identity_service_url
            else:
                self._identity_service_url = identity_service_url
        except AttributeError:
            raise ValueError("Identity Service URL must be a string.")

        self.api_version = kwargs.pop("api_version", DEFAULT_VERSION)

        pipeline = kwargs.pop("pipeline", None)
        transport = kwargs.pop("transport", RequestsTransport(**kwargs))
        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {
                "x-ms-keyvault-network-info",
                "x-ms-keyvault-region",
                "x-ms-keyvault-service-version",
            }
        )

        authentication_policy = None

        self._client = _ConfidentialLedgerIdentityServiceClient(
            self._identity_service_url,
            api_version=self.api_version,
            pipeline=pipeline,
            transport=transport,
            authentication_policy=authentication_policy,
            http_logging_policy=http_logging_policy,
            sdk_moniker=USER_AGENT,
            **kwargs
        )

    @property
    def identity_service_url(self):
        # type: () -> str
        """The URL this client is connected to."""
        return self._identity_service_url

    @distributed_trace
    def get_ledger_identity(self, ledger_id, **kwargs):
        # type: (str, Any) -> LedgerIdentity
        """Gets the network information for a Confidential Ledger instance.

        :param ledger_id: Id for the Confidential Ledger instance to get information for.
        :type ledger_id: str
        :return: The ledger identity.
        :rtype: ~azure.confidentialledger.LedgerIdentity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if not ledger_id:
            raise ValueError("ledger_id must be a non-empty string")

        result = self._client.confidential_ledger_identity_service.get_ledger_identity(
            ledger_id=ledger_id,
            **kwargs
        )
        return LedgerIdentity(
            ledger_id=result.ledger_id,
            ledger_tls_certificate=result.ledger_tls_certificate,
        )
