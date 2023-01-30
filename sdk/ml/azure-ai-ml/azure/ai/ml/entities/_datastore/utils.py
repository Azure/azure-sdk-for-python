# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from azure.ai.ml._restclient.v2022_10_01_preview import models as models_preview
from azure.ai.ml._restclient.v2022_10_01 import models
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials, KerberosPasswordCredentials


def from_rest_datastore_credentials(rest_credentials: models.DatastoreCredentials):
    config_class = NoneCredentialConfiguration

    if isinstance(rest_credentials, models.AccountKeyDatastoreCredentials):
        config_class = AccountKeyConfiguration
    elif isinstance(rest_credentials, models.SasDatastoreCredentials):
        config_class = SasTokenConfiguration
    elif isinstance(rest_credentials, models.ServicePrincipalDatastoreCredentials):
        config_class = ServicePrincipalConfiguration
    elif isinstance(rest_credentials, models.CertificateDatastoreCredentials):
        config_class = CertificateConfiguration

    return config_class._from_datastore_rest_object(rest_credentials)


def _from_rest_datastore_credentials_preview(
    rest_credentials: models_preview.DatastoreCredentials,
):
    if isinstance(rest_credentials, models_preview.KerberosKeytabCredentials):
        return KerberosKeytabCredentials._from_rest_object(rest_credentials)
    if isinstance(rest_credentials, models_preview.KerberosPasswordCredentials):
        return KerberosPasswordCredentials._from_rest_object(rest_credentials)
