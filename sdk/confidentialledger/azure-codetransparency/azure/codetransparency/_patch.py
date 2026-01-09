# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
from typing import Any, Iterator, List, Union

from azure.core.credentials import TokenCredential
from azure.core.pipeline import policies

from azure.codetransparency._client import CodeTransparencyClient as GeneratedClient
from azure.confidentialledger.certificate import (
    ConfidentialLedgerCertificateClient,
)  # pylint: disable=import-error,no-name-in-module

__all__: list[str] = [
    "CodeTransparencyClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class CodeTransparencyClient(GeneratedClient):
    """The CodeTransparencyClient writes and retrieves ledger entries from transparency service.

    :param endpoint: The Ledger URL, for example
     https://contoso.confidentialledger.azure.com.
    :type endpoint: str
    :param credential: A credential object for authenticating with the Ledger.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword ledger_certificate_path: The path to the Ledger's TLS certificate. If this
        file does not exist yet, the Ledger's TLS certificate will be fetched and saved
        to this file.
    :paramtype ledger_certificate_path: Union[bytes, str, os.PathLike]
    :keyword api_version: Api Version.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: TokenCredential,
        *,
        ledger_certificate_path: Union[bytes, str, os.PathLike],
        **kwargs: Any,
    ) -> None:

        if not os.path.isfile(ledger_certificate_path):
            # We'll need to fetch the TLS certificate.

            identity_service_client = ConfidentialLedgerCertificateClient(**kwargs)

            # Ledger URIs are of the form https://<ledger id>.confidential-ledger.azure.com.

            ledger_id = endpoint.replace("https://", "").split(".")[0]
            ledger_cert = identity_service_client.get_ledger_identity(
                ledger_id, **kwargs
            )

            with open(ledger_certificate_path, "w", encoding="utf-8") as outfile:
                outfile.write(ledger_cert["ledgerTlsCertificate"])

        # Customize the underlying client to use a self-signed TLS certificate.

        kwargs["connection_verify"] = kwargs.get(
            "connection_verify", ledger_certificate_path
        )

        super().__init__(endpoint, credential, **kwargs)

