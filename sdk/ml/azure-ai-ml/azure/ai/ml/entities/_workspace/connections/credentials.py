# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ConnectionAuthType,
    ManagedIdentity,
    ServicePrincipal,
    SharedAccessSignature,
    UsernamePassword,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class WorkspaceConnectionCredentials(RestTranslatableMixin):
    """Base class for workspace connection credentials."""

    def __init__(self):
        self.type = None


class SasTokenCredentials(WorkspaceConnectionCredentials):
    """Shared Access Signatures Token Credentials.

    :param sas: sas token
    :type sas: str
    """

    def __init__(self, *, sas: str):
        super().__init__()
        self.type = ConnectionAuthType.SAS
        self.sas = sas

    def _to_rest_object(self) -> SharedAccessSignature:
        return SharedAccessSignature(sas=self.sas)

    @classmethod
    def _from_rest_object(cls, obj: SharedAccessSignature) -> "SasTokenCredentials":
        return cls(sas=obj.sas if obj.sas else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SasTokenCredentials):
            return NotImplemented
        return self.sas == other.sas


class UsernamePasswordCredentials(WorkspaceConnectionCredentials):
    """Username Password Credentials.

    :param username: username
    :type username: str
    :param password: password
    :type password: str
    """

    def __init__(
        self,
        *,
        username: str,
        password: str,
    ):
        super().__init__()
        self.type = ConnectionAuthType.USERNAME_PASSWORD
        self.username = username
        self.password = password

    def _to_rest_object(self) -> UsernamePassword:
        return UsernamePassword(username=self.username, password=self.password)

    @classmethod
    def _from_rest_object(cls, obj: UsernamePassword) -> "UsernamePasswordCredentials":
        return cls(
            username=obj.username if obj.username else None,
            password=obj.password if obj.password else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UsernamePasswordCredentials):
            return NotImplemented
        return self.username == other.username and self.password == other.password


class ManagedIdentityCredentials(WorkspaceConnectionCredentials):
    """Managed Identity Credentials.

    :param client_id: client id, should be guid
    :type client_id: str
    :param resource_id: resource id
    :type resource_id: str
    """

    def __init__(self, *, client_id: str, resource_id: str):
        super().__init__()
        self.type = ConnectionAuthType.MANAGED_IDENTITY
        self.client_id = client_id
        # TODO: Check if both client_id and resource_id are required
        self.resource_id = resource_id

    def _to_rest_object(self) -> ManagedIdentity:
        return ManagedIdentity(client_id=self.client_id, resource_id=self.resource_id)

    @classmethod
    def _from_rest_object(cls, obj: ManagedIdentity) -> "ManagedIdentityCredentials":
        return cls(
            client_id=obj.client_id,
            resource_id=obj.resource_id,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManagedIdentityCredentials):
            return NotImplemented
        return self.client_id == other.client_id and self.resource_id == other.resource_id


class ServicePrincipalCredentials(WorkspaceConnectionCredentials):
    """Service Principal Credentials.

    :param client_id: client id, should be guid
    :type client_id: str
    :param client_secret: client secret
    :type client_secret: str
    :param tenant_id: tenant id, should be guid
    :type tenant_id: str
    """

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        tenant_id: str,
    ):
        super().__init__()
        self.type = ConnectionAuthType.SERVICE_PRINCIPAL
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def _to_rest_object(self) -> ServicePrincipal:
        return ServicePrincipal(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: ServicePrincipal) -> "ServicePrincipalCredentials":
        return cls(
            client_id=obj.client_id if obj.client_id else None,
            client_secret=obj.client_secret if obj.client_secret else None,
            tenant_id=obj.tenant_id if obj.tenant_id else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServicePrincipalCredentials):
            return NotImplemented
        return (
            self.client_id == other.client_id
            and self.client_secret == other.client_secret
            and self.tenant_id == other.tenant_id
        )


class AccessKeyCredentials(WorkspaceConnectionCredentials):
    """Access Key Credentials.

    :param access_key_id: access key id
    :type access_key_id: str
    :param secret_access_key: secret access key
    :type secret_access_key: str
    """

    def __init__(
        self,
        *,
        access_key_id: str,
        secret_access_key: str,
    ):
        super().__init__()
        self.type = ConnectionAuthType.ACCESS_KEY
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def _to_rest_object(self) -> UsernamePassword:
        return UsernamePassword(username=self.access_key_id, password=self.secret_access_key)

    @classmethod
    def _from_rest_object(cls, obj: UsernamePassword) -> "AccessKeyCredentials":
        return cls(
            access_key_id=obj.username if obj.username else None,
            secret_access_key=obj.password if obj.password else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccessKeyCredentials):
            return NotImplemented
        return self.access_key_id == other.access_key_id and self.secret_access_key == other.secret_access_key
