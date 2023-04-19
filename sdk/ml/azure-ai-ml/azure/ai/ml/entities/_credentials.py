# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,redefined-builtin

from abc import ABC
from typing import Dict, List, Optional, Union

from azure.ai.ml._azure_environments import _get_active_directory_url_from_metadata
from azure.ai.ml._restclient.v2022_01_01_preview.models import Identity as RestIdentityConfiguration
from azure.ai.ml._restclient.v2022_01_01_preview.models import ManagedIdentity as RestWorkspaceConnectionManagedIdentity
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    PersonalAccessToken as RestWorkspaceConnectionPersonalAccessToken,
)
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ServicePrincipal as RestWorkspaceConnectionServicePrincipal,
)
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    SharedAccessSignature as RestWorkspaceConnectionSharedAccessSignature,
)
from azure.ai.ml._restclient.v2022_01_01_preview.models import UserAssignedIdentity as RestUserAssignedIdentity
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    UsernamePassword as RestWorkspaceConnectionUsernamePassword,
)
from azure.ai.ml._restclient.v2022_05_01.models import ManagedServiceIdentity as RestManagedServiceIdentityConfiguration
from azure.ai.ml._restclient.v2022_05_01.models import UserAssignedIdentity as RestUserAssignedIdentityConfiguration
from azure.ai.ml._restclient.v2022_10_01.models import (
    AccountKeyDatastoreCredentials as RestAccountKeyDatastoreCredentials,
)
from azure.ai.ml._restclient.v2022_10_01.models import AccountKeyDatastoreSecrets as RestAccountKeyDatastoreSecrets
from azure.ai.ml._restclient.v2022_10_01.models import (
    CertificateDatastoreCredentials as RestCertificateDatastoreCredentials,
)
from azure.ai.ml._restclient.v2022_10_01.models import CertificateDatastoreSecrets, CredentialsType
from azure.ai.ml._restclient.v2022_10_01.models import NoneDatastoreCredentials as RestNoneDatastoreCredentials
from azure.ai.ml._restclient.v2022_10_01.models import SasDatastoreCredentials as RestSasDatastoreCredentials
from azure.ai.ml._restclient.v2022_10_01.models import SasDatastoreSecrets as RestSasDatastoreSecrets
from azure.ai.ml._restclient.v2022_10_01.models import (
    ServicePrincipalDatastoreCredentials as RestServicePrincipalDatastoreCredentials,
)
from azure.ai.ml._restclient.v2022_10_01.models import (
    ServicePrincipalDatastoreSecrets as RestServicePrincipalDatastoreSecrets,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ConnectionAuthType
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    WorkspaceConnectionAccessKey as RestWorkspaceConnectionAccessKey,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import AmlToken as RestAmlToken
from azure.ai.ml._restclient.v2023_04_01_preview.models import IdentityConfiguration as RestJobIdentityConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import IdentityConfigurationType
from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedIdentity as RestJobManagedIdentity
from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedServiceIdentity as RestRegistryManagedIdentity
from azure.ai.ml._restclient.v2023_04_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_pascal
from azure.ai.ml.constants._common import CommonYamlFields, IdentityType
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin, YamlTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException, ValidationErrorType, ValidationException


class _BaseIdentityConfiguration(ABC, DictMixin, RestTranslatableMixin):
    def __init__(self):
        self.type = None


class AccountKeyConfiguration(RestTranslatableMixin, DictMixin):
    def __init__(
        self,
        *,
        account_key: str,
    ):
        self.type = camel_to_snake(CredentialsType.ACCOUNT_KEY)
        self.account_key = account_key

    def _to_datastore_rest_object(self) -> RestAccountKeyDatastoreCredentials:
        secrets = RestAccountKeyDatastoreSecrets(key=self.account_key)
        return RestAccountKeyDatastoreCredentials(secrets=secrets)

    @classmethod
    def _from_datastore_rest_object(cls, obj: RestAccountKeyDatastoreCredentials) -> "AccountKeyConfiguration":
        return cls(account_key=obj.secrets.key if obj.secrets else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountKeyConfiguration):
            return NotImplemented
        return self.account_key == other.account_key

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class SasTokenConfiguration(RestTranslatableMixin, DictMixin):
    def __init__(
        self,
        *,
        sas_token: str,
    ):
        super().__init__()
        self.type = camel_to_snake(CredentialsType.SAS)
        self.sas_token = sas_token

    def _to_datastore_rest_object(self) -> RestSasDatastoreCredentials:
        secrets = RestSasDatastoreSecrets(sas_token=self.sas_token)
        return RestSasDatastoreCredentials(secrets=secrets)

    @classmethod
    def _from_datastore_rest_object(cls, obj: RestSasDatastoreCredentials) -> "SasTokenConfiguration":
        return cls(sas_token=obj.secrets.sas_token if obj.secrets else None)

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionSharedAccessSignature:
        return RestWorkspaceConnectionSharedAccessSignature(sas=self.sas_token)

    @classmethod
    def _from_workspace_connection_rest_object(
        cls, obj: Optional[RestWorkspaceConnectionSharedAccessSignature]
    ) -> "SasTokenConfiguration":
        return cls(sas_token=obj.sas if obj is not None and obj.sas else None)

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
    def _from_workspace_connection_rest_object(
        cls, obj: Optional[RestWorkspaceConnectionPersonalAccessToken]
    ) -> "PatTokenConfiguration":
        return cls(pat=obj.pat if obj is not None and obj.pat else None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatTokenConfiguration):
            return NotImplemented
        return self.pat == other.pat


class UsernamePasswordConfiguration(RestTranslatableMixin, DictMixin):
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
    def _from_workspace_connection_rest_object(
        cls, obj: Optional[RestWorkspaceConnectionUsernamePassword]
    ) -> "UsernamePasswordConfiguration":
        return cls(
            username=obj.username if obj is not None and obj.username else None,
            password=obj.password if obj is not None and obj.password else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UsernamePasswordConfiguration):
            return NotImplemented
        return self.username == other.username and self.password == other.password


class BaseTenantCredentials(RestTranslatableMixin, DictMixin, ABC):
    def __init__(
        self,
        authority_url: str = _get_active_directory_url_from_metadata(),
        resource_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
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
    def _from_datastore_rest_object(
        cls, obj: RestServicePrincipalDatastoreCredentials
    ) -> "ServicePrincipalConfiguration":
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
    def _from_workspace_connection_rest_object(
        cls, obj: Optional[RestWorkspaceConnectionServicePrincipal]
    ) -> "ServicePrincipalConfiguration":
        return cls(
            client_id=obj.client_id if obj is not None and obj.client_id else None,
            client_secret=obj.client_secret if obj is not None and obj.client_secret else None,
            tenant_id=obj.tenant_id if obj is not None and obj.tenant_id else None,
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
        certificate: Optional[str] = None,
        thumbprint: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = CredentialsType.CERTIFICATE
        self.certificate = certificate
        self.thumbprint = thumbprint

    def _to_datastore_rest_object(self) -> RestCertificateDatastoreCredentials:
        secrets = CertificateDatastoreSecrets(certificate=self.certificate)
        return RestCertificateDatastoreCredentials(
            authority_url=self.authority_url,
            resource_uri=self.resource_url,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            thumbprint=self.thumbprint,
            secrets=secrets,
        )

    @classmethod
    def _from_datastore_rest_object(cls, obj: RestCertificateDatastoreCredentials) -> "CertificateConfiguration":
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


class _BaseJobIdentityConfiguration(ABC, RestTranslatableMixin, DictMixin, YamlTranslatableMixin):
    def __init__(self):
        self.type = None

    @classmethod
    def _from_rest_object(cls, obj: RestJobIdentityConfiguration) -> "Identity":
        if obj is None:
            return None
        mapping = {
            IdentityConfigurationType.AML_TOKEN: AmlTokenConfiguration,
            IdentityConfigurationType.MANAGED: ManagedIdentityConfiguration,
            IdentityConfigurationType.USER_IDENTITY: UserIdentityConfiguration,
        }

        if isinstance(obj, dict):
            # TODO: support data binding expression
            obj = RestJobIdentityConfiguration.from_dict(obj)

        identity_class = mapping.get(obj.identity_type, None)
        if identity_class:
            # pylint: disable=protected-access
            return identity_class._from_job_rest_object(obj)
        msg = f"Unknown identity type: {obj.identity_type}"
        raise JobException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.IDENTITY,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
    ) -> Union["ManagedIdentityConfiguration", "UserIdentityConfiguration", "AmlTokenConfiguration"]:
        type_str = data.get(CommonYamlFields.TYPE)
        if type_str == IdentityType.MANAGED_IDENTITY:
            identity_cls = ManagedIdentityConfiguration
        elif type_str == IdentityType.USER_IDENTITY:
            identity_cls = UserIdentityConfiguration
        elif type_str == IdentityType.AML_TOKEN:
            identity_cls = AmlTokenConfiguration
        else:
            msg = f"Unsupported identity type: {type_str}."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.IDENTITY,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return identity_cls._load_from_dict(data)


class ManagedIdentityConfiguration(_BaseIdentityConfiguration):
    """Managed Identity Credentials.

    :param client_id: client id, should be guid
    :type client_id: str
    :param resource_id: resource id
    :type resource_id: str
    """

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        object_id: Optional[str] = None,
        principal_id: Optional[str] = None,
    ):
        super().__init__()
        self.type = IdentityType.MANAGED_IDENTITY
        self.client_id = client_id
        # TODO: Check if both client_id and resource_id are required
        self.resource_id = resource_id
        self.object_id = object_id
        self.principal_id = principal_id

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionManagedIdentity:
        return RestWorkspaceConnectionManagedIdentity(client_id=self.client_id, resource_id=self.resource_id)

    @classmethod
    def _from_workspace_connection_rest_object(
        cls, obj: Optional[RestWorkspaceConnectionManagedIdentity]
    ) -> "ManagedIdentityConfiguration":
        return cls(
            client_id=obj.client_id if obj is not None and obj.client_id else None,
            resource_id=obj.resource_id if obj is not None and obj.client_id else None,
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
    def _from_identity_configuration_rest_object(
        cls, rest_obj: RestUserAssignedIdentity, **kwargs
    ) -> "ManagedIdentityConfiguration":
        result = cls(resource_id=kwargs["resource_id"])
        result.__dict__.update(rest_obj.as_dict())
        return result

    def _to_online_endpoint_rest_object(self) -> RestUserAssignedIdentityConfiguration:
        return RestUserAssignedIdentityConfiguration()

    def _to_workspace_rest_object(self) -> RestUserAssignedIdentityConfiguration:
        return RestUserAssignedIdentityConfiguration(
            principal_id=self.principal_id,
            client_id=self.client_id,
        )

    @classmethod
    def _from_workspace_rest_object(cls, obj: RestUserAssignedIdentityConfiguration) -> "ManagedIdentityConfiguration":
        return cls(
            principal_id=obj.principal_id,
            client_id=obj.client_id,
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        from azure.ai.ml._schema.job.identity import ManagedIdentitySchema

        return ManagedIdentitySchema().dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict) -> "ManagedIdentityConfiguration":
        # pylint: disable=no-member
        from azure.ai.ml._schema.job.identity import ManagedIdentitySchema

        return ManagedIdentitySchema().load(data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManagedIdentityConfiguration):
            return NotImplemented
        return self.client_id == other.client_id and self.resource_id == other.resource_id


class UserIdentityConfiguration(_BaseIdentityConfiguration):
    """User identity configuration."""

    def __init__(self):
        super().__init__()
        self.type = IdentityType.USER_IDENTITY

    # pylint: disable=no-self-use
    def _to_job_rest_object(self) -> RestUserIdentity:
        return RestUserIdentity()

    @classmethod
    # pylint: disable=unused-argument
    def _from_job_rest_object(cls, obj: RestUserIdentity) -> "UserIdentity":
        return cls()

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        from azure.ai.ml._schema.job.identity import UserIdentitySchema

        return UserIdentitySchema().dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict) -> "UserIdentityConfiguration":
        # pylint: disable=no-member
        from azure.ai.ml._schema.job.identity import UserIdentitySchema

        return UserIdentitySchema().load(data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserIdentityConfiguration):
            return NotImplemented
        return self._to_job_rest_object() == other._to_job_rest_object()


class AmlTokenConfiguration(_BaseIdentityConfiguration):
    """AML Token identity configuration."""

    def __init__(self):
        super().__init__()
        self.type = IdentityType.AML_TOKEN

    # pylint: disable=no-self-use
    def _to_job_rest_object(self) -> RestAmlToken:
        return RestAmlToken()

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema

        return AMLTokenIdentitySchema().dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict) -> "AMLTokenIdentitySchema":
        # pylint: disable=no-member
        from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema

        return AMLTokenIdentitySchema().load(data)

    @classmethod
    # pylint: disable=unused-argument
    def _from_job_rest_object(cls, obj: RestAmlToken) -> "AmlTokenConfiguration":
        return cls()


# This class will be used to represent Identity property on compute, endpoint, and registry
class IdentityConfiguration(RestTranslatableMixin):
    """Managed identity specification."""

    def __init__(
        self, *, type: str, user_assigned_identities: Optional[List[ManagedIdentityConfiguration]] = None, **kwargs
    ):
        """Managed identity specification.

        :param type: Managed identity type, defaults to None
        :type type: str, optional
        :param user_assigned_identities: List of UserAssignedIdentity objects.
        :type user_assigned_identities: list, optional
        """

        self.type = type
        self.user_assigned_identities = user_assigned_identities
        self.principal_id = kwargs.pop("principal_id", None)
        self.tenant_id = kwargs.pop("tenant_id", None)

    def _to_compute_rest_object(self) -> RestIdentityConfiguration:
        rest_user_assigned_identities = (
            {uai.resource_id: uai._to_identity_configuration_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )
        return RestIdentityConfiguration(
            type=snake_to_pascal(self.type), user_assigned_identities=rest_user_assigned_identities
        )

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

    def _to_online_endpoint_rest_object(self) -> RestManagedServiceIdentityConfiguration:
        rest_user_assigned_identities = (
            {uai.resource_id: uai._to_online_endpoint_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )

        return RestManagedServiceIdentityConfiguration(
            type=snake_to_pascal(self.type),
            principal_id=self.principal_id,
            tenant_id=self.tenant_id,
            user_assigned_identities=rest_user_assigned_identities,
        )

    @classmethod
    def _from_online_endpoint_rest_object(cls, obj: RestManagedServiceIdentityConfiguration) -> "IdentityConfiguration":
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

    @classmethod
    def _from_workspace_rest_object(cls, obj: RestManagedServiceIdentityConfiguration) -> "IdentityConfiguration":
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

    def _to_workspace_rest_object(self) -> RestManagedServiceIdentityConfiguration:
        rest_user_assigned_identities = (
            {uai.resource_id: uai._to_workspace_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )
        return RestManagedServiceIdentityConfiguration(
            type=snake_to_pascal(self.type), user_assigned_identities=rest_user_assigned_identities
        )

    def _to_rest_object(self) -> RestRegistryManagedIdentity:
        return RestRegistryManagedIdentity(
            type=self.type,
            principal_id=self.principal_id,
            tenant_id=self.tenant_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRegistryManagedIdentity) -> "IdentityConfiguration":
        result = cls(
            type=obj.type,
            user_assigned_identities=None,
        )
        result.principal_id = obj.principal_id
        result.tenant_id = obj.tenant_id
        return result


class NoneCredentialConfiguration(RestTranslatableMixin):
    """None Credential Configuration."""

    def __init__(self):
        self.type = CredentialsType.NONE

    # pylint: disable=no-self-use
    def _to_datastore_rest_object(self) -> RestNoneDatastoreCredentials:
        return RestNoneDatastoreCredentials()

    @classmethod
    # pylint: disable=unused-argument
    def _from_datastore_rest_object(cls, obj: RestNoneDatastoreCredentials) -> "NoneCredentialConfiguration":
        return cls()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NoneCredentialConfiguration):
            return True
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class AccessKeyConfiguration(RestTranslatableMixin, DictMixin):
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
        self.type = camel_to_snake(ConnectionAuthType.ACCESS_KEY)
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def _to_workspace_connection_rest_object(self) -> RestWorkspaceConnectionAccessKey:
        return RestWorkspaceConnectionAccessKey(
            access_key_id=self.access_key_id, secret_access_key=self.secret_access_key
        )

    @classmethod
    def _from_workspace_connection_rest_object(
        cls, obj: Optional[RestWorkspaceConnectionAccessKey]
    ) -> "AccessKeyConfiguration":
        return cls(
            access_key_id=obj.access_key_id if obj is not None and obj.access_key_id else None,
            secret_access_key=obj.secret_access_key if obj is not None and obj.secret_access_key else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccessKeyConfiguration):
            return NotImplemented
        return self.access_key_id == other.access_key_id and self.secret_access_key == other.secret_access_key
