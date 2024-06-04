# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Dict

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class BaseKerberosCredentials(metaclass=PatchedSchemaMeta):
    kerberos_realm = fields.Str(required=True)
    kerberos_kdc_address = fields.Str(required=True)
    kerberos_principal = fields.Str(required=True)


class KerberosPasswordSchema(BaseKerberosCredentials):
    kerberos_password = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> "KerberosPasswordCredentials":
        from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosPasswordCredentials

        return KerberosPasswordCredentials(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosPasswordCredentials

        if not isinstance(data, KerberosPasswordCredentials):
            raise ValidationError("Cannot dump non-KerberosPasswordCredentials object into KerberosPasswordCredentials")
        return data


class KerberosKeytabSchema(BaseKerberosCredentials):
    kerberos_keytab = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> "KerberosKeytabCredentials":
        from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials

        return KerberosKeytabCredentials(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosKeytabCredentials

        if not isinstance(data, KerberosKeytabCredentials):
            raise ValidationError("Cannot dump non-KerberosKeytabCredentials object into KerberosKeytabCredentials")
        return data
