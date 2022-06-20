# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
from typing import Any, List, Union

from azure.core.credentials import TokenCredential
from azure.core.pipeline import policies

from azure.confidentialledger.aio.operations import ConfidentialLedgerOperations as OperationsMixin
from azure.confidentialledger.aio._client import (
    ConfidentialLedgerClient as GeneratedClient,
)
from azure.confidentialledger._patch import ConfidentialLedgerCertificateCredential

__all__: List[str] = [
    "ConfidentialLedgerClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class ConfidentialLedgerClient(GeneratedClient, OperationsMixin):
    """The ConfidentialLedgerClient writes and retrieves ledger entries against the Confidential
    Ledger service.

    :ivar confidential_ledger: ConfidentialLedgerOperations operations
    :vartype confidential_ledger: azure.confidentialledger.operations.ConfidentialLedgerOperations
    :param ledger_uri: The Confidential Ledger URL, for example
     https://contoso.confidentialledger.azure.com.
    :type ledger_uri: str
    :param credential: A credential object for authenticating with the Confidential Ledger.
    :type credential: Union[~azure.confidentialledger.ConfidentialLedgerCertificateCredential, ~azure.core.credentials.TokenCredential]
    :param ledger_certificate_path: The path to the Confidential Ledger's TLS certificate.
    :type ledger_certificate_path: Union[bytes, str, os.PathLike]
    :keyword api_version: Api Version. Default value is "2022-05-13". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        ledger_uri: str,
        credential: Union[ConfidentialLedgerCertificateCredential, TokenCredential],
        *,
        ledger_certificate_path: Union[bytes, str, os.PathLike],
        **kwargs: Any,
    ) -> None:
        # For ConfidentialLedgerCertificateCredential, pass the path to the certificate down to the
        # PipelineCLient.
        if isinstance(credential, ConfidentialLedgerCertificateCredential):
            # The async version of the client seems to expect a sequence of filenames.
            # azure/core/pipeline/transport/_aiohttp.py:163
            # > ssl_ctx.load_cert_chain(*cert)
            kwargs["connection_cert"] = (credential.certificate_path,)

        # The auto-generated client has authentication disabled so we can customize authentication.
        # If the credential is the typical TokenCredential, then construct the authentication policy
        # the normal way.
        else:
            credential_scopes = kwargs.pop(
                "credential_scopes", ["https://confidential-ledger.azure.com/.default"]
            )
            kwargs["authentication_policy"] = kwargs.get(
                "authentication_policy",
                policies.AsyncBearerTokenCredentialPolicy(
                    credential, *credential_scopes, **kwargs
                ),
            )

        # Customize the underlying client to use a self-signed TLS certificate.
        kwargs["connection_verify"] = kwargs.get(
            "connection_verify", ledger_certificate_path
        )

        super().__init__(ledger_uri, **kwargs)
