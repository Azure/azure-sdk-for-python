# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=line-too-long

from typing import Dict, List, NamedTuple, Optional, Union
from msrest.serialization import Model
from azure.core.credentials import AzureSasCredential, TokenCredential


class BlobStoreInfo(NamedTuple):
    name: str
    account_name: str
    endpoint: str
    container_name: str
    credential: Optional[Union[AzureSasCredential, TokenCredential, str]]


class WorkspaceHubConfig(Model):
    """WorkspaceHub's configuration object."""

    _attribute_map = {
        "additional_workspace_storage_accounts": {"key": "additionalWorkspaceStorageAccounts", "type": "[str]"},
        "default_workspace_resource_group": {"key": "defaultWorkspaceResourceGroup", "type": "str"},
    }

    def __init__(
        self,
        *,
        additional_workspace_storage_accounts: Optional[List[str]] = None,
        default_workspace_resource_group: Optional[str] = None,
        **kwargs
    ):
        super(WorkspaceHubConfig, self).__init__(**kwargs)
        self.additional_workspace_storage_accounts = additional_workspace_storage_accounts
        self.default_workspace_resource_group = default_workspace_resource_group


class Workspace(Model):
    """An object that represents a machine learning workspace.

    Variables are only populated by the server, and will be ignored when sending a request."""

    _validation = {
        "id": {"readonly": True},
        "name": {"readonly": True},
        "type": {"readonly": True},
        #'system_data': {'readonly': True},
        "agents_endpoint_uri": {"readonly": True},
        "ml_flow_tracking_uri": {"readonly": True},
        #'notebook_info': {'readonly': True},
        "private_endpoint_connections": {"readonly": True},
        #'private_link_count': {'readonly': True},
        "provisioning_state": {"readonly": True},
        "service_provisioned_resource_group": {"readonly": True},
        "storage_hns_enabled": {"readonly": True},
        "tenant_id": {"readonly": True},
        "workspace_id": {"readonly": True},
    }

    _attribute_map = {
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "type": {"key": "type", "type": "str"},
        #'system_data': {'key': 'systemData', 'type': 'SystemData'},
        #'identity': {'key': 'identity', 'type': 'ManagedServiceIdentity'},
        "kind": {"key": "kind", "type": "str"},
        "location": {"key": "location", "type": "str"},
        #'sku': {'key': 'sku', 'type': 'Sku'},
        "tags": {"key": "tags", "type": "{str}"},
        "agents_endpoint_uri": {"key": "properties.agentsEndpointUri", "type": "str"},
        "allow_public_access_when_behind_vnet": {"key": "properties.allowPublicAccessWhenBehindVnet", "type": "bool"},
        "allow_role_assignment_on_rg": {"key": "properties.allowRoleAssignmentOnRG", "type": "bool"},
        "application_insights": {"key": "properties.applicationInsights", "type": "str"},
        "associated_workspaces": {"key": "properties.associatedWorkspaces", "type": "[str]"},
        "container_registries": {"key": "properties.containerRegistries", "type": "[str]"},
        "container_registry": {"key": "properties.containerRegistry", "type": "str"},
        "description": {"key": "properties.description", "type": "str"},
        "discovery_url": {"key": "properties.discoveryUrl", "type": "str"},
        "enable_data_isolation": {"key": "properties.enableDataIsolation", "type": "bool"},
        "enable_service_side_cmk_encryption": {"key": "properties.enableServiceSideCMKEncryption", "type": "bool"},
        "enable_simplified_cmk": {"key": "properties.enableSimplifiedCmk", "type": "bool"},
        "enable_software_bill_of_materials": {"key": "properties.enableSoftwareBillOfMaterials", "type": "bool"},
        #'encryption': {'key': 'properties.encryption', 'type': 'EncryptionProperty'},
        "existing_workspaces": {"key": "properties.existingWorkspaces", "type": "[str]"},
        #'feature_store_settings': {'key': 'properties.featureStoreSettings', 'type': 'FeatureStoreSettings'},
        "friendly_name": {"key": "properties.friendlyName", "type": "str"},
        "hbi_workspace": {"key": "properties.hbiWorkspace", "type": "bool"},
        "hub_resource_id": {"key": "properties.hubResourceId", "type": "str"},
        "image_build_compute": {"key": "properties.imageBuildCompute", "type": "str"},
        "ip_allowlist": {"key": "properties.ipAllowlist", "type": "[str]"},
        "key_vault": {"key": "properties.keyVault", "type": "str"},
        "key_vaults": {"key": "properties.keyVaults", "type": "[str]"},
        #'managed_network': {'key': 'properties.managedNetwork', 'type': 'ManagedNetworkSettings'},
        "ml_flow_tracking_uri": {"key": "properties.mlFlowTrackingUri", "type": "str"},
        #'network_acls': {'key': 'properties.networkAcls', 'type': 'NetworkAcls'},
        #'notebook_info': {'key': 'properties.notebookInfo', 'type': 'NotebookResourceInfo'},
        "primary_user_assigned_identity": {"key": "properties.primaryUserAssignedIdentity", "type": "str"},
        "private_endpoint_connections": {
            "key": "properties.privateEndpointConnections",
            "type": "[PrivateEndpointConnection]",
        },
        "private_link_count": {"key": "properties.privateLinkCount", "type": "int"},
        "provision_network_now": {"key": "properties.provisionNetworkNow", "type": "bool"},
        "provisioning_state": {"key": "properties.provisioningState", "type": "str"},
        #'public_network_access': {'key': 'properties.publicNetworkAccess', 'type': 'str'},
        #'serverless_compute_settings': {'key': 'properties.serverlessComputeSettings', 'type': 'ServerlessComputeSettings'},
        #'service_managed_resources_settings': {'key': 'properties.serviceManagedResourcesSettings', 'type': 'ServiceManagedResourcesSettings'},
        "service_provisioned_resource_group": {"key": "properties.serviceProvisionedResourceGroup", "type": "str"},
        #'shared_private_link_resources': {'key': 'properties.sharedPrivateLinkResources', 'type': '[SharedPrivateLinkResource]'},
        "soft_delete_retention_in_days": {"key": "properties.softDeleteRetentionInDays", "type": "int"},
        "storage_account": {"key": "properties.storageAccount", "type": "str"},
        "storage_accounts": {"key": "properties.storageAccounts", "type": "[str]"},
        "storage_hns_enabled": {"key": "properties.storageHnsEnabled", "type": "bool"},
        #'system_datastores_auth_mode': {'key': 'properties.systemDatastoresAuthMode', 'type': 'str'},
        "tenant_id": {"key": "properties.tenantId", "type": "str"},
        "v1_legacy_mode": {"key": "properties.v1LegacyMode", "type": "bool"},
        "workspace_hub_config": {"key": "properties.workspaceHubConfig", "type": "WorkspaceHubConfig"},
        "workspace_id": {"key": "properties.workspaceId", "type": "str"},
    }

    def __init__(
        self,
        *,
        # system_data: Optional[SystemData] = None,
        # identity: Optional["ManagedServiceIdentity"] = None,
        kind: Optional[str] = None,
        location: Optional[str] = None,
        # sku: Optional["Sku"] = None,
        tags: Optional[Dict[str, str]] = None,
        allow_public_access_when_behind_vnet: Optional[bool] = None,
        allow_role_assignment_on_rg: Optional[bool] = None,
        application_insights: Optional[str] = None,
        associated_workspaces: Optional[List[str]] = None,
        container_registries: Optional[List[str]] = None,
        container_registry: Optional[str] = None,
        description: Optional[str] = None,
        discovery_url: Optional[str] = None,
        enable_data_isolation: Optional[bool] = None,
        enable_service_side_cmk_encryption: Optional[bool] = None,
        enable_simplified_cmk: Optional[bool] = None,
        enable_software_bill_of_materials: Optional[bool] = None,
        # encryption: Optional["EncryptionProperty"] = None,
        existing_workspaces: Optional[List[str]] = None,
        # feature_store_settings: Optional["FeatureStoreSettings"] = None,
        friendly_name: Optional[str] = None,
        hbi_workspace: Optional[bool] = None,
        hub_resource_id: Optional[str] = None,
        image_build_compute: Optional[str] = None,
        ip_allowlist: Optional[List[str]] = None,
        key_vault: Optional[str] = None,
        key_vaults: Optional[List[str]] = None,
        # managed_network: Optional["ManagedNetworkSettings"] = None,
        # network_acls: Optional["NetworkAcls"] = None,
        primary_user_assigned_identity: Optional[str] = None,
        provision_network_now: Optional[bool] = None,
        # public_network_access: Optional[Union[str, "PublicNetworkAccessType"]] = None,
        # serverless_compute_settings: Optional["ServerlessComputeSettings"] = None,
        # service_managed_resources_settings: Optional["ServiceManagedResourcesSettings"] = None,
        # shared_private_link_resources: Optional[List["SharedPrivateLinkResource"]] = None,
        soft_delete_retention_in_days: Optional[int] = None,
        storage_account: Optional[str] = None,
        storage_accounts: Optional[List[str]] = None,
        # system_datastores_auth_mode: Optional[Union[str, "SystemDatastoresAuthMode"]] = None,
        v1_legacy_mode: Optional[bool] = None,
        workspace_hub_config: Optional["WorkspaceHubConfig"] = None,
        **kwargs
    ):
        super(Workspace, self).__init__(**kwargs)
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.type: Optional[str] = None
        # self.system_data = system_data
        # self.identity = identity
        self.kind = kind
        self.location = location
        # self.sku = sku
        self.tags = tags
        self.agents_endpoint_uri = None
        self.allow_public_access_when_behind_vnet = allow_public_access_when_behind_vnet
        self.allow_role_assignment_on_rg = allow_role_assignment_on_rg
        self.application_insights = application_insights
        self.associated_workspaces = associated_workspaces
        self.container_registries = container_registries
        self.container_registry = container_registry
        self.description = description
        self.discovery_url = discovery_url
        self.enable_data_isolation = enable_data_isolation
        self.enable_service_side_cmk_encryption = enable_service_side_cmk_encryption
        self.enable_simplified_cmk = enable_simplified_cmk
        self.enable_software_bill_of_materials = enable_software_bill_of_materials
        # self.encryption = encryption
        self.existing_workspaces = existing_workspaces
        # self.feature_store_settings = feature_store_settings
        self.friendly_name = friendly_name
        self.hbi_workspace = hbi_workspace
        self.hub_resource_id = hub_resource_id
        self.image_build_compute = image_build_compute
        self.ip_allowlist = ip_allowlist
        self.key_vault = key_vault
        self.key_vaults = key_vaults
        # self.managed_network = managed_network
        self.ml_flow_tracking_uri = None
        # self.network_acls = network_acls
        # self.notebook_info = None
        self.primary_user_assigned_identity = primary_user_assigned_identity
        self.private_endpoint_connections = None
        self.private_link_count = None
        self.provision_network_now = provision_network_now
        self.provisioning_state = None
        # self.public_network_access = public_network_access
        # self.serverless_compute_settings = serverless_compute_settings
        # self.service_managed_resources_settings = service_managed_resources_settings
        self.service_provisioned_resource_group = None
        # self.shared_private_link_resources = shared_private_link_resources
        self.soft_delete_retention_in_days = soft_delete_retention_in_days
        self.storage_account = storage_account
        self.storage_accounts = storage_accounts
        self.storage_hns_enabled = None
        # self.system_datastores_auth_mode = system_datastores_auth_mode
        self.tenant_id = None
        self.v1_legacy_mode = v1_legacy_mode
        self.workspace_hub_config = workspace_hub_config
        self.workspace_id = None
