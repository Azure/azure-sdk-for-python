# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Optional, Union, cast

from azure.ai.ml._restclient.v2023_04_01_preview import models
from azure.ai.ml._restclient.v2024_07_01_preview import models as models2024
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials, KerberosPasswordCredentials


def from_rest_datastore_credentials(
    rest_credentials: models.DatastoreCredentials,
) -> Union[
    AccountKeyConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
]:
    config_class: Any = NoneCredentialConfiguration

    if isinstance(rest_credentials, (models.AccountKeyDatastoreCredentials, models2024.AccountKeyDatastoreCredentials)):
        config_class = AccountKeyConfiguration
    elif isinstance(rest_credentials, (models.SasDatastoreCredentials, models2024.SasDatastoreCredentials)):
        config_class = SasTokenConfiguration
    elif isinstance(
        rest_credentials, (models.ServicePrincipalDatastoreCredentials, models2024.ServicePrincipalDatastoreCredentials)
    ):
        config_class = ServicePrincipalConfiguration
    elif isinstance(
        rest_credentials, (models.CertificateDatastoreCredentials, models2024.CertificateDatastoreCredentials)
    ):
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
    rest_credentials: models.DatastoreCredentials,
) -> Optional[Union[KerberosKeytabCredentials, KerberosPasswordCredentials]]:
    if isinstance(rest_credentials, models.KerberosKeytabCredentials):
        return KerberosKeytabCredentials._from_rest_object(rest_credentials)
    if isinstance(rest_credentials, models.KerberosPasswordCredentials):
        return KerberosPasswordCredentials._from_rest_object(rest_credentials)

    return None
