# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,redefined-builtin

from abc import ABC
from typing import List

from azure.ai.ml._azure_environments import _get_active_directory_url_from_metadata
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_pascal
from azure.ai.ml.entities._mixins import RestTranslatableMixin, DictMixin
from azure.ai.ml._restclient.v2022_05_01.models import (
    AccountKeyDatastoreCredentials as RestAccountKeyDatastoreCredentials,
    AccountKeyDatastoreSecrets as RestAccountKeyDatastoreSecrets,
    CertificateDatastoreCredentials,
    CertificateDatastoreSecrets,
    CredentialsType,
    SasDatastoreCredentials as RestSasDatastoreCredentials,
    SasDatastoreSecrets as RestSasDatastoreSecrets,
    ServicePrincipalDatastoreCredentials as RestServicePrincipalDatastoreCredentials,
    ServicePrincipalDatastoreSecrets as RestServicePrincipalDatastoreSecrets,
)

from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ConnectionAuthType,
    ManagedIdentity as RestWorkspaceConnectionManagedIdentity,
    PersonalAccessToken as RestWorkspaceConnectionPersonalAccessToken,
    ServicePrincipal as RestWorkspaceConnectionServicePrincipal,
    SharedAccessSignature as RestWorkspaceConnectionSharedAccessSignature,
    UsernamePassword as RestWorkspaceConnectionUsernamePassword,
)

from azure.ai.ml._restclient.v2022_06_01_preview.models import (
    IdentityConfigurationType,
    ManagedIdentity as RestJobManagedIdentity,
    UserIdentity as RestUserIdentity,
    AmlToken as RestAmlToken
)

from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    UserAssignedIdentity as RestUserAssignedIdentity,
    Identity as RestIdentityConfiguration
)

from azure.ai.ml._restclient.v2022_05_01.models import (
    ManagedServiceIdentity as RestOnlineEndpointIdentityConfiguration,
    UserIdentity as RestOnlineEndpointManagedIdentityConfiguration
)


class AccountKeyConfiguration(RestTranslatableMixin, ABC):
    def __init__(
            self,
            *,
            account_key: str,
    ):
        self.type = camel_to_snake(CredentialsType.ACCOUNT_KEY)
        self.account_key = account_key

    def _to_rest_object(self) -> RestAccountKeyDatastoreCredentials:
        secrets = RestAccountKeyDatastoreSecrets(key=self.account_key)
        return RestAccountKeyDatastoreCredentials(secrets=secrets)

    @classmethod
    def _from_rest_object(cls, obj: RestAccountKeyDatastoreCredentials) -> "AccountKeyConfiguration":
        return cls(account_key=obj.secrets.key if obj.secrets else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountKeyConfiguration):
            return NotImplemented
        return self.account_key == other.account_key

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class SasTokenConfiguration(RestTranslatableMixin, ABC):
    def __init__(
            self,
            *,
            sas_token: str,
    ):
        super().__init__()
        self.type = camel_to_snake(CredentialsType.SAS)
        self.sas_token = sas_token

    def _to_rest_datastore_object(self) -> RestSasDatastoreCredentials:
        secrets = RestSasDatastoreSecrets(sas_token=self.sas_token)
        return RestSasDatastoreCredentials(secrets=secrets)

    @classmethod
    def _from_datastore_rest_object(cls, obj: RestSasDatastoreCredentials) -> "SasTokenConfiguration":
        return cls(sas_token=obj.secrets.sas_token if obj.secrets else None)

    def _to_rest_workspace_connection_object(self) -> RestWorkspaceConnectionSharedAccessSignature:
        return RestWorkspaceConnectionSharedAccessSignature(sas=self.sas_token)

    @classmethod
    def _from_workspace_connection_rest_object(
        cls,
        obj: RestWorkspaceConnectionSharedAccessSignature
    ) -> "SasTokenConfiguration":
        return cls(sas_token=obj.sas if obj.sas else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SasTokenConfiguration):
            return NotImplemented
        return self.sas_token == other.sas_token

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class PatTokenConfiguration(RestTranslatableMixin, DictMixin):
    """Personal access token credentials.

    :param pat: personal access token
    :type pat: str
    """

    def __init__(self, *, pat: str):
        super().__init__()
        self.type = camel_to_snake(ConnectionAuthType.PAT)
        self.pat = pat

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionPersonalAccessToken:
        return RestWorkspaceConnectionPersonalAccessToken(pat=self.pat)

    @classmethod
    def _from_workspace_connection_rest_object(cls, obj: RestWorkspaceConnectionPersonalAccessToken) \
            -> "PatTokenConfiguration":
        return cls(pat=obj.pat if obj and obj.pat else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatTokenConfiguration):
            return NotImplemented
        return self.pat == other.pat


class UsernamePasswordConfiguration(RestTranslatableMixin, ABC):
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
        self.type = camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        self.username = username
        self.password = password

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionUsernamePassword:
        return RestWorkspaceConnectionUsernamePassword(username=self.username, password=self.password)

    @classmethod
    def _from_workspace_connection_rest_object(cls, obj: RestWorkspaceConnectionUsernamePassword) \
            -> "UsernamePasswordConfiguration":
        return cls(
            username=obj.username if obj and obj.username else None,
            password=obj.password if obj and obj.password else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UsernamePasswordConfiguration):
            return NotImplemented
        return self.username == other.username and self.password == other.password


class BaseTenantCredentials(RestTranslatableMixin, ABC):
    def __init__(
            self,
            authority_url: str = _get_active_directory_url_from_metadata(),
            resource_url: str = None,
            tenant_id: str = None,
            client_id: str = None,
    ):
        super().__init__()
        self.authority_url = authority_url
        self.resource_url = resource_url
        self.tenant_id = tenant_id
        self.client_id = client_id


class ServicePrincipalConfiguration(BaseTenantCredentials):
    def __init__(
            self,
            *,
            client_secret: str,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = camel_to_snake(CredentialsType.SERVICE_PRINCIPAL)
        self.client_secret = client_secret

    def _to_datastore_rest_object(self) -> RestServicePrincipalDatastoreCredentials:
        secrets = RestServicePrincipalDatastoreSecrets(client_secret=self.client_secret)
        return RestServicePrincipalDatastoreCredentials(
            authority_url=self.authority_url,
            resource_uri=self.resource_url,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            secrets=secrets,
        )

    @classmethod
    def _from_datastore_rest_object(cls, obj: RestServicePrincipalDatastoreCredentials) \
            -> "ServicePrincipalConfiguration":
        return cls(
            authority_url=obj.authority_url,
            resource_url=obj.resource_url,
            tenant_id=obj.tenant_id,
            client_id=obj.client_id,
            client_secret=obj.secrets.client_secret if obj.secrets else None,
        )

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionServicePrincipal:
        return RestWorkspaceConnectionServicePrincipal(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )

    @classmethod
    def _from_workspace_connection_rest_object(cls, obj: RestWorkspaceConnectionServicePrincipal) \
            -> "ServicePrincipalConfiguration":
        return cls(
            client_id=obj.client_id if obj.client_id else None,
            client_secret=obj.client_secret if obj.client_secret else None,
            tenant_id=obj.tenant_id if obj.tenant_id else None,
            authority_url=None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServicePrincipalConfiguration):
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


class CertificateConfiguration(BaseTenantCredentials):
    def __init__(
            self,
            certificate: str = None,
            thumbprint: str = None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = CredentialsType.CERTIFICATE
        self.certificate = certificate
        self.thumbprint = thumbprint

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
    def _from_rest_object(cls, obj: CertificateDatastoreCredentials) -> "CertificateConfiguration":
        return cls(
            authority_url=obj.authority_url,
            resource_url=obj.resource_uri,
            tenant_id=obj.tenant_id,
            client_id=obj.client_id,
            thumbprint=obj.thumbprint,
            certificate=obj.secrets.certificate if obj.secrets else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CertificateConfiguration):
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


class ManagedIdentityConfiguration(RestTranslatableMixin, DictMixin):
    """Managed Identity Credentials.

    :param client_id: client id, should be guid
    :type client_id: str
    :param resource_id: resource id
    :type resource_id: str
    """

    def __init__(
            self,
            *,
            client_id: str = None,
            resource_id: str = None,
            object_id: str = None,
    ):
        self.type = camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
        self.client_id = client_id
        # TODO: Check if both client_id and resource_id are required
        self.resource_id = resource_id
        self.object_id = object_id

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionManagedIdentity:
        return RestWorkspaceConnectionManagedIdentity(client_id=self.client_id, resource_id=self.resource_id)

    @classmethod
    def _from_workspace_connection_rest_object(cls,
            obj: RestWorkspaceConnectionManagedIdentity) -> "ManagedIdentityConfiguration":
        return cls(
            client_id=obj.client_id if obj else None,
            resource_id=obj.resource_id if obj else None,
        )

    def _to_job_rest_object(self) -> RestJobManagedIdentity:
        return RestJobManagedIdentity(
            client_id=self.client_id,
            object_id=self.object_id,
            resource_id=self.resource_id,
        )

    @classmethod
    def _from_job_rest_object(cls, obj: RestJobManagedIdentity) -> "ManagedIdentityConfiguration":
        return cls(
            client_id=obj.client_id,
            object_id=obj.client_id,
            resource_id=obj.resource_id,
        )

    # pylint: disable=no-self-use
    def _to_identity_configuration_rest_object(self) -> RestUserAssignedIdentity:
        return RestUserAssignedIdentity()

    @classmethod
    def _from_identity_configuration_rest_object(cls, rest_obj: RestUserAssignedIdentity,
                                                 **kwargs) -> "ManagedIdentityConfiguration":
        result = cls(resource_id=kwargs["resource_id"])
        result.__dict__.update(rest_obj.as_dict())
        return result

    def _to_online_endpoint_rest_object(self) -> RestOnlineEndpointManagedIdentityConfiguration:
        return RestOnlineEndpointManagedIdentityConfiguration()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManagedIdentityConfiguration):
            return NotImplemented
        return self.client_id == other.client_id and self.resource_id == other.resource_id


class UserIdentityConfiguration(ABC, RestTranslatableMixin):
    """User identity configuration."""

    def __init__(self):
        self.type = camel_to_snake(IdentityConfigurationType.USER_IDENTITY)

    # pylint: disable=no-self-use
    def _to_job_rest_object(self) -> RestUserIdentity:
        return RestUserIdentity()

    @classmethod
    # pylint: disable=unused-argument
    def _from_job_rest_object(cls, obj: RestUserIdentity) -> "UserIdentity":
        return cls()


class AmlTokenConfiguration(ABC, RestTranslatableMixin):
    """AML Token identity configuration."""

    def __init__(self):
        self.type = camel_to_snake(IdentityConfigurationType.AML_TOKEN)

    # pylint: disable=no-self-use
    def _to_job_rest_object(self) -> RestAmlToken:
        return RestAmlToken()

    @classmethod
    # pylint: disable=unused-argument
    def _from_job_rest_object(cls, obj: RestAmlToken) -> "AmlTokenConfiguration":
        return cls()


# This class will be used to represent Identity property on compute and endpoint
class IdentityConfiguration(RestTranslatableMixin):
    """Managed identity specification."""

    def __init__(self, *, type: str, user_assigned_identities: List[ManagedIdentityConfiguration] = None):
        """Managed identity specification.

        :param type: Managed identity type, defaults to None
        :type type: str, optional
        :param user_assigned_identities: List of UserAssignedIdentity objects.
        :type user_assigned_identities: list, optional
        """

        self.type = type
        self.user_assigned_identities = user_assigned_identities
        self.principal_id = None
        self.tenant_id = None

    def _to_compute_rest_object(self) -> RestIdentityConfiguration:
        rest_user_assigned_identities = (
            {uai.resource_id: uai._to_identity_configuration_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )
        return RestIdentityConfiguration(type=snake_to_pascal(self.type),
                                         user_assigned_identities=rest_user_assigned_identities)

    @classmethod
    def _from_compute_rest_object(cls, obj: RestIdentityConfiguration) -> "IdentityConfiguration":
        from_rest_user_assigned_identities = (
            [
                ManagedIdentityConfiguration._from_identity_configuration_rest_object(uai, resource_id=resource_id)
                for (resource_id, uai) in obj.user_assigned_identities.items()
            ]
            if obj.user_assigned_identities
            else None
        )
        result = cls(
            type=camel_to_snake(obj.type),
            user_assigned_identities=from_rest_user_assigned_identities,
        )
        result.principal_id = obj.principal_id
        result.tenant_id = obj.tenant_id
        return result

    def _to_online_endpoint_rest_object(self) -> RestOnlineEndpointIdentityConfiguration:
        rest_user_assigned_identities = (
            {uai.resource_id: uai._to_online_endpoint_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )

        return RestOnlineEndpointIdentityConfiguration(
            type=snake_to_pascal(self.type),
            principal_id=self.principal_id,
            tenant_id=self.tenant_id,
            user_assigned_identities=None,
        )

    @classmethod
    def _from_online_endpoint_rest_object(cls, obj: RestOnlineEndpointIdentityConfiguration) -> "IdentityConfiguration":

