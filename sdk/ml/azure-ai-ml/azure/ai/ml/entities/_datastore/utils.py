# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from azure.ai.ml._restclient.v2022_02_01_preview import models as models_preview
from azure.ai.ml._restclient.v2022_05_01 import models
from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials, KerberosPasswordCredentials
from azure.ai.ml.entities._datastore.credentials import (
    AccountKeyCredentials,
    CertificateCredentials,
    NoneCredentials,
    SasTokenCredentials,
    ServicePrincipalCredentials,
)


def from_rest_datastore_credentials(rest_credentials: models.DatastoreCredentials):
    if isinstance(rest_credentials, models.AccountKeyDatastoreCredentials):
        return AccountKeyCredentials._from_rest_object(rest_credentials)
    elif isinstance(rest_credentials, models.SasDatastoreCredentials):
        return SasTokenCredentials._from_rest_object(rest_credentials)
    elif isinstance(rest_credentials, models.ServicePrincipalDatastoreCredentials):
        return ServicePrincipalCredentials._from_rest_object(rest_credentials)
    elif isinstance(rest_credentials, models.CertificateDatastoreCredentials):
        return CertificateCredentials._from_rest_object(rest_credentials)
    elif isinstance(rest_credentials, models.NoneDatastoreCredentials):
        return NoneCredentials._from_rest_object(rest_credentials)


def _from_rest_datastore_credentials_preview(
    rest_credentials: models_preview.DatastoreCredentials,
):
    if isinstance(rest_credentials, models_preview.KerberosKeytabCredentials):
        return KerberosKeytabCredentials._from_rest_object(rest_credentials)
    elif isinstance(rest_credentials, models_preview.KerberosPasswordCredentials):
        return KerberosPasswordCredentials._from_rest_object(rest_credentials)
