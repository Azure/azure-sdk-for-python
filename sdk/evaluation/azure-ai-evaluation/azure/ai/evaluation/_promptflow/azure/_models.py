# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, Sequence, Union

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential


class BlobStoreInfo(NamedTuple):
    name: str
    account_name: str
    endpoint: str
    container_name: str
    credential: Union[AzureSasCredential, AzureNamedKeyCredential, None]


@dataclass(frozen=True)
class Sku:
    capacity: int # If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted.
    family: str # If the service has different generations of hardware, for the same SKU, then that can be captured here.
    name: str # The name of the SKU. Ex - P3. It is typically a letter+number code
    size: str # The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code.
    #tier: SkuTier # This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT.


class CreatedByType(Enum):
    # start with capital letters to match the API response
    APPLICATION = "Application"
    KEY = "Key"
    MANAGED_IDENTITY = "ManagedIdentity"
    USER = "User"


class ProvisioningState(Enum):
    # start with capital letters to match the API response
    UNKNOWN = "Unknown"
    CANCELED = "Canceled"
    CREATING = "Creating"
    DELETING = "Deleting"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    UPDATING = "Updating"


@dataclass(frozen=True)
class systemData:
    created_at: str                         # The timestamp of resource creation (UTC).
    created_by: str                         # The identity that created the resource.
    created_by_type: CreatedByType          # The type of identity that created the resource.
    last_modified_at: str                   # The timestamp of resource last modification (UTC)
    last_modified_by: str                   # The identity that last modified the resource.
    last_modified_by_type: CreatedByType    # The type of identity that last modified the resource.


@dataclass(frozen=True)
class WorkspaceHubConfig:
    additional_workspace_storage_accounts: Sequence[str]
    default_workspace_resource_group: str


@dataclass(frozen=True)
class WorkspaceInfo:
    @dataclass(frozen=True)
    class Properties:
        application_insights: str                          # ARM id of the application insights associated with this workspace.
        associated_workspaces: Sequence[str]
        container_registry: str                            # ARM id of the container registry associated with this workspace.
        description: str                                   # The description of this workspace.
        discovery_url: str                                 # Url for the discovery service to identify regional endpoints for machine learning experimentation services
        enable_data_isolation: bool
        #encryption: EncryptionProperty                    # The encryption settings of Azure ML workspace.
        #feature_store_settings: FeatureStoreSettings      # Settings for feature store type workspace.
        friendly_name: str                                 # The friendly name for this workspace. This name in mutable
        hub_resource_id: str
        image_build_compute: str                           # The compute name for image build
        key_vault: str                                     # ARM id of the key vault associated with this workspace. This cannot be changed once the workspace has been created
        #managed_network: ManagedNetworkSettings           # Managed Network settings for a machine learning workspace.
        ml_flow_tracking_uri: str                          # The URI associated with this workspace that machine learning flow must point at to set up tracking.
        #notebook_info: NotebookResourceInfo               # The notebook info of Azure ML workspace.
        primary_user_assigned_identity: str                # The user assigned identity resource id that represents the workspace identity.
        #private_endpoint_connections: PrivateEndpointConnection[] # The list of private endpoint connections in the workspace.
        private_link_count: int                            # Count of private connections in the workspace
        provisioning_state: ProvisioningState              # The current deployment state of workspace resource. The provisioningState is to indicate states for resource provisioning.
        #public_network_access: PublicNetworkAccess        # Whether requests from Public Network are allowed.
        #serverless_compute_settings: ServerlessComputeSettings # Settings for serverless compute created in the workspace
        #service_managed_resources_settings: ServiceManagedResourcesSettings # The service managed resource settings.
        service_provisioned_resource_group: str            # The name of the managed resource group created by workspace RP in customer subscription if the workspace is CMK workspace
        #shared_private_link_resources: SharedPrivateLinkResource[] # The list of shared private link resources in this workspace.
        storage_account: str                               # ARM id of the storage account associated with this workspace. This cannot be changed once the workspace has been created
        storage_hns_enabled: bool                          # If the storage associated with the workspace has hierarchical namespace(HNS) enabled.
        tenant_id: str                                     # The tenant id associated with this workspace.
        workspace_hub_config: WorkspaceHubConfig           # WorkspaceHub's configuration object.
        workspace_id: str                                  # The immutable id associated with this workspace.
        v1_legacy_mode: bool = False                       # Enabling v1_legacy_mode may prevent you from using features provided by the v2 API.
        allow_public_access_when_behind_vnet: bool = False # The flag to indicate whether to allow public access when behind VNet.
        hbi_workspace: bool = False                        # The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service

    id: str                             # Fully qualified resource ID for the resource. Ex - /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{resourceType}/{resourceName}
    #identity: ManagedServiceIdentity   # The identity of the resource.
    kind: str
    location: str                       # Specifies the location of the resource.
    name: str                           # The name of the resource
    properties: Properties
    sku: Sku                            # The sku of the workspace.
    system_data: systemData             # Azure Resource Manager metadata containing createdBy and modifiedBy information.
    #tags: Dict[str, Any]               # Contains resource tags defined as key/value pairs.
    type: str                           # The type of the resource. E.g. "Microsoft.Compute/virtualMachines" or "Microsoft.Storage/storageAccounts"
