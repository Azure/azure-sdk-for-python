#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from azure.common import (
    AzureHttpError,
)
from ._common_models import (
    Feed,
    WindowsAzureData,
    _Base64String,
    _dict_of,
    _list_of,
    _scalar_list_of,
    _unicode_type,
    _xml_attribute,
)


class AzureAsyncOperationHttpError(AzureHttpError):

    '''Indicates that a batch operation failed'''

    def __init__(self, message, status_code, result):
        super(AzureAsyncOperationHttpError, self).__init__(message, status_code)
        self.result = result


class StorageServices(WindowsAzureData):

    def __init__(self):
        self.storage_services = _list_of(StorageService)

    def __iter__(self):
        return iter(self.storage_services)

    def __len__(self):
        return len(self.storage_services)

    def __getitem__(self, index):
        return self.storage_services[index]


class StorageService(WindowsAzureData):

    def __init__(self):
        self.url = ''
        self.service_name = ''
        self.storage_service_properties = StorageAccountProperties()
        self.storage_service_keys = StorageServiceKeys()
        self.extended_properties = _dict_of(
            'ExtendedProperty', 'Name', 'Value')
        self.capabilities = _scalar_list_of(_unicode_type, 'Capability')


class StorageAccountProperties(WindowsAzureData):

    def __init__(self):
        self.description = ''
        self.affinity_group = ''
        self.location = ''
        self.label = _Base64String()
        self.status = ''
        self.endpoints = _scalar_list_of(_unicode_type, 'Endpoint')
        self.geo_replication_enabled = False
        self.geo_primary_region = ''
        self.status_of_primary = ''
        self.geo_secondary_region = ''
        self.status_of_secondary = ''
        self.last_geo_failover_time = ''
        self.creation_time = ''
        self.account_type = ''


class StorageServiceKeys(WindowsAzureData):

    def __init__(self):
        self.primary = ''
        self.secondary = ''


class Locations(WindowsAzureData):

    def __init__(self):
        self.locations = _list_of(Location)

    def __iter__(self):
        return iter(self.locations)

    def __len__(self):
        return len(self.locations)

    def __getitem__(self, index):
        return self.locations[index]


class Location(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.display_name = ''
        self.available_services = _scalar_list_of(_unicode_type, 'AvailableService')
        self.compute_capabilities = ComputeCapabilities()


class ComputeCapabilities(WindowsAzureData):

    def __init__(self):
        self.web_worker_role_sizes = _scalar_list_of(_unicode_type, 'RoleSize')
        self.virtual_machines_role_sizes = _scalar_list_of(_unicode_type, 'RoleSize')


class AffinityGroup(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.label = _Base64String()
        self.description = ''
        self.location = ''
        self.hosted_services = HostedServices()
        self.storage_services = StorageServices()
        self.capabilities = _scalar_list_of(_unicode_type, 'Capability')


class AffinityGroups(WindowsAzureData):

    def __init__(self):
        self.affinity_groups = _list_of(AffinityGroup)

    def __iter__(self):
        return iter(self.affinity_groups)

    def __len__(self):
        return len(self.affinity_groups)

    def __getitem__(self, index):
        return self.affinity_groups[index]


class HostedServices(WindowsAzureData):

    def __init__(self):
        self.hosted_services = _list_of(HostedService)

    def __iter__(self):
        return iter(self.hosted_services)

    def __len__(self):
        return len(self.hosted_services)

    def __getitem__(self, index):
        return self.hosted_services[index]


class HostedService(WindowsAzureData):

    def __init__(self):
        self.url = ''
        self.service_name = ''
        self.hosted_service_properties = HostedServiceProperties()
        self.deployments = Deployments()


class HostedServiceProperties(WindowsAzureData):

    def __init__(self):
        self.description = ''
        self.location = ''
        self.affinity_group = ''
        self.label = _Base64String()
        self.status = ''
        self.date_created = ''
        self.date_last_modified = ''
        self.extended_properties = _dict_of(
            'ExtendedProperty', 'Name', 'Value')


class VirtualNetworkSites(WindowsAzureData):

    def __init__(self):
        self.virtual_network_sites = _list_of(VirtualNetworkSite)

    def __iter__(self):
        return iter(self.virtual_network_sites)

    def __len__(self):
        return len(self.virtual_network_sites)

    def __getitem__(self, index):
        return self.virtual_network_sites[index]


class VirtualNetworkSite(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.id = ''
        self.affinity_group = ''
        self.subnets = Subnets()


class Subnets(WindowsAzureData):

    def __init__(self):
        self.subnets = _list_of(Subnet)

    def __iter__(self):
        return iter(self.subnets)

    def __len__(self):
        return len(self.subnets)

    def __getitem__(self, index):
        return self.subnets[index]


class Subnet(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.address_prefix = ''



class Deployments(WindowsAzureData):

    def __init__(self):
        self.deployments = _list_of(Deployment)

    def __iter__(self):
        return iter(self.deployments)

    def __len__(self):
        return len(self.deployments)

    def __getitem__(self, index):
        return self.deployments[index]


class Deployment(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.deployment_slot = ''
        self.private_id = ''
        self.status = ''
        self.label = _Base64String()
        self.url = ''
        self.configuration = _Base64String()
        self.role_instance_list = RoleInstanceList()
        self.upgrade_status = UpgradeStatus()
        self.upgrade_domain_count = ''
        self.role_list = RoleList()
        self.sdk_version = ''
        self.input_endpoint_list = InputEndpoints()
        self.locked = False
        self.rollback_allowed = False
        self.persistent_vm_downtime_info = PersistentVMDowntimeInfo()
        self.created_time = ''
        self.virtual_network_name = ''
        self.last_modified_time = ''
        self.extended_properties = _dict_of(
            'ExtendedProperty', 'Name', 'Value')
        self.virtual_ips = VirtualIPs()


class RoleInstanceList(WindowsAzureData):

    def __init__(self):
        self.role_instances = _list_of(RoleInstance)

    def __iter__(self):
        return iter(self.role_instances)

    def __len__(self):
        return len(self.role_instances)

    def __getitem__(self, index):
        return self.role_instances[index]


class RoleInstance(WindowsAzureData):

    def __init__(self):
        self.role_name = ''
        self.instance_name = ''
        self.instance_status = ''
        self.instance_upgrade_domain = 0
        self.instance_fault_domain = 0
        self.instance_size = ''
        self.instance_state_details = ''
        self.instance_error_code = ''
        self.ip_address = ''
        self.instance_endpoints = InstanceEndpoints()
        self.power_state = ''
        self.fqdn = ''
        self.host_name = ''
        self.public_ips = PublicIPs()

class InstanceEndpoints(WindowsAzureData):

    def __init__(self):
        self.instance_endpoints = _list_of(InstanceEndpoint)

    def __iter__(self):
        return iter(self.instance_endpoints)

    def __len__(self):
        return len(self.instance_endpoints)

    def __getitem__(self, index):
        return self.instance_endpoints[index]


class InstanceEndpoint(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.vip = ''
        self.public_port = ''
        self.local_port = ''
        self.protocol = ''


class UpgradeStatus(WindowsAzureData):

    def __init__(self):
        self.upgrade_type = ''
        self.current_upgrade_domain_state = ''
        self.current_upgrade_domain = ''


class InputEndpoints(WindowsAzureData):

    def __init__(self):
        self.input_endpoints = _list_of(InputEndpoint)

    def __iter__(self):
        return iter(self.input_endpoints)

    def __len__(self):
        return len(self.input_endpoints)

    def __getitem__(self, index):
        return self.input_endpoints[index]


class InputEndpoint(WindowsAzureData):

    def __init__(self):
        self.role_name = ''
        self.vip = ''
        self.port = ''


class RoleList(WindowsAzureData):

    def __init__(self):
        self.roles = _list_of(Role)

    def __iter__(self):
        return iter(self.roles)

    def __len__(self):
        return len(self.roles)

    def __getitem__(self, index):
        return self.roles[index]


class Role(WindowsAzureData):

    def __init__(self):
        self.role_name = ''
        self.role_type = ''
        self.os_version = ''
        self.configuration_sets = ConfigurationSets()
        self.availability_set_name = ''
        self.data_virtual_hard_disks = DataVirtualHardDisks()
        self.os_virtual_hard_disk = OSVirtualHardDisk()
        self.role_size = ''
        self.default_win_rm_certificate_thumbprint = ''


class CaptureRoleAsVMImage(WindowsAzureData):

    def __init__(self, os_state=None, vm_image_name=None, vm_image_label=None,
                 description=None, language=None, image_family=None,
                 recommended_vm_size=None):
        self.os_state = os_state
        self.vm_image_name = vm_image_name
        self.vm_image_label = vm_image_label
        self.description = description
        self.language = language
        self.image_family = image_family
        self.recommended_vm_size = recommended_vm_size


class OSDiskConfiguration(WindowsAzureData):

    def __init__(self):
        self.name = None
        self.host_caching = None
        self.os_state = None
        self.os = None
        self.media_link = None
        self.logical_disk_size_in_gb = -1


class DataDiskConfigurations(WindowsAzureData):

    def __init__(self):
        self.data_disk_configurations = _list_of(DataDiskConfiguration)

    def __iter__(self):
        return iter(self.data_disk_configurations)

    def __len__(self):
        return len(self.data_disk_configurations)

    def __getitem__(self, index):
        return self.data_disk_configurations[index]


class DataDiskConfiguration(WindowsAzureData):

    def __init__(self):
        self.name = None
        self.host_caching = None
        self.lun = -1
        self.media_link = None
        self.logical_disk_size_in_gb = -1


class VMImages(WindowsAzureData):

    def __init__(self):
        self.vm_images = _list_of(VMImage)

    def __iter__(self):
        return iter(self.vm_images)

    def __len__(self):
        return len(self.vm_images)

    def __getitem__(self, index):
        return self.vm_images[index]


class VMImage(WindowsAzureData):

    def __init__(self, name=None, label=None, description=None):
        self.name = name
        self.label = label
        self.category = None # read-only
        self.description = description
        self.os_disk_configuration = OSDiskConfiguration()
        self.data_disk_configurations = DataDiskConfigurations()
        self.service_name = None # read-only
        self.deployment_name = None # read-only
        self.role_name = None # read-only
        self.location = None # read-only
        self.affinity_group = None # read-only
        self.created_time = None # read-only
        self.modified_time = None # read-only
        self.language = None
        self.image_family = None
        self.recommended_vm_size = None
        self.is_premium = False # read-only
        self.eula = None
        self.icon_uri = None
        self.small_icon_uri = None
        self.privacy_uri = None
        self.publisher_name = None # read-only
        self.published_date = None
        self.show_in_gui = False
        self.pricing_detail_link = None # read-only


class ResourceExtensions(WindowsAzureData):

    def __init__(self):
        self.resource_extensions = _list_of(ResourceExtension)

    def __iter__(self):
        return iter(self.resource_extensions)

    def __len__(self):
        return len(self.resource_extensions)

    def __getitem__(self, index):
        return self.resource_extensions[index]


class ResourceExtension(WindowsAzureData):

    def __init__(self):
        self.publisher = ''
        self.name = ''
        self.version = ''
        self.label = ''
        self.description = ''
        self.public_configuration_schema = ''
        self.private_configuration_schema = ''
        self.sample_config = ''
        self.replication_completed = False
        self.eula = ''
        self.privacy_uri = ''
        self.homepage_uri = ''
        self.is_json_extension = False
        self.is_internal_extension = False
        self.disallow_major_version_upgrade = False
        self.company_name = ''
        self.supported_os = ''
        self.published_date = ''


class ResourceExtensionParameterValues(WindowsAzureData):

    def __init__(self):
        self.resource_extension_parameter_values = _list_of(ResourceExtensionParameterValue)

    def __iter__(self):
        return iter(self.resource_extension_parameter_values)

    def __len__(self):
        return len(self.resource_extension_parameter_values)

    def __getitem__(self, index):
        return self.resource_extension_parameter_values[index]


class ResourceExtensionParameterValue(WindowsAzureData):

    def __init__(self):
        self.key = ''
        self.value = ''
        self.type = ''


class ResourceExtensionReferences(WindowsAzureData):

    def __init__(self):
        self.resource_extension_references = _list_of(ResourceExtensionReference)

    def __iter__(self):
        return iter(self.resource_extension_references)

    def __len__(self):
        return len(self.resource_extension_references)

    def __getitem__(self, index):
        return self.resource_extension_references[index]


class ResourceExtensionReference(WindowsAzureData):

    def __init__(self, reference_name='', publisher='', name='', version=''):
        self.reference_name = reference_name
        self.publisher = publisher
        self.name = name
        self.version = version
        self.resource_extension_parameter_values = ResourceExtensionParameterValues()
        self.state = ''
        self.certificates = Certificates()


class AdditionalUnattendContent(WindowsAzureData):

    def __init__(self):
        self.passes = Passes()


class Passes(WindowsAzureData):

    def __init__(self):
        self.passes = _list_of(UnattendPass)

    def __iter__(self):
        return iter(self.passes)

    def __len__(self):
        return len(self.passes)

    def __getitem__(self, index):
        return self.passes[index]


class UnattendPass(WindowsAzureData):

    def __init__(self):
        self.pass_name = ''
        self.components = Components()


class Components(WindowsAzureData):

    def __init__(self):
        self.components = _list_of(UnattendComponent)

    def __iter__(self):
        return iter(self.components)

    def __len__(self):
        return len(self.components)

    def __getitem__(self, index):
        return self.components[index]


class UnattendComponent(WindowsAzureData):

    def __init__(self):
        self.component_name = ''
        self.component_settings = ComponentSettings()


class ComponentSettings(WindowsAzureData):

    def __init__(self):
        self.component_settings = _list_of(ComponentSetting)

    def __iter__(self):
        return iter(self.component_settings)

    def __len__(self):
        return len(self.component_settings)

    def __getitem__(self, index):
        return self.component_settings[index]


class ComponentSetting(WindowsAzureData):

    def __init__(self):
        self.setting_name = ''
        self.content = ''


class DnsServer(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.address = ''


class ReservedIPs(WindowsAzureData):

    def __init__(self):
        self.reserved_ips = _list_of(ReservedIP)

    def __iter__(self):
        return iter(self.reserved_ips)

    def __len__(self):
        return len(self.reserved_ips)

    def __getitem__(self, index):
        return self.reserved_ips[index]


class ReservedIP(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.address = ''
        self.id = ''
        self.label = ''
        self.state = ''
        self.in_use = False
        self.service_name = ''
        self.deployment_name = ''
        self.location = ''


class PersistentVMDowntimeInfo(WindowsAzureData):

    def __init__(self):
        self.start_time = ''
        self.end_time = ''
        self.status = ''

class VirtualIPs(WindowsAzureData):

    def __init__(self):
        self.virtual_ips = _list_of(VirtualIP)

    def __iter__(self):
        return iter(self.virtual_ips)

    def __len__(self):
        return len(self.virtual_ips)

    def __getitem__(self, index):
        return self.virtual_ips[index]

class VirtualIP(WindowsAzureData):

    def __init__(self):
        self.address = ''
        self.is_reserved = False
        self.reserved_ip_name = ''
        self.type = ''


class Certificates(WindowsAzureData):

    def __init__(self):
        self.certificates = _list_of(Certificate)

    def __iter__(self):
        return iter(self.certificates)

    def __len__(self):
        return len(self.certificates)

    def __getitem__(self, index):
        return self.certificates[index]


class Certificate(WindowsAzureData):

    def __init__(self):
        self.certificate_url = ''
        self.thumbprint = ''
        self.thumbprint_algorithm = ''
        self.data = ''


class OperationError(WindowsAzureData):

    def __init__(self):
        self.code = ''
        self.message = ''


class Operation(WindowsAzureData):

    def __init__(self):
        self.id = ''
        self.status = ''
        self.http_status_code = ''
        self.error = OperationError()


class OperatingSystem(WindowsAzureData):

    def __init__(self):
        self.version = ''
        self.label = _Base64String()
        self.is_default = True
        self.is_active = True
        self.family = 0
        self.family_label = _Base64String()


class OperatingSystems(WindowsAzureData):

    def __init__(self):
        self.operating_systems = _list_of(OperatingSystem)

    def __iter__(self):
        return iter(self.operating_systems)

    def __len__(self):
        return len(self.operating_systems)

    def __getitem__(self, index):
        return self.operating_systems[index]


class OperatingSystemFamily(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.label = _Base64String()
        self.operating_systems = OperatingSystems()


class OperatingSystemFamilies(WindowsAzureData):

    def __init__(self):
        self.operating_system_families = _list_of(OperatingSystemFamily)

    def __iter__(self):
        return iter(self.operating_system_families)

    def __len__(self):
        return len(self.operating_system_families)

    def __getitem__(self, index):
        return self.operating_system_families[index]


class Subscriptions(WindowsAzureData):

    def __init__(self):
        self.subscriptions = _list_of(Subscription)

    def __iter__(self):
        return iter(self.subscriptions)

    def __len__(self):
        return len(self.subscriptions)

    def __getitem__(self, index):
        return self.subscriptions[index]


class Subscription(WindowsAzureData):

    def __init__(self):
        self.subscription_id = ''
        self.subscription_name = ''
        self.subscription_status = ''
        self.account_admin_live_email_id = ''
        self.service_admin_live_email_id = ''
        self.max_core_count = 0
        self.max_storage_accounts = 0
        self.max_hosted_services = 0
        self.current_core_count = 0
        self.current_hosted_services = 0
        self.current_storage_accounts = 0
        self.max_virtual_network_sites = 0
        self.current_virtual_network_sites = 0
        self.max_local_network_sites = 0
        self.max_dns_servers = 0
        self.aad_tenant_id = ''
        self.created_time = ''


class SubscriptionOperationCollection(WindowsAzureData):

    def __init__(self):
        self.subscription_operations = SubscriptionOperations()
        self.continuation_token = ''


class SubscriptionOperations(WindowsAzureData):

    def __init__(self):
        self.subscription_operations = _list_of(SubscriptionOperation)

    def __iter__(self):
        return iter(self.subscription_operations)

    def __len__(self):
        return len(self.subscription_operations)

    def __getitem__(self, index):
        return self.subscription_operations[index]


class SubscriptionOperation(WindowsAzureData):

    def __init__(self):
        self.operation_id = ''
        self.operation_object_id = ''
        self.operation_name = ''
        self.operation_parameters = _dict_of(
            'OperationParameter', 'a:Name', 'a:Value')
        self.operation_caller = OperationCaller()
        self.operation_status = SubscriptionOperationStatus()
        self.operation_started_time = ''
        self.operation_completed_time = ''
        self.operation_kind = ''


class SubscriptionOperationStatus(WindowsAzureData):
    _xml_name = 'OperationStatus'

    def __init__(self):
        self.status_id = ''
        self.status = ''
        self.http_status_code = 0


class OperationCaller(WindowsAzureData):

    def __init__(self):
        self.used_service_management_api = False
        self.user_email_address = ''
        self.subscription_certificate_thumbprint = ''
        self.client_ip = ''


class AvailabilityResponse(WindowsAzureData):

    def __init__(self):
        self.result = False
        self.reason = False


class SubscriptionCertificates(WindowsAzureData):

    def __init__(self):
        self.subscription_certificates = _list_of(SubscriptionCertificate)

    def __iter__(self):
        return iter(self.subscription_certificates)

    def __len__(self):
        return len(self.subscription_certificates)

    def __getitem__(self, index):
        return self.subscription_certificates[index]


class SubscriptionCertificate(WindowsAzureData):

    def __init__(self):
        self.subscription_certificate_public_key = ''
        self.subscription_certificate_thumbprint = ''
        self.subscription_certificate_data = ''
        self.created = ''


class RoleSizes(WindowsAzureData):

    def __init__(self):
        self.role_sizes = _list_of(RoleSize)

    def __iter__(self):
        return iter(self.role_sizes)

    def __len__(self):
        return len(self.role_sizes)

    def __getitem__(self, index):
        return self.role_sizes[index]


class RoleSize(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.label = ''
        self.cores = 0
        self.memory_in_mb = 0
        self.supported_by_web_worker_roles = False
        self.supported_by_virtual_machines = False
        self.max_data_disk_count = 0
        self.web_worker_resource_disk_size_in_mb = 0
        self.virtual_machine_resource_disk_size_in_mb = 0


class Images(WindowsAzureData):

    def __init__(self):
        self.images = _list_of(OSImage)

    def __iter__(self):
        return iter(self.images)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        return self.images[index]


class OSImage(WindowsAzureData):

    def __init__(self):
        self.affinity_group = ''
        self.category = ''
        self.location = ''
        self.logical_size_in_gb = 0
        self.label = ''
        self.media_link = ''
        self.name = ''
        self.os = ''
        self.eula = ''
        self.description = ''
        self.image_family = ''
        self.show_in_gui = True
        self.published_date = ''
        self.is_premium = True
        self.icon_uri = ''
        self.privacy_uri = ''
        self.recommended_vm_size = ''
        self.publisher_name = ''
        self.pricing_detail_link = ''
        self.small_icon_uri = ''
        self.os_state = ''
        self.language = ''


class OSImageDetails(WindowsAzureData):

    def __init__(self):
        self.category = ''
        self.label = ''
        self.location = ''
        self.logical_size_in_gb = 0
        self.media_link = ''
        self.name = ''
        self.os = ''
        self.eula = ''
        self.description = ''
        self.image_family = ''
        self.show_in_gui = True
        self.published_date = ''
        self.is_premium = True
        self.icon_uri = ''
        self.privacy_uri = ''
        self.recommended_vm_size = ''
        self.small_icon_uri = ''
        self.language = ''
        self.replication_progress = ReplicationProgress()


class ReplicationProgress(WindowsAzureData):

    def __init__(self):
        self.replication_progress_elements = _list_of(ReplicationProgressElement)

    def __iter__(self):
        return iter(self.replication_progress_elements)

    def __len__(self):
        return len(self.replication_progress_elements)

    def __getitem__(self, index):
        return self.replication_progress_elements[index]


class ReplicationProgressElement(WindowsAzureData):

    def __init__(self):
        self.location = ''
        self.progress = 0


class Disks(WindowsAzureData):

    def __init__(self):
        self.disks = _list_of(Disk)

    def __iter__(self):
        return iter(self.disks)

    def __len__(self):
        return len(self.disks)

    def __getitem__(self, index):
        return self.disks[index]


class Disk(WindowsAzureData):

    def __init__(self):
        self.affinity_group = ''
        self.attached_to = AttachedTo()
        self.has_operating_system = ''
        self.is_corrupted = ''
        self.location = ''
        self.logical_disk_size_in_gb = 0
        self.label = ''
        self.media_link = ''
        self.name = ''
        self.os = ''
        self.source_image_name = ''


class AttachedTo(WindowsAzureData):

    def __init__(self):
        self.hosted_service_name = ''
        self.deployment_name = ''
        self.role_name = ''


class PersistentVMRole(WindowsAzureData):

    def __init__(self):
        self.role_name = ''
        self.role_type = ''
        self.os_version = ''  # undocumented
        self.configuration_sets = ConfigurationSets()
        self.availability_set_name = ''
        self.data_virtual_hard_disks = DataVirtualHardDisks()
        self.os_virtual_hard_disk = OSVirtualHardDisk()
        self.role_size = ''
        self.default_win_rm_certificate_thumbprint = ''


class ConfigurationSets(WindowsAzureData):

    def __init__(self):
        self.configuration_sets = _list_of(ConfigurationSet)

    def __iter__(self):
        return iter(self.configuration_sets)

    def __len__(self):
        return len(self.configuration_sets)

    def __getitem__(self, index):
        return self.configuration_sets[index]


class PublicIPs(WindowsAzureData):

    def __init__(self):
        self.public_ips = _list_of(PublicIP)

    def __iter__(self):
        return iter(self.public_ips)

    def __len__(self):
        return len(self.public_ips)

    def __getitem__(self, index):
        return self.public_ips[index]


class PublicIP(WindowsAzureData):

    def __init__(self, name=''):
        self.name = name
        self.idle_timeout_in_minutes = 4
        self.address = None

class ConfigurationSet(WindowsAzureData):

    def __init__(self):
        self.configuration_set_type = u'NetworkConfiguration'
        self.role_type = ''
        self.input_endpoints = ConfigurationSetInputEndpoints()
        self.subnet_names = _scalar_list_of(_unicode_type, 'SubnetName')
        self.public_ips = PublicIPs()
        self.static_virtual_network_ip_address = None


class ConfigurationSetInputEndpoints(WindowsAzureData):

    def __init__(self):
        self.input_endpoints = _list_of(
            ConfigurationSetInputEndpoint, 'InputEndpoint')

    def __iter__(self):
        return iter(self.input_endpoints)

    def __len__(self):
        return len(self.input_endpoints)

    def __getitem__(self, index):
        return self.input_endpoints[index]


class ConfigurationSetInputEndpoint(WindowsAzureData):

    '''
    Initializes a network configuration input endpoint.

    name:
        Specifies the name for the external endpoint.
    protocol:
        Specifies the protocol to use to inspect the virtual machine
        availability status. Possible values are: HTTP, TCP.
    port:
        Specifies the external port to use for the endpoint.
    local_port:
        Specifies the internal port on which the virtual machine is listening
        to serve the endpoint.
    load_balanced_endpoint_set_name:
        Specifies a name for a set of load-balanced endpoints. Specifying this
        element for a given endpoint adds it to the set. If you are setting an
        endpoint to use to connect to the virtual machine via the Remote
        Desktop, do not set this property.
    enable_direct_server_return:
        Specifies whether direct server return load balancing is enabled.
    '''

    def __init__(self, name='', protocol='', port='', local_port='',
                 load_balanced_endpoint_set_name='',
                 enable_direct_server_return=False,
                 idle_timeout_in_minutes=4):
        self.enable_direct_server_return = enable_direct_server_return
        self.idle_timeout_in_minutes = idle_timeout_in_minutes
        self.load_balanced_endpoint_set_name = load_balanced_endpoint_set_name
        self.local_port = local_port
        self.name = name
        self.port = port
        self.load_balancer_probe = LoadBalancerProbe()
        self.protocol = protocol


class WindowsConfigurationSet(WindowsAzureData):

    def __init__(self, computer_name=None, admin_password=None,
                 reset_password_on_first_logon=None,
                 enable_automatic_updates=None, time_zone=None,
                 admin_username=None, custom_data=None):
        self.configuration_set_type = u'WindowsProvisioningConfiguration'
        self.computer_name = computer_name
        self.admin_password = admin_password
        self.admin_username = admin_username
        self.reset_password_on_first_logon = reset_password_on_first_logon
        self.enable_automatic_updates = enable_automatic_updates
        self.time_zone = time_zone
        self.domain_join = DomainJoin()
        self.stored_certificate_settings = StoredCertificateSettings()
        self.win_rm = WinRM()
        self.custom_data = custom_data
        self.additional_unattend_content = AdditionalUnattendContent()


class DomainJoin(WindowsAzureData):

    def __init__(self):
        self.credentials = Credentials()
        self.join_domain = ''
        self.machine_object_ou = ''


class Credentials(WindowsAzureData):

    def __init__(self):
        self.domain = ''
        self.username = ''
        self.password = ''


class StoredCertificateSettings(WindowsAzureData):

    def __init__(self):
        self.stored_certificate_settings = _list_of(CertificateSetting)

    def __iter__(self):
        return iter(self.stored_certificate_settings)

    def __len__(self):
        return len(self.stored_certificate_settings)

    def __getitem__(self, index):
        return self.stored_certificate_settings[index]


class CertificateSetting(WindowsAzureData):

    '''
    Initializes a certificate setting.

    thumbprint:
        Specifies the thumbprint of the certificate to be provisioned. The
        thumbprint must specify an existing service certificate.
    store_name:
        Specifies the name of the certificate store from which retrieve
        certificate.
    store_location:
        Specifies the target certificate store location on the virtual machine.
        The only supported value is LocalMachine.
    '''

    def __init__(self, thumbprint='', store_name='', store_location=''):
        self.thumbprint = thumbprint
        self.store_name = store_name
        self.store_location = store_location


class WinRM(WindowsAzureData):

    '''
    Contains configuration settings for the Windows Remote Management service on
    the Virtual Machine.
    '''

    def __init__(self):
        self.listeners = Listeners()


class Listeners(WindowsAzureData):

    def __init__(self):
        self.listeners = _list_of(Listener)

    def __iter__(self):
        return iter(self.listeners)

    def __len__(self):
        return len(self.listeners)

    def __getitem__(self, index):
        return self.listeners[index]


class Listener(WindowsAzureData):

    '''
    Specifies the protocol and certificate information for the listener.

    protocol:
        Specifies the protocol of listener.  Possible values are: Http, Https.
        The value is case sensitive.
    certificate_thumbprint:
        Optional. Specifies the certificate thumbprint for the secure
        connection. If this value is not specified, a self-signed certificate is
        generated and used for the Virtual Machine.
    '''

    def __init__(self, protocol='', certificate_thumbprint=''):
        self.protocol = protocol
        self.certificate_thumbprint = certificate_thumbprint


class LinuxConfigurationSet(WindowsAzureData):

    def __init__(self, host_name=None, user_name=None, user_password=None,
                 disable_ssh_password_authentication=None, custom_data=None):
        self.configuration_set_type = u'LinuxProvisioningConfiguration'
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.disable_ssh_password_authentication =\
            disable_ssh_password_authentication
        self.ssh = SSH()
        self.custom_data = custom_data


class SSH(WindowsAzureData):

    def __init__(self):
        self.public_keys = PublicKeys()
        self.key_pairs = KeyPairs()


class PublicKeys(WindowsAzureData):

    def __init__(self):
        self.public_keys = _list_of(PublicKey)

    def __iter__(self):
        return iter(self.public_keys)

    def __len__(self):
        return len(self.public_keys)

    def __getitem__(self, index):
        return self.public_keys[index]


class PublicKey(WindowsAzureData):

    def __init__(self, fingerprint='', path=''):
        self.fingerprint = fingerprint
        self.path = path


class KeyPairs(WindowsAzureData):

    def __init__(self):
        self.key_pairs = _list_of(KeyPair)

    def __iter__(self):
        return iter(self.key_pairs)

    def __len__(self):
        return len(self.key_pairs)

    def __getitem__(self, index):
        return self.key_pairs[index]


class KeyPair(WindowsAzureData):

    def __init__(self, fingerprint='', path=''):
        self.fingerprint = fingerprint
        self.path = path


class LoadBalancerProbe(WindowsAzureData):

    def __init__(self):
        self.path = ''
        self.port = ''
        self.protocol = ''


class DataVirtualHardDisks(WindowsAzureData):

    def __init__(self):
        self.data_virtual_hard_disks = _list_of(DataVirtualHardDisk)

    def __iter__(self):
        return iter(self.data_virtual_hard_disks)

    def __len__(self):
        return len(self.data_virtual_hard_disks)

    def __getitem__(self, index):
        return self.data_virtual_hard_disks[index]


class DataVirtualHardDisk(WindowsAzureData):

    def __init__(self, media_link='', host_caching=None,
                 disk_label='', disk_name='',
                 lun=0, logical_disk_size_in_gb=0,
                 source_media_link=None):
        self.host_caching = host_caching
        self.disk_label = disk_label
        self.disk_name = disk_name
        self.lun = lun
        self.logical_disk_size_in_gb = logical_disk_size_in_gb
        self.media_link = media_link
        self.source_media_link = source_media_link


class OSVirtualHardDisk(WindowsAzureData):

    def __init__(self, source_image_name=None, media_link=None,
                 host_caching=None, disk_label=None, disk_name=None,
                 os=None, remote_source_image_link=None):
        self.source_image_name = source_image_name
        self.media_link = media_link
        self.host_caching = host_caching
        self.disk_label = disk_label
        self.disk_name = disk_name
        self.os = os
        self.remote_source_image_link = remote_source_image_link


class AsynchronousOperationResult(WindowsAzureData):

    def __init__(self, request_id=None):
        self.request_id = request_id


class ServiceBusRegion(WindowsAzureData):

    def __init__(self):
        self.code = ''
        self.fullname = ''


class ServiceBusNamespace(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.region = ''
        self.default_key = ''
        self.status = ''
        self.created_at = ''
        self.acs_management_endpoint = ''
        self.servicebus_endpoint = ''
        self.connection_string = ''
        self.subscription_id = ''
        self.enabled = False


class MetricProperties(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.primary_aggregation = ''
        self.unit = ''
        self.display_name = ''


class MetricValues(WindowsAzureData):

    def __init__(self):
        self.timestamp = ''
        self.min = 0
        self.max = 0
        self.average = 0
        self.total = 0


class MetricRollups(WindowsAzureData):

    def __init__(self):
        self.time_grain = ''
        self.retention = ''


class WebSpaces(WindowsAzureData):

    def __init__(self):
        self.web_space = _list_of(WebSpace)

    def __iter__(self):
        return iter(self.web_space)

    def __len__(self):
        return len(self.web_space)

    def __getitem__(self, index):
        return self.web_space[index]


class WebSpace(WindowsAzureData):

    def __init__(self):
        self.availability_state = ''
        self.geo_location = ''
        self.geo_region = ''
        self.name = ''
        self.plan = ''
        self.status = ''
        self.subscription = ''


class Sites(WindowsAzureData):

    def __init__(self):
        self.site = _list_of(Site)

    def __iter__(self):
        return iter(self.site)

    def __len__(self):
        return len(self.site)

    def __getitem__(self, index):
        return self.site[index]


class Site(WindowsAzureData):

    def __init__(self):
        self.admin_enabled = False
        self.availability_state = ''
        self.compute_mode = ''
        self.enabled = False
        self.enabled_host_names = _scalar_list_of(_unicode_type, 'a:string')
        self.host_name_ssl_states = HostNameSslStates()
        self.host_names = _scalar_list_of(_unicode_type, 'a:string')
        self.last_modified_time_utc = ''
        self.name = ''
        self.repository_site_name = ''
        self.self_link = ''
        self.server_farm = ''
        self.site_mode = ''
        self.state = ''
        self.storage_recovery_default_state = ''
        self.usage_state = ''
        self.web_space = ''


class HostNameSslStates(WindowsAzureData):

    def __init__(self):
        self.host_name_ssl_state = _list_of(HostNameSslState)

    def __iter__(self):
        return iter(self.host_name_ssl_state)

    def __len__(self):
        return len(self.host_name_ssl_state)

    def __getitem__(self, index):
        return self.host_name_ssl_state[index]


class HostNameSslState(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.ssl_state = ''


class PublishData(WindowsAzureData):
    _xml_name = 'publishData'

    def __init__(self):
        self.publish_profiles = _list_of(PublishProfile, 'publishProfile')

class PublishProfile(WindowsAzureData):

    def __init__(self):
        self.profile_name = _xml_attribute('profileName')
        self.publish_method = _xml_attribute('publishMethod')
        self.publish_url = _xml_attribute('publishUrl')
        self.msdeploysite = _xml_attribute('msdeploySite')
        self.user_name = _xml_attribute('userName')
        self.user_pwd = _xml_attribute('userPWD')
        self.destination_app_url = _xml_attribute('destinationAppUrl')
        self.sql_server_db_connection_string = _xml_attribute('SQLServerDBConnectionString')
        self.my_sqldb_connection_string = _xml_attribute('mySQLDBConnectionString')
        self.hosting_provider_forum_link = _xml_attribute('hostingProviderForumLink')
        self.control_panel_link = _xml_attribute('controlPanelLink')

class QueueDescription(WindowsAzureData):

    def __init__(self):
        self.lock_duration = ''
        self.max_size_in_megabytes = 0
        self.requires_duplicate_detection = False
        self.requires_session = False
        self.default_message_time_to_live = ''
        self.dead_lettering_on_message_expiration = False
        self.duplicate_detection_history_time_window = ''
        self.max_delivery_count = 0
        self.enable_batched_operations = False
        self.size_in_bytes = 0
        self.message_count = 0
        self.is_anonymous_accessible = False
        self.authorization_rules = AuthorizationRules()
        self.status = ''
        self.created_at = ''
        self.updated_at = ''
        self.accessed_at = ''
        self.support_ordering = False
        self.auto_delete_on_idle = ''
        self.count_details = CountDetails()
        self.entity_availability_status = ''

class TopicDescription(WindowsAzureData):

    def __init__(self):
        self.default_message_time_to_live = ''
        self.max_size_in_megabytes = 0
        self.requires_duplicate_detection = False
        self.duplicate_detection_history_time_window = ''
        self.enable_batched_operations = False
        self.size_in_bytes = 0
        self.filtering_messages_before_publishing = False
        self.is_anonymous_accessible = False
        self.authorization_rules = AuthorizationRules()
        self.status = ''
        self.created_at = ''
        self.updated_at = ''
        self.accessed_at = ''
        self.support_ordering = False
        self.count_details = CountDetails()
        self.subscription_count = 0

class CountDetails(WindowsAzureData):

    def __init__(self):
        self.active_message_count = 0
        self.dead_letter_message_count = 0
        self.scheduled_message_count = 0
        self.transfer_message_count = 0
        self.transfer_dead_letter_message_count = 0

class NotificationHubDescription(WindowsAzureData):

    def __init__(self):
        self.registration_ttl = ''
        self.authorization_rules = AuthorizationRules()

class AuthorizationRules(WindowsAzureData):

    def __init__(self):
        self.authorization_rule = _list_of(AuthorizationRule)

    def __iter__(self):
        return iter(self.authorization_rule)

    def __len__(self):
        return len(self.authorization_rule)

    def __getitem__(self, index):
        return self.authorization_rule[index]

class AuthorizationRule(WindowsAzureData):

    def __init__(self):
        self.claim_type = ''
        self.claim_value = ''
        self.rights = _scalar_list_of(_unicode_type, 'AccessRights')
        self.created_time = ''
        self.modified_time = ''
        self.key_name = ''
        self.primary_key = ''
        self.secondary_keu = ''

class RelayDescription(WindowsAzureData):

    def __init__(self):
        self.path = ''
        self.listener_type = ''
        self.listener_count = 0
        self.created_at = ''
        self.updated_at = ''


class MetricResponses(WindowsAzureData):

    def __init__(self):
        self.metric_response = _list_of(MetricResponse)

    def __iter__(self):
        return iter(self.metric_response)

    def __len__(self):
        return len(self.metric_response)

    def __getitem__(self, index):
        return self.metric_response[index]


class MetricResponse(WindowsAzureData):

    def __init__(self):
        self.code = ''
        self.data = Data()
        self.message = ''


class Data(WindowsAzureData):

    def __init__(self):
        self.display_name = ''
        self.end_time = ''
        self.name = ''
        self.primary_aggregation_type = ''
        self.start_time = ''
        self.time_grain = ''
        self.unit = ''
        self.values = Values()


class Values(WindowsAzureData):

    def __init__(self):
        self.metric_sample = _list_of(MetricSample)

    def __iter__(self):
        return iter(self.metric_sample)

    def __len__(self):
        return len(self.metric_sample)

    def __getitem__(self, index):
        return self.metric_sample[index]


class MetricSample(WindowsAzureData):

    def __init__(self):
        self.count = 0
        self.time_created = ''
        self.total = 0


class MetricDefinitions(WindowsAzureData):

    def __init__(self):
        self.metric_definition = _list_of(MetricDefinition)

    def __iter__(self):
        return iter(self.metric_definition)

    def __len__(self):
        return len(self.metric_definition)

    def __getitem__(self, index):
        return self.metric_definition[index]


class MetricDefinition(WindowsAzureData):

    def __init__(self):
        self.display_name = ''
        self.metric_availabilities = MetricAvailabilities()
        self.name = ''
        self.primary_aggregation_type = ''
        self.unit = ''


class MetricAvailabilities(WindowsAzureData):

    def __init__(self):
        self.metric_availability = _list_of(MetricAvailability, 'MetricAvailabilily')

    def __iter__(self):
        return iter(self.metric_availability)

    def __len__(self):
        return len(self.metric_availability)

    def __getitem__(self, index):
        return self.metric_availability[index]


class MetricAvailability(WindowsAzureData):

    def __init__(self):
        self.retention = ''
        self.time_grain = ''


class Servers(WindowsAzureData):

    def __init__(self):
        self.server = _list_of(Server)

    def __iter__(self):
        return iter(self.server)

    def __len__(self):
        return len(self.server)

    def __getitem__(self, index):
        return self.server[index]


class Server(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.administrator_login = ''
        self.location = ''
        self.geo_paired_region = ''
        self.fully_qualified_domain_name = ''
        self.version = ''


class ServerQuota(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.state = ''
        self.self_link = ''
        self.parent_link = ''
        self.value = 0


class EventLog(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.state = ''
        self.self_link = ''
        self.parent_link = ''
        self.database_name = ''
        self.name = ''
        self.start_time_utc = ''
        self.interval_size_in_minutes = 0
        self.event_category = ''
        self.event_type = ''
        self.event_subtype = 0
        self.event_subtype_description = ''
        self.number_of_events = 0
        self.severity = 0
        self.description = ''
        self.additional_data = ''


class CreateServerResponse(WindowsAzureData):

    def __init__(self):
        self.server_name = ''


class Database(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.state = ''
        self.self_link = ''
        self.parent_link = ''
        self.id = 0
        self.edition = ''
        self.collation_name = ''
        self.creation_date = ''
        self.is_federation_root = False
        self.is_system_object = False
        self.max_size_bytes = 0


class FirewallRule(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.state = ''
        self.self_link = ''
        self.parent_link = ''
        self.start_ip_address = ''
        self.end_ip_address = ''


class ServiceObjective(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.state = ''
        self.self_link = ''
        self.parent_link = ''
        self.id = ''
        self.is_default = False
        self.is_system = False
        self.description = ''
        self.enabled = False


class CloudServices(WindowsAzureData):

    def __init__(self):
        self.cloud_service = _list_of(CloudService)

    def __iter__(self):
        return iter(self.cloud_service)

    def __len__(self):
        return len(self.cloud_service)

    def __getitem__(self, index):
        return self.cloud_service[index]


class CloudService(WindowsAzureData):

    def __init__(self):
        self.name = ''
        self.label = ''
        self.description = ''
        self.geo_region = ''
        self.resources = Resources()


class Resources(WindowsAzureData):

    def __init__(self):
        self.resource = _list_of(Resource)

    def __iter__(self):
        return iter(self.resource)

    def __len__(self):
        return len(self.resource)

    def __getitem__(self, index):
        return self.resource[index]


class Resource(WindowsAzureData):

    def __init__(self):
        self.resource_provider_namespace = ''
        self.type = ''
        self.name = ''
        self.schema_version = ''
        self.e_tag = ''
        self.state = ''
        self.intrinsic_settings = IntrinsicSettings()
        self.operation_status = OperationStatus()


class IntrinsicSettings(WindowsAzureData):

    def __init__(self):
        self.plan = ''
        self.quota = Quota()


class Quota(WindowsAzureData):

    def __init__(self):
        self.max_job_count = 0
        self.max_recurrence = MaxRecurrence()


class MaxRecurrence(WindowsAzureData):

    def __init__(self):
        self.frequency = ''
        self.interval = 0


class OperationStatus(WindowsAzureData):

    def __init__(self):
        self.type = ''
        self.result = ''
