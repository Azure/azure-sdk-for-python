# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
from typing import Any, List, Union

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies

from azure.confidentialledger.aio._client import (
    ConfidentialLedgerClient as GeneratedClient,
)

# Since we can't `await` in __init__, use the sync client for the Identity Service.
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
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


class ConfidentialLedgerClient(GeneratedClient):
    """The ConfidentialLedgerClient writes and retrieves ledger entries against the Confidential
    Ledger service.

    :param endpoint: The Confidential Ledger URL, for example
     https://contoso.confidentialledger.azure.com.
    :type endpoint: str
    :param credential: A credential object for authenticating with the Confidential Ledger.
    :type credential: Union[
        ~azure.confidentialledger.ConfidentialLedgerCertificateCredential,
        ~azure.core.credentials_async.AsyncTokenCredential]
    :keyword ledger_certificate_path: The path to the Confidential Ledger's TLS certificate. If this
        file does not exist yet, the Confidential Ledger's TLS certificate will be fetched and saved
        to this file.
    :paramtype ledger_certificate_path: Union[bytes, str, os.PathLike]
    :keyword api_version: Api Version. Default value is "2022-05-13". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[ConfidentialLedgerCertificateCredential, AsyncTokenCredential],
        *,
        ledger_certificate_path: Union[bytes, str, os.PathLike],
        **kwargs: Any,
    ) -> None:
        if os.path.isfile(ledger_certificate_path) is False:
            # We'll need to fetch the TLS certificate.
            identity_service_client = ConfidentialLedgerCertificateClient(**kwargs)

            # Ledger URIs are of the form https://<ledger id>.confidential-ledger.azure.com.
            ledger_id = endpoint.replace("https://", "").split(".")[0]
            ledger_cert = identity_service_client.get_ledger_identity(ledger_id, **kwargs)

            with open(ledger_certificate_path, "w", encoding="utf-8") as outfile:
                outfile.write(ledger_cert["ledgerTlsCertificate"])

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
            credential_scopes = kwargs.pop("credential_scopes", ["https://confidential-ledger.azure.com/.default"])
            kwargs["authentication_policy"] = kwargs.get(
                "authentication_policy",
                policies.AsyncBearerTokenCredentialPolicy(credential, *credential_scopes, **kwargs),
            )

        # Customize the underlying client to use a self-signed TLS certificate.
        kwargs["connection_verify"] = kwargs.get("connection_verify", ledger_certificate_path)

        super().__init__(endpoint, **kwargs)
