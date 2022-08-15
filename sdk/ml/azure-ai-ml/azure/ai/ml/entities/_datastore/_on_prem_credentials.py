# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from base64 import b64encode

from azure.ai.ml._restclient.v2022_02_01_preview import models as model_preview
from azure.ai.ml._utils._experimental import experimental

from .credentials import DatastoreCredentials


@experimental
class BaseKerberosCredentials(DatastoreCredentials):
    def __init__(self, kerberos_realm: str, kerberos_kdc_address: str, kerberos_principal: str):
        self.kerberos_realm = kerberos_realm
        self.kerberos_kdc_address = kerberos_kdc_address
        self.kerberos_principal = kerberos_principal


@experimental
class KerberosKeytabCredentials(BaseKerberosCredentials):
    def __init__(
        self,
        *,
        kerberos_realm: str,
        kerberos_kdc_address: str,
        kerberos_principal: str,
        kerberos_keytab: str,
        **kwargs,
    ):
        super().__init__(
            kerberos_realm=kerberos_realm,
            kerberos_kdc_address=kerberos_kdc_address,
            kerberos_principal=kerberos_principal,
            **kwargs,
        )
        self.type = model_preview.CredentialsType.KERBEROS_KEYTAB
        self.kerberos_keytab = kerberos_keytab

    def _to_rest_object(self) -> model_preview.KerberosKeytabCredentials:
        use_this_keytab = None
        if self.kerberos_keytab:
            with open(self.kerberos_keytab, "rb") as f:
                use_this_keytab = b64encode(f.read()).decode("utf-8")
        secrets = model_preview.KerberosKeytabSecrets(kerberos_keytab=use_this_keytab)
        return model_preview.KerberosKeytabCredentials(
            kerberos_kdc_address=self.kerberos_kdc_address,
            kerberos_principal=self.kerberos_principal,
            kerberos_realm=self.kerberos_realm,
            secrets=secrets,
        )

    @classmethod
    def _from_rest_object(cls, obj: model_preview.KerberosKeytabCredentials) -> "KerberosKeytabCredentials":
        return cls(
            kerberos_kdc_address=obj.kerberos_kdc_address,
            kerberos_principal=obj.kerberos_principal,
            kerberos_realm=obj.kerberos_realm,
            kerberos_keytab=obj.secrets.kerberos_keytab if obj.secrets else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KerberosKeytabCredentials):
            return NotImplemented
        return (
            self.kerberos_kdc_address == other.kerberos_kdc_address
            and self.kerberos_principal == other.kerberos_principal
            and self.kerberos_realm == other.kerberos_realm
            and self.kerberos_keytab == other.kerberos_keytab
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


@experimental
class KerberosPasswordCredentials(BaseKerberosCredentials):
    def __init__(
        self,
        *,
        kerberos_realm: str,
        kerberos_kdc_address: str,
        kerberos_principal: str,
        kerberos_password: str,
        **kwargs,
    ):
        super().__init__(
            kerberos_realm=kerberos_realm,
            kerberos_kdc_address=kerberos_kdc_address,
            kerberos_principal=kerberos_principal,
            **kwargs,
        )
        self.type = model_preview.CredentialsType.KERBEROS_PASSWORD
        self.kerberos_password = kerberos_password

    def _to_rest_object(self) -> model_preview.KerberosPasswordCredentials:
        secrets = model_preview.KerberosPasswordSecrets(kerberos_password=self.kerberos_password)
        return model_preview.KerberosPasswordCredentials(
            kerberos_kdc_address=self.kerberos_kdc_address,
            kerberos_principal=self.kerberos_principal,
            kerberos_realm=self.kerberos_realm,
            secrets=secrets,
        )

    @classmethod
    def _from_rest_object(cls, obj: model_preview.KerberosPasswordCredentials) -> "KerberosPasswordCredentials":
        return cls(
            kerberos_kdc_address=obj.kerberos_kdc_address,
            kerberos_principal=obj.kerberos_principal,
            kerberos_realm=obj.kerberos_realm,
            kerberos_password=obj.secrets.kerberos_password if obj.secrets else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KerberosPasswordCredentials):
            return NotImplemented
        return (
            self.kerberos_kdc_address == other.kerberos_kdc_address
            and self.kerberos_principal == other.kerberos_principal
            and self.kerberos_realm == other.kerberos_realm
            and self.kerberos_password == other.kerberos_password
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
