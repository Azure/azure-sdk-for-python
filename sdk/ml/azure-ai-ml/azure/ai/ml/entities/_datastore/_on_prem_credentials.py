# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from base64 import b64encode
from typing import Any, Dict, Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._credentials import NoneCredentialConfiguration


# ``KerberosKeytabCredentials``/``KerberosPasswordCredentials`` (and their secrets) are absent from the
# arm_ml_service (2025-12) model set, so these entities serialize JSON-direct to the 2023-04 camelCase
# wire contract. The wire ``credentialsType``/``secretsType`` discriminator values are preserved.
_KERBEROS_KEYTAB = "KerberosKeytab"
_KERBEROS_PASSWORD = "KerberosPassword"


# TODO: Move classes in this file to azure.ai.ml.entities._credentials
@experimental
class BaseKerberosCredentials(NoneCredentialConfiguration):
    def __init__(self, kerberos_realm: str, kerberos_kdc_address: str, kerberos_principal: str):
        super().__init__()
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
        kerberos_keytab: Optional[str],
        **kwargs: Any,
    ):
        super().__init__(
            kerberos_realm=kerberos_realm,
            kerberos_kdc_address=kerberos_kdc_address,
            kerberos_principal=kerberos_principal,
            **kwargs,
        )
        self.type = _KERBEROS_KEYTAB
        self.kerberos_keytab = kerberos_keytab

    def _to_rest_object(self) -> Dict[str, Any]:
        use_this_keytab = None
        if self.kerberos_keytab:
            with open(self.kerberos_keytab, "rb") as f:
                use_this_keytab = b64encode(f.read()).decode("utf-8")
        return {
            "credentialsType": _KERBEROS_KEYTAB,
            "kerberosKdcAddress": self.kerberos_kdc_address,
            "kerberosPrincipal": self.kerberos_principal,
            "kerberosRealm": self.kerberos_realm,
            "secrets": {"secretsType": _KERBEROS_KEYTAB, "kerberosKeytab": use_this_keytab},
        }

    @classmethod
    def _from_rest_object(cls, obj: Any) -> "KerberosKeytabCredentials":
        secrets = obj.get("secrets") if obj is not None else None
        return cls(
            kerberos_kdc_address=obj.get("kerberosKdcAddress"),
            kerberos_principal=obj.get("kerberosPrincipal"),
            kerberos_realm=obj.get("kerberosRealm"),
            kerberos_keytab=secrets.get("kerberosKeytab") if secrets else None,
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
        kerberos_password: Optional[str],
        **kwargs: Any,
    ):
        super().__init__(
            kerberos_realm=kerberos_realm,
            kerberos_kdc_address=kerberos_kdc_address,
            kerberos_principal=kerberos_principal,
            **kwargs,
        )
        self.type = _KERBEROS_PASSWORD
        self.kerberos_password = kerberos_password

    def _to_rest_object(self) -> Dict[str, Any]:
        return {
            "credentialsType": _KERBEROS_PASSWORD,
            "kerberosKdcAddress": self.kerberos_kdc_address,
            "kerberosPrincipal": self.kerberos_principal,
            "kerberosRealm": self.kerberos_realm,
            "secrets": {"secretsType": _KERBEROS_PASSWORD, "kerberosPassword": self.kerberos_password},
        }

    @classmethod
    def _from_rest_object(cls, obj: Any) -> "KerberosPasswordCredentials":
        secrets = obj.get("secrets") if obj is not None else None
        return cls(
            kerberos_kdc_address=obj.get("kerberosKdcAddress"),
            kerberos_principal=obj.get("kerberosPrincipal"),
            kerberos_realm=obj.get("kerberosRealm"),
            kerberos_password=secrets.get("kerberosPassword") if secrets else None,
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
