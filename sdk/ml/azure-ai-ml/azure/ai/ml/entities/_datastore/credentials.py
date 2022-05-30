# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._constants import DEFAULT_AUTHORITY_URL
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2022_05_01.models import (
    AccountKeyDatastoreCredentials,
    AccountKeyDatastoreSecrets,
    SasDatastoreCredentials,
    SasDatastoreSecrets,
    ServicePrincipalDatastoreCredentials,
    ServicePrincipalDatastoreSecrets,
    CertificateDatastoreCredentials,
    CertificateDatastoreSecrets,
    NoneDatastoreCredentials,
    CredentialsType,
)


class DatastoreCredentials(RestTranslatableMixin):
    def __init__(self, type: str = None):
        self.type = type


class NoneCredentials(DatastoreCredentials):
    def __init__(
        self,
    ):
        self.type = CredentialsType.NONE

    def _to_rest_object(self) -> NoneDatastoreCredentials:
        return NoneDatastoreCredentials()

    @classmethod
    def _from_rest_object(cls, obj: NoneDatastoreCredentials) -> "NoneCredentials":
        return cls()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NoneCredentials):
            return True
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class AccountKeyCredentials(DatastoreCredentials):
    def __init__(
        self,
        *,
        account_key: str,
    ):
        self.type = CredentialsType.ACCOUNT_KEY
        self.account_key = account_key

    def _to_rest_object(self) -> AccountKeyDatastoreCredentials:
        secrets = AccountKeyDatastoreSecrets(key=self.account_key)
        return AccountKeyDatastoreCredentials(secrets=secrets)

    @classmethod
    def _from_rest_object(cls, obj: AccountKeyDatastoreCredentials) -> "AccountKeyCredentials":
        return cls(account_key=obj.secrets.key if obj.secrets else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountKeyCredentials):
            return NotImplemented
        return self.account_key == other.account_key

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class SasTokenCredentials(DatastoreCredentials):
    def __init__(
        self,
        *,
        sas_token: str,
    ):
        self.type = CredentialsType.SAS
        self.sas_token = sas_token

    def _to_rest_object(self) -> SasDatastoreCredentials:
        secrets = SasDatastoreSecrets(sas_token=self.sas_token)
        return SasDatastoreCredentials(secrets=secrets)

    @classmethod
    def _from_rest_object(cls, obj: SasDatastoreCredentials) -> "AccountKeyCredentials":
        return cls(sas_token=obj.secrets.sas_token if obj.secrets else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SasTokenCredentials):
            return NotImplemented
        return self.sas_token == other.sas_token

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class BaseTenantCredentials(DatastoreCredentials):
    def __init__(
        self,
        authority_url: str = DEFAULT_AUTHORITY_URL,
        resource_url: str = None,
        tenant_id: str = None,
        client_id: str = None,
    ):
        self.authority_url = authority_url
        self.resource_url = resource_url
        self.tenant_id = tenant_id
        self.client_id = client_id


class ServicePrincipalCredentials(BaseTenantCredentials):
    def __init__(
        self,
        *,
        client_secret: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = CredentialsType.SERVICE_PRINCIPAL
        self.client_secret = client_secret

    def _to_rest_object(self) -> ServicePrincipalDatastoreCredentials:
        secrets = ServicePrincipalDatastoreSecrets(client_secret=self.client_secret)
        return ServicePrincipalDatastoreCredentials(
            authority_url=self.authority_url,
            resource_uri=self.resource_url,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            secrets=secrets,
        )

    @classmethod
    def _from_rest_object(cls, obj: ServicePrincipalDatastoreCredentials) -> "ServicePrincipalCredentials":
        return cls(
            authority_url=obj.authority_url,
            resource_url=obj.resource_url,
            tenant_id=obj.tenant_id,
            client_id=obj.client_id,
            client_secret=obj.secrets.client_secret if obj.secrets else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServicePrincipalCredentials):
            return NotImplemented
        return (
            self.authority_url == other.authority_url
            and self.resource_url == other.resource_url
            and self.tenant_id == other.tenant_id
            and self.client_id == other.client_id
            and self.client_secret == other.client_secret
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class CertificateCredentials(BaseTenantCredentials):
    def __init__(
        self,
        certificate: str = None,
        thumprint: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = CredentialsType.CERTIFICATE
        self.certificate = certificate
        self.thumbprint = thumprint

    def _to_rest_object(self) -> CertificateDatastoreCredentials:
        secrets = CertificateDatastoreSecrets(certificate=self.certificate)
        return CertificateDatastoreCredentials(
            authority_url=self.authority_url,
            resource_uri=self.resource_url,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            thumbprint=self.thumbprint,
            secrets=secrets,
        )

    @classmethod
    def _from_rest_object(cls, obj: CertificateDatastoreCredentials) -> "CertificateCredentials":
        return cls(
            authority_url=obj.authority_url,
            resource_url=obj.resource_uri,
            tenant_id=obj.tenant_id,
            client_id=obj.client_id,
            thumbprint=obj.thumbprint,
            certificate=obj.secrets.certificate if obj.secrets else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CertificateCredentials):
            return NotImplemented
        return (
            self.authority_url == other.authority_url
            and self.resource_url == other.resource_url
            and self.tenant_id == other.tenant_id
            and self.client_id == other.client_id
            and self.thumbprint == other.thumbprint
            and self.certificate == other.certificate
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
