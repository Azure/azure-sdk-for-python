# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from azure.core.rest import HttpResponse

from ._enums import (
    KeyVaultEkmConnectivityMode,
    KeyVaultEkmPrivateEndpointConnectionStatus,
    KeyVaultEkmPrivateEndpointOperationStatus,
    KeyVaultEkmPrivateEndpointOperationType,
    KeyVaultEkmPrivateEndpointProvisioningState,
    KeyVaultSettingType,
)
from ._generated.models import (
    EkmConnection,
    EkmPrivateEndpoint,
    EkmPrivateEndpointConnectionState,
    EkmPrivateEndpointOperation,
    EkmPrivateEndpointProperties,
    EkmProxyClientCertificateInfo,
    EkmProxyInfo,
    FullBackupOperation,
    Permission,
    RoleAssignment,
    RoleAssignmentProperties,
    RoleAssignmentPropertiesWithScope,
    RoleDefinition,
    Setting,
)


class KeyVaultPermission(object):
    """Role definition permissions.

    :ivar list[str] actions: Action permissions that are granted.
    :ivar list[str] not_actions: Action permissions that are excluded but not denied. They may be granted by other role
     definitions assigned to a principal.
    :ivar list[str] data_actions: Data action permissions that are granted.
    :ivar list[str] not_data_actions: Data action permissions that are excluded but not denied. They may be granted by
     other role definitions assigned to a principal.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.actions = kwargs.get("actions")
        self.not_actions = kwargs.get("not_actions")
        self.data_actions = kwargs.get("data_actions")
        self.not_data_actions = kwargs.get("not_data_actions")

    @classmethod
    def _from_generated(cls, permissions: Permission) -> "KeyVaultPermission":
        return cls(
            actions=permissions.actions,
            not_actions=permissions.not_actions,
            data_actions=permissions.data_actions,
            not_data_actions=permissions.not_data_actions,
        )


class KeyVaultRoleAssignment(object):
    """Represents the assignment to a principal of a role over a scope

    :ivar str name: the assignment's name
    :ivar KeyVaultRoleAssignmentProperties properties: the assignment's properties
    :ivar str role_assignment_id: unique identifier for the assignment
    :ivar str type: type of the assignment
    """

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.get("name")
        self.properties = kwargs.get("properties")
        self.role_assignment_id = kwargs.get("role_assignment_id")
        self.type = kwargs.get("assignment_type")

    def __repr__(self) -> str:
        return f"KeyVaultRoleAssignment<{self.role_assignment_id}>"

    @classmethod
    def _from_generated(cls, role_assignment: RoleAssignment) -> "KeyVaultRoleAssignment":
        # pylint:disable=protected-access
        return cls(
            role_assignment_id=role_assignment.id,
            name=role_assignment.name,
            assignment_type=role_assignment.type,
            properties=(
                KeyVaultRoleAssignmentProperties._from_generated(role_assignment.properties)
                if role_assignment.properties
                else KeyVaultRoleAssignmentProperties()
            ),
        )


class KeyVaultRoleAssignmentProperties(object):
    """Properties of a role assignment

    :ivar str principal_id: ID of the principal the assignment applies to. This maps to an Active Directory user,
        service principal, or security group.
    :ivar str role_definition_id: ID of the scope's role definition
    :ivar str scope: the scope of the assignment
    """

    def __init__(self, **kwargs: Any) -> None:
        self.principal_id = kwargs.get("principal_id")
        self.role_definition_id = kwargs.get("role_definition_id")
        self.scope = kwargs.get("scope")

    def __repr__(self) -> str:
        string = (
            f"KeyVaultRoleAssignmentProperties(principal_id={self.principal_id}, "
            + f"role_definition_id={self.role_definition_id}, scope={self.scope})"
        )
        return string[:1024]

    @classmethod
    def _from_generated(
        cls, role_assignment_properties: Union[RoleAssignmentProperties, RoleAssignmentPropertiesWithScope]
    ) -> "KeyVaultRoleAssignmentProperties":
        # the generated RoleAssignmentProperties and RoleAssignmentPropertiesWithScope
        # models differ only in that the latter has a "scope" attribute
        return cls(
            principal_id=role_assignment_properties.principal_id,
            role_definition_id=role_assignment_properties.role_definition_id,
            scope=getattr(role_assignment_properties, "scope", None),
        )


class KeyVaultRoleDefinition(object):
    """The definition of a role over one or more scopes

    :ivar list[str] assignable_scopes: scopes the role can be assigned over
    :ivar str description: description of the role definition
    :ivar str id: unique identifier for this role definition
    :ivar str name: the role definition's name
    :ivar list[KeyVaultPermission] permissions: permissions defined for the role
    :ivar str role_name: the role's name
    :ivar str role_type: type of the role
    :ivar str type: type of the role definition
    """

    def __init__(self, **kwargs: Any) -> None:
        self.assignable_scopes = kwargs.get("assignable_scopes")
        self.description = kwargs.get("description")
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.permissions = kwargs.get("permissions")
        self.role_name = kwargs.get("role_name")
        self.role_type = kwargs.get("role_type")
        self.type = kwargs.get("type")

    def __repr__(self) -> str:
        return f"KeyVaultRoleDefinition<{self.id}>"

    @classmethod
    def _from_generated(cls, definition: RoleDefinition) -> "KeyVaultRoleDefinition":
        # pylint:disable=protected-access
        return cls(
            assignable_scopes=definition.properties.assignable_scopes if definition.properties else None,
            description=definition.properties.description if definition.properties else None,
            id=definition.id,
            name=definition.name,
            permissions=(
                [KeyVaultPermission._from_generated(p) for p in definition.properties.permissions or []]
                if definition.properties
                else None
            ),
            role_name=definition.properties.role_name if definition.properties else None,
            role_type=definition.properties.role_type if definition.properties else None,
            type=definition.type,
        )


class KeyVaultBackupResult(object):
    """A Key Vault full backup operation result

    :ivar str folder_url: URL of the Azure Blob Storage container containing the backup
    """

    # pylint:disable=unused-argument

    def __init__(self, **kwargs: Any) -> None:
        self.folder_url: Optional[str] = kwargs.get("folder_url")

    @classmethod
    def _from_generated(
        cls, response: HttpResponse, deserialized_operation: FullBackupOperation, response_headers: Dict
    ) -> "KeyVaultBackupResult":
        return cls(folder_url=deserialized_operation.azure_storage_blob_container_uri)


class KeyVaultSetting(object):
    """A Key Vault setting.

    :ivar str name: The name of the account setting.
    :ivar str value: The value of the account setting.
    :ivar setting_type: The type specifier of the value.
    :vartype setting_type: str or KeyVaultSettingType or None

    :param str name: The name of the account setting.
    :param str value: The value of the account setting.
    :param setting_type: The type specifier of the value.
    :type setting_type: str or KeyVaultSettingType or None
    """

    def __init__(
        self,
        name: str,
        value: Union[str, bool],
        setting_type: Optional[Union[str, KeyVaultSettingType]] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        self.name = name
        self.value = value if isinstance(value, str) else str(value)  # `value` is stored as a string
        if setting_type == KeyVaultSettingType.BOOLEAN:
            self.setting_type: Optional[Union[str, KeyVaultSettingType]] = KeyVaultSettingType.BOOLEAN
        else:
            self.setting_type = setting_type.lower() if isinstance(setting_type, str) else setting_type

        # If a setting type isn't provided, set it based on `value`'s type (without inferring from the value itself)
        if self.setting_type is None:
            if isinstance(value, bool):
                self.setting_type = KeyVaultSettingType.BOOLEAN

        # If the setting is a boolean, lower-case the string for serialization
        if self.setting_type == KeyVaultSettingType.BOOLEAN:
            self.value = self.value.lower()

    def getboolean(self) -> bool:
        """Gets the account setting value as a boolean if the ``setting_type`` is ``KeyVaultSettingType.BOOLEAN``.

        :returns: The account setting value as a boolean.
        :rtype: bool

        :raises ValueError: if the ``setting_type`` is not boolean or the value cannot be represented as a boolean.
        """
        if self.setting_type == KeyVaultSettingType.BOOLEAN:
            if self.value == "true":
                return True
            if self.value == "false":
                return False
        raise ValueError(
            'The `setting_type` of the setting must be `KeyVaultSettingType.BOOLEAN` and the `value` must be "true" '
            'or "false" in order to use `getboolean`.'
        )

    @classmethod
    def _from_generated(cls, setting: Setting) -> "KeyVaultSetting":
        setting_type = KeyVaultSettingType.BOOLEAN if setting.type == "boolean" else setting.type
        return cls(name=setting.name, value=setting.value, setting_type=setting_type)


class KeyVaultEkmConnection(object):
    """An External Key Manager (EKM) connection.

    :param str host: EKM proxy FQDN (Fully Qualified Domain Name). Only allowed characters are
        ``a-z``, ``A-Z``, ``0-9``, hyphen (``-``), dot (``.``), and colon (``:``).
    :param server_ca_certificates: The root CA certificate chain that issued the proxy server's
        certificate. An array of certificates in the certificate chain, each in DER format and
        base64 encoded.
    :type server_ca_certificates: list[bytes]

    :keyword str path_prefix: Optional path prefix for the EKM proxy (if any).
    :keyword str server_subject_common_name: The subject common name of the server certificate of
        the EKM proxy.
    :keyword connectivity_mode: The connectivity mode used to reach the EKM proxy. Defaults to
        ``KeyVaultEkmConnectivityMode.PUBLIC``. When set to
        ``KeyVaultEkmConnectivityMode.PRIVATE_ENDPOINT``, ``host`` is the name of an EKM proxy
        private endpoint instead of a DNS name or IP address.
    :paramtype connectivity_mode: str or ~azure.keyvault.administration.KeyVaultEkmConnectivityMode or None

    :ivar str host: EKM proxy FQDN.
    :ivar list[bytes] server_ca_certificates: The root CA certificate chain that issued the proxy
        server's certificate.
    :ivar path_prefix: Optional path prefix for the EKM proxy (if any).
    :vartype path_prefix: str or None
    :ivar server_subject_common_name: The subject common name of the server certificate of the EKM
        proxy.
    :vartype server_subject_common_name: str or None
    :ivar connectivity_mode: The connectivity mode used to reach the EKM proxy.
    :vartype connectivity_mode: str or ~azure.keyvault.administration.KeyVaultEkmConnectivityMode or None
    """

    def __init__(
        self,
        host: str,
        server_ca_certificates: List[bytes],
        *,
        path_prefix: Optional[str] = None,
        server_subject_common_name: Optional[str] = None,
        connectivity_mode: Optional[Union[str, KeyVaultEkmConnectivityMode]] = None,
    ) -> None:
        self.host = host
        self.server_ca_certificates = server_ca_certificates
        self.path_prefix = path_prefix
        self.server_subject_common_name = server_subject_common_name
        self.connectivity_mode = connectivity_mode

    def __repr__(self) -> str:
        return f"KeyVaultEkmConnection<{self.host}>"

    @classmethod
    def _from_generated(cls, connection: EkmConnection) -> "KeyVaultEkmConnection":
        return cls(
            host=connection.host,
            server_ca_certificates=connection.server_ca_certificates,
            path_prefix=connection.path_prefix,
            server_subject_common_name=connection.server_subject_common_name,
            connectivity_mode=connection.connectivity_mode,
        )

    def _to_generated(self) -> EkmConnection:
        return EkmConnection(
            host=self.host,
            server_ca_certificates=self.server_ca_certificates,
            path_prefix=self.path_prefix,
            server_subject_common_name=self.server_subject_common_name,
            connectivity_mode=self.connectivity_mode,
        )


class KeyVaultEkmProxyClientCertificateInfo(object):
    """EKM proxy client certificate information.

    :ivar ca_certificates: The client root CA certificate chain to authenticate to the EKM proxy.
        An array of certificates in the certificate chain, each in DER format and base64 encoded.
    :vartype ca_certificates: list[bytes] or None
    :ivar subject_common_name: The subject common name of the client certificate used to
        authenticate to the EKM proxy.
    :vartype subject_common_name: str or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.ca_certificates: Optional[List[bytes]] = kwargs.get("ca_certificates")
        self.subject_common_name: Optional[str] = kwargs.get("subject_common_name")

    def __repr__(self) -> str:
        return f"KeyVaultEkmProxyClientCertificateInfo<{self.subject_common_name}>"

    @classmethod
    def _from_generated(
        cls, certificate_info: EkmProxyClientCertificateInfo
    ) -> "KeyVaultEkmProxyClientCertificateInfo":
        return cls(
            ca_certificates=certificate_info.ca_certificates,
            subject_common_name=certificate_info.subject_common_name,
        )


class KeyVaultEkmProxyInfo(object):
    """EKM proxy information returned when checking an EKM connection.

    :ivar api_version: The highest version of proxy interface API supported by the EKM proxy.
    :vartype api_version: str or None
    :ivar proxy_vendor: The name of the proxy vendor.
    :vartype proxy_vendor: str or None
    :ivar proxy_name: The name of the proxy product and its version.
    :vartype proxy_name: str or None
    :ivar ekm_vendor: The name of the EKM vendor.
    :vartype ekm_vendor: str or None
    :ivar ekm_product: The name of the EKM product and its version.
    :vartype ekm_product: str or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.api_version: Optional[str] = kwargs.get("api_version")
        self.proxy_vendor: Optional[str] = kwargs.get("proxy_vendor")
        self.proxy_name: Optional[str] = kwargs.get("proxy_name")
        self.ekm_vendor: Optional[str] = kwargs.get("ekm_vendor")
        self.ekm_product: Optional[str] = kwargs.get("ekm_product")

    def __repr__(self) -> str:
        return (
            f"KeyVaultEkmProxyInfo(api_version={self.api_version}, "
            f"proxy_vendor={self.proxy_vendor}, proxy_name={self.proxy_name}, "
            f"ekm_vendor={self.ekm_vendor}, ekm_product={self.ekm_product})"
        )

    @classmethod
    def _from_generated(cls, proxy_info: EkmProxyInfo) -> "KeyVaultEkmProxyInfo":
        return cls(
            api_version=proxy_info.api_version,
            proxy_vendor=proxy_info.proxy_vendor,
            proxy_name=proxy_info.proxy_name,
            ekm_vendor=proxy_info.ekm_vendor,
            ekm_product=proxy_info.ekm_product,
        )


class KeyVaultEkmPrivateEndpointProperties(object):
    """The properties of an EKM proxy private endpoint.

    :ivar private_link_service_id: Alias of the Private Link Service that the private endpoint connects to.
    :vartype private_link_service_id: str or None
    :ivar private_link_service_connection_name: The name of the private link service connection, generated by the
        service.
    :vartype private_link_service_connection_name: str or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.private_link_service_id: Optional[str] = kwargs.get("private_link_service_id")
        self.private_link_service_connection_name: Optional[str] = kwargs.get("private_link_service_connection_name")

    def __repr__(self) -> str:
        return f"KeyVaultEkmPrivateEndpointProperties<{self.private_link_service_id}>"

    @classmethod
    def _from_generated(cls, properties: EkmPrivateEndpointProperties) -> "KeyVaultEkmPrivateEndpointProperties":
        return cls(
            private_link_service_id=properties.private_link_service_id,
            private_link_service_connection_name=properties.private_link_service_connection_name,
        )


class KeyVaultEkmPrivateEndpointConnectionState(object):  # pylint:disable=name-too-long
    """The state of the connection between an EKM proxy private endpoint and the Private Link Service.

    :ivar status: The status of the private link service connection.
    :vartype status: str or ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointConnectionStatus or None
    :ivar description: A description of the current connection state.
    :vartype description: str or None
    :ivar actions_required: Any actions required from the customer to maintain the connection.
    :vartype actions_required: str or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.status: Optional[Union[str, KeyVaultEkmPrivateEndpointConnectionStatus]] = kwargs.get("status")
        self.description: Optional[str] = kwargs.get("description")
        self.actions_required: Optional[str] = kwargs.get("actions_required")

    def __repr__(self) -> str:
        return f"KeyVaultEkmPrivateEndpointConnectionState<{self.status}>"

    @classmethod
    def _from_generated(
        cls, connection_state: EkmPrivateEndpointConnectionState
    ) -> "KeyVaultEkmPrivateEndpointConnectionState":
        return cls(
            status=connection_state.status,
            description=connection_state.description,
            actions_required=connection_state.actions_required,
        )


class KeyVaultEkmPrivateEndpoint(object):
    """An EKM proxy private endpoint.

    :ivar name: The name of the private endpoint.
    :vartype name: str or None
    :ivar location: The Azure region where the private endpoint is provisioned.
    :vartype location: str or None
    :ivar provisioning_state: The provisioning state of the private endpoint.
    :vartype provisioning_state: str or
        ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointProvisioningState or None
    :ivar properties: The properties of the private endpoint.
    :vartype properties: ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointProperties or None
    :ivar private_link_service_connection_state: The state of the connection between the private endpoint and the
        Private Link Service.
    :vartype private_link_service_connection_state:
        ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointConnectionState or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.name: Optional[str] = kwargs.get("name")
        self.location: Optional[str] = kwargs.get("location")
        self.provisioning_state: Optional[Union[str, KeyVaultEkmPrivateEndpointProvisioningState]] = kwargs.get(
            "provisioning_state"
        )
        self.properties: Optional[KeyVaultEkmPrivateEndpointProperties] = kwargs.get("properties")
        self.private_link_service_connection_state: Optional[KeyVaultEkmPrivateEndpointConnectionState] = kwargs.get(
            "private_link_service_connection_state"
        )

    def __repr__(self) -> str:
        return f"KeyVaultEkmPrivateEndpoint<{self.name}>"

    @classmethod
    def _from_generated(cls, private_endpoint: EkmPrivateEndpoint) -> "KeyVaultEkmPrivateEndpoint":
        # pylint:disable=protected-access
        return cls(
            name=private_endpoint.name,
            location=private_endpoint.location,
            provisioning_state=private_endpoint.provisioning_state,
            properties=(
                KeyVaultEkmPrivateEndpointProperties._from_generated(private_endpoint.properties)
                if private_endpoint.properties
                else None
            ),
            private_link_service_connection_state=(
                KeyVaultEkmPrivateEndpointConnectionState._from_generated(
                    private_endpoint.private_link_service_connection_state
                )
                if private_endpoint.private_link_service_connection_state
                else None
            ),
        )


class KeyVaultEkmPrivateEndpointOperation(object):
    """A long-running operation on an EKM proxy private endpoint.

    :ivar job_id: Identifier for the private endpoint operation.
    :vartype job_id: str or None
    :ivar private_endpoint_name: The name of the private endpoint the operation applies to.
    :vartype private_endpoint_name: str or None
    :ivar operation_type: The type of the operation.
    :vartype operation_type: str or ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointOperationType or None
    :ivar status: The status of the operation.
    :vartype status: str or ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointOperationStatus or None
    :ivar status_details: The status details of the operation.
    :vartype status_details: str or None
    :ivar start_time: The start time of the operation, in UTC.
    :vartype start_time: ~datetime.datetime or None
    :ivar end_time: The end time of the operation, in UTC.
    :vartype end_time: ~datetime.datetime or None
    :ivar error_code: The code of the error encountered, if any, during the operation.
    :vartype error_code: str or None
    :ivar error_message: The message of the error encountered, if any, during the operation.
    :vartype error_message: str or None
    """

    # pylint:disable=unused-argument

    def __init__(self, **kwargs: Any) -> None:
        self.job_id: Optional[str] = kwargs.get("job_id")
        self.private_endpoint_name: Optional[str] = kwargs.get("private_endpoint_name")
        self.operation_type: Optional[Union[str, KeyVaultEkmPrivateEndpointOperationType]] = kwargs.get(
            "operation_type"
        )
        self.status: Optional[Union[str, KeyVaultEkmPrivateEndpointOperationStatus]] = kwargs.get("status")
        self.status_details: Optional[str] = kwargs.get("status_details")
        self.start_time: Optional[datetime] = kwargs.get("start_time")
        self.end_time: Optional[datetime] = kwargs.get("end_time")
        self.error_code: Optional[str] = kwargs.get("error_code")
        self.error_message: Optional[str] = kwargs.get("error_message")

    def __repr__(self) -> str:
        return f"KeyVaultEkmPrivateEndpointOperation<{self.private_endpoint_name}>"

    @classmethod
    def _from_generated(cls, operation: EkmPrivateEndpointOperation) -> "KeyVaultEkmPrivateEndpointOperation":
        return cls(
            job_id=operation.job_id,
            private_endpoint_name=operation.private_endpoint_name,
            operation_type=operation.operation_type,
            status=operation.status,
            status_details=operation.status_details,
            start_time=operation.start_time,
            end_time=operation.end_time,
            error_code=operation.error.code if operation.error else None,
            error_message=operation.error.message if operation.error else None,
        )

    @classmethod
    def _from_polling_result(
        cls, response: HttpResponse, deserialized_operation: EkmPrivateEndpointOperation, response_headers: Dict
    ) -> "KeyVaultEkmPrivateEndpointOperation":
        return cls._from_generated(deserialized_operation)
