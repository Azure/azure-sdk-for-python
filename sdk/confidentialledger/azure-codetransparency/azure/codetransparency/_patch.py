# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
import re
import tempfile
import random
from typing import Any, Union

from azure.core.credentials import AzureKeyCredential, TokenCredential

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
    :type credential: ~azure.core.credentials.AzureKeyCredential
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
        credential: AzureKeyCredential,
        *,
        ledger_certificate_path: Union[bytes, str, os.PathLike, None] = None,
        **kwargs: Any,
    ) -> None:

        if ledger_certificate_path is None:
            # Create a temporary file path for the ledger certificate based on the endpoint.
            # Use the ledger id from the endpoint to create a deterministic filename
            # so the certificate can be reused across client instances.
            ledger_id = endpoint.replace("https://", "").split(".")[0]
            # Normalize the ledger_id to ensure it's a valid filename on any OS
            # by replacing any non-alphanumeric characters (except hyphen) with underscore
            normalized_ledger_id = re.sub(r"[^a-zA-Z0-9\-]", "_", ledger_id)
            suffix_random = "".join(
                random.Random().choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8)
            )
            ledger_certificate_path = os.path.join(
                tempfile.gettempdir(),
                f"{normalized_ledger_id}_ledger_cert_{suffix_random}.pem",
            )

        if not os.path.isfile(ledger_certificate_path):
            # We'll need to fetch the TLS certificate.
            identity_service_client = ConfidentialLedgerCertificateClient(**kwargs)
            # Ledger URIs are of the form https://<ledger id>.confidential-ledger.azure.com.
            ledger_id = endpoint.replace("https://", "").split(".")[0]

            # Some client specific kwargs will not be supported by the identity request
            # this is to ensure users have full control of the underlying client config
            # Otherwise the client will break because get_ledger_identity request will fail
            # with unsupported options that are meant for the Client
            valid_identity_kwargs = {
                key: value
                for key, value in kwargs.items()
                if key
                in ["error_map", "headers", "params", "cls", "stream", "transport"]
            }
            ledger_cert = identity_service_client.get_ledger_identity(
                ledger_id, **valid_identity_kwargs
            )

            with open(ledger_certificate_path, "w", encoding="utf-8") as outfile:
                outfile.write(ledger_cert["ledgerTlsCertificate"])

        # Customize the underlying client to use a self-signed TLS certificate.

        kwargs["connection_verify"] = kwargs.get(
            "connection_verify", ledger_certificate_path
        )

        # Increase default retry attempts and backoff factor to better handle transient failures
        # see defaults in azure.core.pipeline.policies.RetryPolicyBase
        kwargs["retry_status"] = kwargs.pop(
            "retry_status", 5
        )  # some 503 responses may take a while to recover
        kwargs["retry_backoff_factor"] = kwargs.pop("retry_backoff_factor", 0.9)

        super().__init__(endpoint, credential, **kwargs)
