# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Optional, Union, cast

from azure.ai.ml._restclient.arm_ml_service import models as models2024
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials, KerberosPasswordCredentials


def from_rest_datastore_credentials(
    rest_credentials: "models2024.DatastoreCredentials",
) -> Union[
    AccountKeyConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
]:
    config_class: Any = NoneCredentialConfiguration

    if isinstance(rest_credentials, models2024.AccountKeyDatastoreCredentials):
        # we are no more using key for key base account.
        # https://github.com/Azure/azure-sdk-for-python/pull/35716
        if isinstance(rest_credentials.secrets, models2024.SasDatastoreSecrets):
            config_class = SasTokenConfiguration
        else:
            config_class = AccountKeyConfiguration
    elif isinstance(rest_credentials, models2024.SasDatastoreCredentials):
        config_class = SasTokenConfiguration
    elif isinstance(rest_credentials, models2024.ServicePrincipalDatastoreCredentials):
        config_class = ServicePrincipalConfiguration
    elif isinstance(rest_credentials, models2024.CertificateDatastoreCredentials):
        config_class = CertificateConfiguration

    return cast(
        Union[
            AccountKeyConfiguration,
            SasTokenConfiguration,
            ServicePrincipalConfiguration,
            CertificateConfiguration,
            NoneCredentialConfiguration,
        ],
        config_class._from_datastore_rest_object(rest_credentials),
    )


def _from_rest_datastore_credentials_preview(
    rest_credentials: Any,
) -> Optional[Union[KerberosKeytabCredentials, KerberosPasswordCredentials]]:
    # ``Kerberos*`` credential models are absent from arm_ml_service; the operation client returns them
    # as a raw mapping, so dispatch on the ``credentialsType`` wire discriminator.
    if not rest_credentials:
        return None
    credentials_type = rest_credentials.get("credentialsType")
    if credentials_type == "KerberosKeytab":
        return KerberosKeytabCredentials._from_rest_object(rest_credentials)
    if credentials_type == "KerberosPassword":
        return KerberosPasswordCredentials._from_rest_object(rest_credentials)

    return None
