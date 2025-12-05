from typing import TYPE_CHECKING, Any, Optional, List, Dict, Union, cast
try:
    from typing import TypedDict, NotRequired  # Python 3.11+
except ImportError:
    from typing_extensions import TypedDict, NotRequired  # Python 3.8-3.10

from azure.core.rest import HttpResponse
from .service_factory import ServiceProviderFactory

if TYPE_CHECKING:
    from .._client import ManagementClient

# TypedDict models based on azure-mgmt-appconfiguration

class ApiKey(TypedDict, total=False):
    """An API key used for authenticating with a configuration store endpoint."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    value: NotRequired[str]  # readonly
    connection_string: NotRequired[str]  # readonly
    last_modified: NotRequired[str]  # readonly, ISO-8601 datetime
    read_only: NotRequired[bool]  # readonly

class ApiKeyListResult(TypedDict, total=False):
    """The result of a request to list API keys."""
    value: NotRequired[List[ApiKey]]
    next_link: NotRequired[str]

class Sku(TypedDict):
    """The SKU of the configuration store."""
    name: str  # Required. Known values: "Free", "Standard", "Premium"

class UserIdentity(TypedDict, total=False):
    """User assigned identity properties."""
    principal_id: NotRequired[str]  # readonly
    client_id: NotRequired[str]  # readonly

class ResourceIdentity(TypedDict, total=False):
    """The managed identity information for the configuration store."""
    type: NotRequired[str]  # Known values: "None", "SystemAssigned", "UserAssigned", "SystemAssigned, UserAssigned"
    user_assigned_identities: NotRequired[Dict[str, UserIdentity]]
    principal_id: NotRequired[str]  # readonly
    tenant_id: NotRequired[str]  # readonly

class KeyVaultProperties(TypedDict, total=False):
    """Settings concerning key vault encryption for a configuration store."""
    key_identifier: NotRequired[str]
    identity_client_id: NotRequired[str]

class EncryptionProperties(TypedDict, total=False):
    """The encryption settings of the configuration store."""
    key_vault_properties: NotRequired[KeyVaultProperties]

class SystemData(TypedDict, total=False):
    """Resource system metadata."""
    created_by: NotRequired[str]
    created_by_type: NotRequired[str]
    created_at: NotRequired[str]  # ISO-8601 datetime
    last_modified_by: NotRequired[str]
    last_modified_by_type: NotRequired[str]
    last_modified_at: NotRequired[str]  # ISO-8601 datetime

class PrivateEndpointConnectionReference(TypedDict, total=False):
    """A reference to a related private endpoint connection."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    provisioning_state: NotRequired[str]  # readonly

class DataPlaneProxyProperties(TypedDict, total=False):
    """Property specifying the configuration of data plane proxy for Azure Resource Manager (ARM)."""
    authentication_mode: NotRequired[str]  # Known values: "Pass", "Local"
    private_link_resource_id: NotRequired[str]

class ConfigurationStore(TypedDict):
    """The configuration store along with all resource properties."""
    # Required fields
    location: str
    sku: Sku
    
    # Optional fields
    tags: NotRequired[Dict[str, str]]
    identity: NotRequired[ResourceIdentity]
    
    # Properties (optional)
    encryption: NotRequired[EncryptionProperties]
    public_network_access: NotRequired[str]  # Known values: "Enabled", "Disabled"
    disable_local_auth: NotRequired[bool]
    soft_delete_retention_in_days: NotRequired[int]
    default_key_value_revision_retention_period_in_seconds: NotRequired[int]
    enable_purge_protection: NotRequired[bool]
    data_plane_proxy: NotRequired[DataPlaneProxyProperties]
    create_mode: NotRequired[str]  # Known values: "Recover", "Default"
    
    # Readonly fields
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    system_data: NotRequired[SystemData]  # readonly
    provisioning_state: NotRequired[str]  # readonly
    creation_date: NotRequired[str]  # readonly, ISO-8601 datetime
    endpoint: NotRequired[str]  # readonly
    private_endpoint_connections: NotRequired[List[PrivateEndpointConnectionReference]]  # readonly

class ConfigurationStoreListResult(TypedDict, total=False):
    """The result of a request to list configuration stores."""
    value: NotRequired[List[ConfigurationStore]]
    next_link: NotRequired[str]

class ConfigurationStoreUpdateParameters(TypedDict, total=False):
    """The parameters for updating a configuration store."""
    identity: NotRequired[ResourceIdentity]
    sku: NotRequired[Sku]
    tags: NotRequired[Dict[str, str]]
    encryption: NotRequired[EncryptionProperties]
    disable_local_auth: NotRequired[bool]
    public_network_access: NotRequired[str]  # Known values: "Enabled", "Disabled"
    enable_purge_protection: NotRequired[bool]
    data_plane_proxy: NotRequired[DataPlaneProxyProperties]
    default_key_value_revision_retention_period_in_seconds: NotRequired[int]

class DeletedConfigurationStore(TypedDict, total=False):
    """The deleted configuration store."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    tags: NotRequired[Dict[str, str]]
    location: NotRequired[str]
    configuration_store_id: NotRequired[str]  # readonly
    scheduled_purge_date: NotRequired[str]  # readonly, ISO-8601 datetime
    deletion_date: NotRequired[str]  # readonly, ISO-8601 datetime
    purge_protection_enabled: NotRequired[bool]  # readonly

class DeletedConfigurationStoreListResult(TypedDict, total=False):
    """The result of a request to list deleted configuration stores."""
    value: NotRequired[List[DeletedConfigurationStore]]
    next_link: NotRequired[str]

class PrivateEndpoint(TypedDict, total=False):
    """Private endpoint which the connection belongs to."""
    id: NotRequired[str]

class PrivateLinkServiceConnectionState(TypedDict, total=False):
    """Connection State of the Private Endpoint Connection."""
    status: NotRequired[str]  # Known values: "Pending", "Approved", "Rejected"
    description: NotRequired[str]
    actions_required: NotRequired[str]

class PrivateEndpointConnection(TypedDict, total=False):
    """A private endpoint connection to the configuration store."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    private_endpoint: NotRequired[PrivateEndpoint]
    group_ids: NotRequired[List[str]]
    private_link_service_connection_state: NotRequired[PrivateLinkServiceConnectionState]
    provisioning_state: NotRequired[str]  # readonly

class PrivateEndpointConnectionListResult(TypedDict, total=False):
    """The result of a request to list private endpoint connections."""
    value: NotRequired[List[PrivateEndpointConnection]]
    next_link: NotRequired[str]

class PrivateLinkResource(TypedDict, total=False):
    """A resource that supports private link capabilities."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    group_id: NotRequired[str]  # readonly
    required_members: NotRequired[List[str]]  # readonly
    required_zone_names: NotRequired[List[str]]

class PrivateLinkResourceListResult(TypedDict, total=False):
    """The result of a request to list private link resources."""
    value: NotRequired[List[PrivateLinkResource]]
    next_link: NotRequired[str]

class KeyValue(TypedDict, total=False):
    """The key-value resource along with all resource properties."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    key: NotRequired[str]  # readonly
    label: NotRequired[str]  # readonly
    value: NotRequired[str]
    content_type: NotRequired[str]
    e_tag: NotRequired[str]  # readonly
    last_modified: NotRequired[str]  # readonly, ISO-8601 datetime
    locked: NotRequired[bool]  # readonly
    tags: NotRequired[Dict[str, str]]

class KeyValueFilter(TypedDict):
    """Enables filtering of key-values."""
    key: str  # Required
    label: NotRequired[str]

class KeyValueListResult(TypedDict, total=False):
    """The result of a request to list key-values."""
    value: NotRequired[List[KeyValue]]
    next_link: NotRequired[str]

class Snapshot(TypedDict, total=False):
    """The snapshot resource."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    provisioning_state: NotRequired[str]  # readonly
    status: NotRequired[str]  # readonly
    filters: NotRequired[List[KeyValueFilter]]
    composition_type: NotRequired[str]  # Known values: "key", "key_label"
    created: NotRequired[str]  # readonly, ISO-8601 datetime
    expires: NotRequired[str]  # ISO-8601 datetime
    retention_period: NotRequired[int]
    size: NotRequired[int]  # readonly
    items_count: NotRequired[int]  # readonly
    tags: NotRequired[Dict[str, str]]
    e_tag: NotRequired[str]  # readonly

class Replica(TypedDict, total=False):
    """The replica resource."""
    id: NotRequired[str]  # readonly
    name: NotRequired[str]  # readonly
    type: NotRequired[str]  # readonly
    location: NotRequired[str]
    system_data: NotRequired[SystemData]  # readonly
    endpoint: NotRequired[str]  # readonly
    provisioning_state: NotRequired[str]  # readonly

class ReplicaListResult(TypedDict, total=False):
    """The result of a request to list replicas."""
    value: NotRequired[List[Replica]]
    next_link: NotRequired[str]

class RegenerateKeyParameters(TypedDict, total=False):
    """The parameters used to regenerate an API key."""
    id: NotRequired[str]

class CheckNameAvailabilityParameters(TypedDict):
    """Parameters used for checking whether a resource name is available."""
    name: str  # Required
    type: str  # Required. Should be "Microsoft.AppConfiguration/configurationStores"

class NameAvailabilityStatus(TypedDict, total=False):
    """The result of a request to check the availability of a resource name."""
    name_available: NotRequired[bool]
    reason: NotRequired[str]  # Known values: "Invalid", "AlreadyExists"
    message: NotRequired[str]

class ErrorAdditionalInfo(TypedDict, total=False):
    """The resource management error additional info."""
    type: NotRequired[str]  # readonly
    info: NotRequired[Any]  # readonly

class ErrorDetail(TypedDict, total=False):
    """The error detail."""
    code: NotRequired[str]  # readonly
    message: NotRequired[str]  # readonly
    target: NotRequired[str]  # readonly
    details: NotRequired[List["ErrorDetail"]]  # readonly
    additional_info: NotRequired[List[ErrorAdditionalInfo]]  # readonly

class ErrorDetails(TypedDict, total=False):
    """The error response containing error details."""
    code: NotRequired[str]  # readonly
    message: NotRequired[str]  # readonly
    additional_info: NotRequired[List[ErrorAdditionalInfo]]  # readonly

class ErrorResponse(TypedDict, total=False):
    """Common error response for all Azure Resource Manager APIs."""
    error: NotRequired[ErrorDetail]

class ErrorResponseAutoGenerated(TypedDict, total=False):
    """Common error response for all Azure Resource Manager APIs."""
    error: NotRequired[ErrorDetail]

class LogSpecification(TypedDict, total=False):
    """Specifications of the Log for Azure Monitoring."""
    name: NotRequired[str]
    display_name: NotRequired[str]
    blob_duration: NotRequired[str]

class MetricDimension(TypedDict, total=False):
    """Specifications of the Dimension of metrics."""
    name: NotRequired[str]
    display_name: NotRequired[str]
    internal_name: NotRequired[str]
    to_be_exported_for_shoebox: NotRequired[bool]

class MetricSpecification(TypedDict, total=False):
    """Specifications of the Metrics for Azure Monitoring."""
    name: NotRequired[str]
    display_name: NotRequired[str]
    display_description: NotRequired[str]
    unit: NotRequired[str]
    aggregation_type: NotRequired[str]
    internal_metric_name: NotRequired[str]
    dimensions: NotRequired[List[MetricDimension]]
    fill_gap_with_zero: NotRequired[bool]

class ServiceSpecification(TypedDict, total=False):
    """Service specification payload."""
    log_specifications: NotRequired[List[LogSpecification]]
    metric_specifications: NotRequired[List[MetricSpecification]]

class OperationProperties(TypedDict, total=False):
    """Extra Operation properties."""
    service_specification: NotRequired[ServiceSpecification]

class OperationDefinitionDisplay(TypedDict, total=False):
    """The display information for a configuration store operation."""
    provider: NotRequired[str]
    resource: NotRequired[str]
    operation: NotRequired[str]
    description: NotRequired[str]

class OperationDefinition(TypedDict, total=False):
    """The definition of a configuration store operation."""
    name: NotRequired[str]
    is_data_action: NotRequired[bool]
    display: NotRequired[OperationDefinitionDisplay]
    origin: NotRequired[str]
    properties: NotRequired[OperationProperties]

class OperationDefinitionListResult(TypedDict, total=False):
    """The result of a request to list configuration store operations."""
    value: NotRequired[List[OperationDefinition]]
    next_link: NotRequired[str]

class Resource(TypedDict):
    id: NotRequired[str]
    name: NotRequired[str]
    type: NotRequired[str]

class TrackedResource(Resource):
    location: str
    tags: NotRequired[Dict[str, str]]



class AppConfigurationFactory(ServiceProviderFactory):
    """Factory for Microsoft.AppConfiguration service provider."""

    def __init__(self, client: "ManagementClient", subscription_id: Optional[str] = None):
        super().__init__(client, "Microsoft.AppConfiguration", subscription_id)

    # Configuration Stores Operations

    def list(self, skip_token: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List all configuration stores in the subscription."""
        return self.get("configurationStores", skip_token=skip_token, **kwargs)



    def configuration_stores(self, resource_group: str, config_store_name: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List configuration stores or get a specific configuration store."""
        return self.get_resource("configurationStores", config_store_name, resource_group, **kwargs)

    def create_configuration_store(self, resource_group: str, config_store_name: str, 
                                 config_store_data: ConfigurationStore, **kwargs: Any) -> HttpResponse:
        """Create a configuration store."""
        return self.create_resource("configurationStores", config_store_name, cast(Dict[str, Any], config_store_data), resource_group, **kwargs)

    def update_configuration_store(self, resource_group: str, config_store_name: str, 
                                 update_data: ConfigurationStoreUpdateParameters, **kwargs: Any) -> HttpResponse:
        """Update a configuration store."""
        return self.update_resource("configurationStores", config_store_name, cast(Dict[str, Any], update_data), resource_group, **kwargs)

    def delete_configuration_store(self, resource_group: str, config_store_name: str, **kwargs: Any) -> HttpResponse:
        """Delete a configuration store."""
        return self.delete_resource("configurationStores", config_store_name, resource_group, **kwargs)

    def list_configuration_stores_by_subscription(self, **kwargs: Any) -> HttpResponse:
        """List all configuration stores in the subscription."""
        return self.get("configurationStores", **kwargs)

    # Deleted Configuration Stores Operations
    def deleted_configuration_stores(self, **kwargs: Any) -> HttpResponse:
        """List deleted configuration stores."""
        return self.get("deletedConfigurationStores", **kwargs)

    def get_deleted_configuration_store(self, location: str, config_store_name: str, **kwargs: Any) -> HttpResponse:
        """Get a specific deleted configuration store."""
        url = f"/subscriptions/{self.subscription_id}/providers/Microsoft.AppConfiguration/locations/{location}/deletedConfigurationStores/{config_store_name}"
        return self.get(url, **kwargs)

    def purge_deleted_configuration_store(self, location: str, config_store_name: str, **kwargs: Any) -> HttpResponse:
        """Purge a deleted configuration store."""
        url = f"/subscriptions/{self.subscription_id}/providers/Microsoft.AppConfiguration/locations/{location}/deletedConfigurationStores/{config_store_name}/purge"
        return self.post(url, **kwargs)

    # API Keys Operations  
    def list_keys(self, resource_group: str, config_store_name: str, **kwargs: Any) -> HttpResponse:
        """List API keys for a configuration store."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/listKeys"
        return self.post(url, **kwargs)

    def regenerate_key(self, resource_group: str, config_store_name: str, key_data: RegenerateKeyParameters, **kwargs: Any) -> HttpResponse:
        """Regenerate an API key for a configuration store."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/regenerateKey"
        return self.post(url, model=cast(Dict[str, Any], key_data), **kwargs)

    # Key-Values Operations
    def key_values(self, resource_group: str, config_store_name: str, key_value_name: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List key-values or get a specific key-value."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/keyValues"
        if key_value_name:
            url += f"/{key_value_name}"
        return self.get(url, **kwargs)

    def create_or_update_key_value(self, resource_group: str, config_store_name: str, 
                                 key_value_name: str, key_value_data: KeyValue, **kwargs: Any) -> HttpResponse:
        """Create or update a key-value."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/keyValues/{key_value_name}"
        return self.put(url, model=cast(Dict[str, Any], key_value_data), **kwargs)

    def delete_key_value(self, resource_group: str, config_store_name: str, key_value_name: str, **kwargs: Any) -> HttpResponse:
        """Delete a key-value."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/keyValues/{key_value_name}"
        return self.delete(url, **kwargs)

    # Snapshots Operations
    def snapshots(self, resource_group: str, config_store_name: str, snapshot_name: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List snapshots or get a specific snapshot."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/snapshots"
        if snapshot_name:
            url += f"/{snapshot_name}"
        return self.get(url, **kwargs)

    def create_snapshot(self, resource_group: str, config_store_name: str, 
                       snapshot_name: str, snapshot_data: Snapshot, **kwargs: Any) -> HttpResponse:
        """Create a snapshot."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/snapshots/{snapshot_name}"
        return self.put(url, model=cast(Dict[str, Any], snapshot_data), **kwargs)

    def update_snapshot(self, resource_group: str, config_store_name: str, 
                       snapshot_name: str, snapshot_data: Snapshot, **kwargs: Any) -> HttpResponse:
        """Update a snapshot."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/snapshots/{snapshot_name}"
        return self.patch(url, model=cast(Dict[str, Any], snapshot_data), **kwargs)

    def archive_snapshot(self, resource_group: str, config_store_name: str, snapshot_name: str, **kwargs: Any) -> HttpResponse:
        """Archive a snapshot."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/snapshots/{snapshot_name}/archive"
        return self.post(url, **kwargs)

    def recover_snapshot(self, resource_group: str, config_store_name: str, snapshot_name: str, **kwargs: Any) -> HttpResponse:
        """Recover a snapshot."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/snapshots/{snapshot_name}/recover"
        return self.post(url, **kwargs)

    # Replicas Operations
    def replicas(self, resource_group: str, config_store_name: str, replica_name: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List replicas or get a specific replica."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/replicas"
        if replica_name:
            url += f"/{replica_name}"
        return self.get(url, **kwargs)

    def create_replica(self, resource_group: str, config_store_name: str, 
                      replica_name: str, replica_data: Replica, **kwargs: Any) -> HttpResponse:
        """Create a replica."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/replicas/{replica_name}"
        return self.put(url, model=cast(Dict[str, Any], replica_data), **kwargs)

    def delete_replica(self, resource_group: str, config_store_name: str, replica_name: str, **kwargs: Any) -> HttpResponse:
        """Delete a replica."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/replicas/{replica_name}"
        return self.delete(url, **kwargs)

    # Private Endpoint Connections Operations
    def private_endpoint_connections(self, resource_group: str, config_store_name: str, 
                                   connection_name: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List private endpoint connections or get a specific one."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/privateEndpointConnections"
        if connection_name:
            url += f"/{connection_name}"
        return self.get(url, **kwargs)

    def create_or_update_private_endpoint_connection(self, resource_group: str, config_store_name: str, 
                                                   connection_name: str, connection_data: PrivateEndpointConnection, 
                                                   **kwargs: Any) -> HttpResponse:
        """Create or update a private endpoint connection."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/privateEndpointConnections/{connection_name}"
        return self.put(url, model=cast(Dict[str, Any], connection_data), **kwargs)

    def delete_private_endpoint_connection(self, resource_group: str, config_store_name: str, 
                                         connection_name: str, **kwargs: Any) -> HttpResponse:
        """Delete a private endpoint connection."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/privateEndpointConnections/{connection_name}"
        return self.delete(url, **kwargs)

    # Private Link Resources Operations
    def private_link_resources(self, resource_group: str, config_store_name: str, 
                             group_name: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """List private link resources or get a specific one."""
        url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{config_store_name}/privateLinkResources"
        if group_name:
            url += f"/{group_name}"
        return self.get(url, **kwargs)

    # Name Availability Operations
    def check_name_availability(self, check_data: CheckNameAvailabilityParameters, **kwargs: Any) -> HttpResponse:
        """Check if a configuration store name is available."""
        url = f"/subscriptions/{self.subscription_id}/providers/Microsoft.AppConfiguration/checkNameAvailability"
        return self.post(url, model=cast(Dict[str, Any], check_data), **kwargs)

    # Operations
    def list_operations(self, **kwargs: Any) -> HttpResponse:
        """List available operations for the App Configuration resource provider."""
        return self.get("/providers/Microsoft.AppConfiguration/operations", **kwargs)
