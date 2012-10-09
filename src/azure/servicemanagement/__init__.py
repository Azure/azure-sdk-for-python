#-------------------------------------------------------------------------
# Copyright 2011-2012 Microsoft Corporation
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
import base64
from azure.http import HTTPError
from azure import (WindowsAzureError, WindowsAzureData,
                          _create_entry, _get_entry_properties, xml_escape,
                          _get_child_nodes, WindowsAzureMissingResourceError,
                          WindowsAzureConflictError, _get_serialization_name, 
                          _list_of, _scalar_list_of, _dict_of, _Base64String,
                          _get_children_from_path, _get_first_child_node_value)
import azure

#-----------------------------------------------------------------------------
# Constants for Azure app environment settings. 
AZURE_MANAGEMENT_CERTFILE = 'AZURE_MANAGEMENT_CERTFILE'
AZURE_MANAGEMENT_SUBSCRIPTIONID = 'AZURE_MANAGEMENT_SUBSCRIPTIONID'

#x-ms-version for service management.
X_MS_VERSION = '2012-03-01'

#-----------------------------------------------------------------------------
# Data classes

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
        self.extended_properties = _dict_of('ExtendedProperty', 'Name', 'Value')
        self.capabilities = _scalar_list_of(str, 'Capability')

class StorageAccountProperties(WindowsAzureData):
    def __init__(self):
        self.description = ''
        self.affinity_group = ''
        self.location = ''
        self.label = _Base64String()
        self.status = ''
        self.endpoints = _scalar_list_of(str, 'Endpoint')
        self.geo_replication_enabled = False
        self.geo_primary_region = ''
        self.status_of_primary = ''
        self.geo_secondary_region = ''
        self.status_of_secondary = ''
        self.last_geo_failover_time = ''

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
        self.available_services = _scalar_list_of(str, 'AvailableService')

class AffinityGroup(WindowsAzureData):
    def __init__(self):
        self.name = ''
        self.label = _Base64String()
        self.description = ''
        self.location = ''
        self.hosted_services = HostedServices()
        self.storage_services = StorageServices()
        self.capabilities = _scalar_list_of(str, 'Capability')

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
        self.extended_properties = _dict_of('ExtendedProperty', 'Name', 'Value')

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
        self.last_modified_time = ''
        self.extended_properties = _dict_of('ExtendedProperty', 'Name', 'Value')

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
        self.power_state = ''
        self.fqdn = ''

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
        self.os_version = ''

class PersistentVMDowntimeInfo(WindowsAzureData):
    def __init__(self):
        self.start_time = ''
        self.end_time = ''
        self.status = ''

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
        self.max_local_network_sites = 0
        self.max_dns_servers = 0

class AvailabilityResponse(WindowsAzureData):
    def __init__(self):
        self.result = False

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
        self.media_link= ''
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
        self.role_type= ''
        self.os_version = '' # undocumented
        self.configuration_sets = ConfigurationSets()
        self.availability_set_name = ''
        self.data_virtual_hard_disks = DataVirtualHardDisks()
        self.os_virtual_hard_disk = OSVirtualHardDisk()
        self.role_size = ''

class ConfigurationSets(WindowsAzureData):
    def __init__(self):
        self.configuration_sets = _list_of(ConfigurationSet)

    def __iter__(self):
        return iter(self.configuration_sets)

    def __len__(self):
        return len(self.configuration_sets)

    def __getitem__(self, index):
        return self.configuration_sets[index]

class ConfigurationSet(WindowsAzureData):
    def __init__(self):
        self.configuration_set_type = ''
        self.role_type= ''
        self.input_endpoints = ConfigurationSetInputEndpoints()
        self.subnet_names = _scalar_list_of(str, 'SubnetName')

class ConfigurationSetInputEndpoints(WindowsAzureData):
    def __init__(self):
        self.input_endpoints = _list_of(ConfigurationSetInputEndpoint, 'InputEndpoint')

    def __iter__(self):
        return iter(self.input_endpoints)

    def __len__(self):
        return len(self.input_endpoints)

    def __getitem__(self, index):
        return self.input_endpoints[index]

class ConfigurationSetInputEndpoint(WindowsAzureData):
    '''
    Initializes a network configuration input endpoint.

    name: Specifies the name for the external endpoint.
    protocol: Specifies the protocol to use to inspect the virtual machine availability status. Possible values are: HTTP, TCP.
    port: Specifies the external port to use for the endpoint.
    local_port: Specifies the internal port on which the virtual machine is listening to serve the endpoint.
    load_balanced_endpoint_set_name: Specifies a name for a set of load-balanced endpoints. Specifying this element for a given endpoint adds it to the set. If you are setting an endpoint to use to connect to the virtual machine via the Remote Desktop, do not set this property.
    enable_direct_server_return: Specifies whether direct server return load balancing is enabled. 
    '''
    def __init__(self, name='', protocol='', port='', local_port='', load_balanced_endpoint_set_name='', enable_direct_server_return=False):
        self.enable_direct_server_return = enable_direct_server_return
        self.load_balanced_endpoint_set_name = load_balanced_endpoint_set_name
        self.local_port = local_port
        self.name = name
        self.port = port
        self.load_balancer_probe = LoadBalancerProbe()
        self.protocol = protocol

class WindowsConfigurationSet(WindowsAzureData):
    def __init__(self, computer_name=None, admin_password=None, reset_password_on_first_logon=None, enable_automatic_updates=None, time_zone=None):
        self.configuration_set_type = 'WindowsProvisioningConfiguration'
        self.computer_name = computer_name
        self.admin_password = admin_password
        self.reset_password_on_first_logon = reset_password_on_first_logon
        self.enable_automatic_updates = enable_automatic_updates
        self.time_zone = time_zone
        self.domain_join = DomainJoin()
        self.stored_certificate_settings = StoredCertificateSettings()
        
class DomainJoin(WindowsAzureData):
    def __init__(self):
        self.credentials = Credentials()
        self.join_domain = ''
        self.machine_object_ou = ''

class Credentials(WindowsAzureData):
    def __init(self):
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

    thumbprint: Specifies the thumbprint of the certificate to be provisioned. The thumbprint must specify an existing service certificate.
    store_name: Specifies the name of the certificate store from which retrieve certificate. 
    store_location: Specifies the target certificate store location on the virtual machine. The only supported value is LocalMachine.
    '''
    def __init__(self, thumbprint='', store_name='', store_location=''):
        self.thumbprint = thumbprint
        self.store_name = store_name
        self.store_location = store_location

class LinuxConfigurationSet(WindowsAzureData):
    def __init__(self, host_name=None, user_name=None, user_password=None, disable_ssh_password_authentication=None):
        self.configuration_set_type = 'LinuxProvisioningConfiguration'
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.disable_ssh_password_authentication = disable_ssh_password_authentication
        self.ssh = SSH()

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
    def __init__(self):
        self.finger_print = ''
        self.path = ''

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
    def __init__(self):
        self.finger_print = ''
        self.path = ''

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
    def __init__(self):
        self.host_caching = ''
        self.disk_label = ''
        self.disk_name = ''
        self.lun = 0
        self.logical_disk_size_in_gb = 0
        self.media_link = ''

class OSVirtualHardDisk(WindowsAzureData):
    def __init__(self, source_image_name=None, media_link=None, host_caching=None, disk_label=None, disk_name=None):
        self.source_image_name = source_image_name
        self.media_link = media_link
        self.host_caching = host_caching
        self.disk_label = disk_label
        self.disk_name = disk_name
        self.os = '' # undocumented, not used when adding a role

class AsynchronousOperationResult(WindowsAzureData):
    def __init__(self, request_id=None):
        self.request_id = request_id

def _update_management_header(request):
    ''' Add additional headers for management. '''

    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
        request.headers.append(('Content-Length', str(len(request.body))))  

    #append additional headers base on the service
    request.headers.append(('x-ms-version', X_MS_VERSION))

    # if it is not GET or HEAD request, must set content-type.            
    if not request.method in ['GET', 'HEAD']:
        for name, value in request.headers:
            if 'content-type' == name.lower():
                break
        else:
            request.headers.append(('Content-Type', 'application/atom+xml;type=entry;charset=utf-8')) 

    return request.headers

def _parse_response_for_async_op(response):
    ''' Extracts request id from response header. '''
    
    if response is None:
        return None

    result = AsynchronousOperationResult()
    if response.headers:
        for name, value in response.headers:
            if name.lower() == 'x-ms-request-id':
                result.request_id = value

    return result

def _management_error_handler(http_error):
    ''' Simple error handler for management service. Will add more specific cases '''

    if http_error.status == 409:
        raise WindowsAzureConflictError(azure._ERROR_CONFLICT)
    elif http_error.status == 404:
        raise WindowsAzureMissingResourceError(azure._ERROR_NOT_FOUND)
    else:
        raise WindowsAzureError(azure._ERROR_UNKNOWN % http_error.message + '\n' + http_error.respbody)

class _XmlSerializer(object):
    @staticmethod
    def extended_properties_dict_to_xml_fragment(extended_properties):
        xml = ''
        if extended_properties is not None and len(extended_properties) > 0:
            xml += '<ExtendedProperties>'
            for key, val in extended_properties.items():
                xml += ''.join(['<ExtendedProperty>', '<Name>', str(key), '</Name>', '<Value>', str(val), '</Value>', '</ExtendedProperty>'])
            xml += '</ExtendedProperties>'
        return xml

    @staticmethod
    def create_storage_service_input_to_xml(service_name, description, label, affinity_group, location, geo_replication_enabled, extended_properties):
        xml = '<CreateStorageServiceInput xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if service_name is not None:
            xml += ''.join(['<ServiceName>', str(service_name), '</ServiceName>'])
        if description is not None:
            xml += ''.join(['<Description>', str(description), '</Description>'])
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if affinity_group is not None:
            xml += ''.join(['<AffinityGroup>', str(affinity_group), '</AffinityGroup>'])
        if location is not None:
            xml += ''.join(['<Location>', str(location), '</Location>'])
        if geo_replication_enabled is not None:
            xml += ''.join(['<GeoReplicationEnabled>', str(geo_replication_enabled).lower(), '</GeoReplicationEnabled>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</CreateStorageServiceInput>'
        return xml

    @staticmethod
    def update_storage_service_input_to_xml(description, label, geo_replication_enabled, extended_properties):
        xml = '<UpdateStorageServiceInput xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if description is not None:
            xml += ''.join(['<Description>', str(description), '</Description>'])
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if geo_replication_enabled is not None:
            xml += ''.join(['<GeoReplicationEnabled>', str(geo_replication_enabled).lower(), '</GeoReplicationEnabled>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</UpdateStorageServiceInput>'
        return xml

    @staticmethod
    def regenerate_keys_to_xml(key_type):
        xml = '<?xml version="1.0" encoding="utf-8"?> \
    <RegenerateKeys xmlns="http://schemas.microsoft.com/windowsazure"> \
      <KeyType>' + xml_escape(str(key_type)) + '</KeyType> \
    </RegenerateKeys>'
        return xml

    @staticmethod
    def update_hosted_service_to_xml(label, description, extended_properties):
        xml = '<UpdateHostedService xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if description is not None:
            xml += ''.join(['<Description>', str(description), '</Description>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</UpdateHostedService>'
        return xml

    @staticmethod
    def create_hosted_service_to_xml(service_name, label, description, location, affinity_group, extended_properties):
        xml = '<CreateHostedService xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if service_name is not None:
            xml += ''.join(['<ServiceName>', str(service_name), '</ServiceName>'])
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if description is not None:
            xml += ''.join(['<Description>', str(description), '</Description>'])
        if location is not None:
            xml += ''.join(['<Location>', str(location), '</Location>'])
        if affinity_group is not None:
            xml += ''.join(['<AffinityGroup>', str(affinity_group), '</AffinityGroup>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</CreateHostedService>'
        return xml

    @staticmethod
    def create_deployment_to_xml(name, package_url, label, configuration, start_deployment, treat_warnings_as_error, extended_properties):
        xml = '<CreateDeployment xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if name is not None:
            xml += ''.join(['<Name>', str(name), '</Name>'])
        if package_url is not None:
            xml += ''.join(['<PackageUrl>', str(package_url), '</PackageUrl>'])
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if configuration is not None:
            xml += ''.join(['<Configuration>', str(configuration), '</Configuration>'])
        if start_deployment is not None:
            xml += ''.join(['<StartDeployment>', str(start_deployment).lower(), '</StartDeployment>'])
        if treat_warnings_as_error is not None:
            xml += ''.join(['<TreatWarningsAsError>', str(treat_warnings_as_error).lower(), '</TreatWarningsAsError>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</CreateDeployment>'
        return xml

    @staticmethod
    def swap_deployment_to_xml(production, source_deployment):
        xml = '<Swap xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if production is not None:
            xml += ''.join(['<Production>', str(production), '</Production>'])
        if source_deployment is not None:
            xml += ''.join(['<SourceDeployment>', str(source_deployment), '</SourceDeployment>'])

        xml += '</Swap>'
        return xml

    @staticmethod
    def update_deployment_status_to_xml(status):
        xml = '<UpdateDeploymentStatus xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if status is not None:
            xml += ''.join(['<Status>', str(status), '</Status>'])

        xml += '</UpdateDeploymentStatus>'
        return xml

    @staticmethod
    def change_deployment_to_xml(configuration, treat_warnings_as_error, mode, extended_properties):
        xml = '<ChangeConfiguration xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if configuration is not None:
            xml += ''.join(['<Configuration>', str(configuration), '</Configuration>'])
        if treat_warnings_as_error is not None:
            xml += ''.join(['<TreatWarningsAsError>', str(treat_warnings_as_error).lower(), '</TreatWarningsAsError>'])
        if mode is not None:
            xml += ''.join(['<Mode>', str(mode), '</Mode>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</ChangeConfiguration>'
        return xml

    @staticmethod
    def upgrade_deployment_to_xml(mode, package_url, configuration, label, role_to_upgrade, force, extended_properties):
        xml = '<UpgradeDeployment xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if mode is not None:
            xml += ''.join(['<Mode>', str(mode), '</Mode>'])
        if package_url is not None:
            xml += ''.join(['<PackageUrl>', str(package_url), '</PackageUrl>'])
        if configuration is not None:
            xml += ''.join(['<Configuration>', str(configuration), '</Configuration>'])
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if role_to_upgrade is not None:
            xml += ''.join(['<RoleToUpgrade>', str(role_to_upgrade), '</RoleToUpgrade>'])
        if force is not None:
            xml += ''.join(['<Force>', str(force).lower(), '</Force>'])
        xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)

        xml += '</UpgradeDeployment>'
        return xml

    @staticmethod
    def rollback_upgrade_to_xml(mode, force):
        xml = '<RollbackUpdateOrUpgrade xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if mode is not None:
            xml += ''.join(['<Mode>', str(mode), '</Mode>'])
        if force is not None:
            xml += ''.join(['<Force>', str(force).lower(), '</Force>'])

        xml += '</RollbackUpdateOrUpgrade>'
        return xml

    @staticmethod
    def walk_upgrade_domain_to_xml(upgrade_domain):
        xml = '<WalkUpgradeDomain xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if upgrade_domain is not None:
            xml += ''.join(['<UpgradeDomain>', str(upgrade_domain), '</UpgradeDomain>'])

        xml += '</WalkUpgradeDomain>'
        return xml

    @staticmethod
    def certificate_file_to_xml(data, certificate_format, password):
        xml = '<CertificateFile xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if data is not None:
            xml += ''.join(['<Data>', str(data), '</Data>'])
        if certificate_format is not None:
            xml += ''.join(['<CertificateFormat>', str(certificate_format), '</CertificateFormat>'])
        if password is not None:
            xml += ''.join(['<Password>', str(password), '</Password>'])

        xml += '</CertificateFile>'
        return xml

    @staticmethod
    def create_affinity_group_to_xml(name, label, description, location):
        xml = '<CreateAffinityGroup xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if name is not None:
            xml += ''.join(['<Name>', str(name), '</Name>'])
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if description is not None:
            xml += ''.join(['<Description>', str(description), '</Description>'])
        if location is not None:
            xml += ''.join(['<Location>', str(location), '</Location>'])

        xml += '</CreateAffinityGroup>'
        return xml

    @staticmethod
    def update_affinity_group_to_xml(label, description):
        xml = '<UpdateAffinityGroup xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if label is not None:
            xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        if description is not None:
            xml += ''.join(['<Description>', str(description), '</Description>'])

        xml += '</UpdateAffinityGroup>'
        return xml

    @staticmethod
    def subscription_certificate_to_xml(public_key, thumbprint, data):
        xml = '<SubscriptionCertificate xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if public_key is not None:
            xml += ''.join(['<SubscriptionCertificatePublicKey>', str(public_key), '</SubscriptionCertificatePublicKey>'])
        if thumbprint is not None:
            xml += ''.join(['<SubscriptionCertificateThumbprint>', str(thumbprint), '</SubscriptionCertificateThumbprint>'])
        if data is not None:
            xml += ''.join(['<SubscriptionCertificateData>', str(data), '</SubscriptionCertificateData>'])
        xml += '</SubscriptionCertificate>'
        return xml

    @staticmethod
    def os_image_to_xml(label, media_link, name, os):
        xml = '<OSImage xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if label is not None:
            xml += ''.join(['<Label>', str(label), '</Label>'])
        if media_link is not None:
            xml += ''.join(['<MediaLink>', str(media_link), '</MediaLink>'])
        if name is not None:
            xml += ''.join(['<Name>', str(name), '</Name>'])
        if os is not None:
            xml += ''.join(['<OS>', str(os), '</OS>'])
        xml += '</OSImage>'
        return xml

    @staticmethod
    def data_virtual_hard_disk_to_xml(host_caching, disk_label, disk_name, lun, logical_disk_size_in_gb, media_link, source_media_link):
        xml = '<DataVirtualHardDisk xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if host_caching is not None:
            xml += ''.join(['<HostCaching>', str(host_caching), '</HostCaching>'])
        if disk_label is not None:
            xml += ''.join(['<DiskLabel>', str(disk_label), '</DiskLabel>'])
        if disk_name is not None:
            xml += ''.join(['<DiskName>', str(disk_name), '</DiskName>'])
        if lun is not None:
            xml += ''.join(['<Lun>', str(lun), '</Lun>'])
        if logical_disk_size_in_gb is not None:
            xml += ''.join(['<LogicalDiskSizeInGB>', str(logical_disk_size_in_gb), '</LogicalDiskSizeInGB>'])
        if media_link is not None:
            xml += ''.join(['<MediaLink>', str(media_link), '</MediaLink>'])
        if source_media_link is not None:
            xml += ''.join(['<SourceMediaLink>', str(source_media_link), '</SourceMediaLink>'])
        xml += '</DataVirtualHardDisk>'
        return xml

    @staticmethod
    def disk_to_xml(has_operating_system, label, media_link, name, os):
        xml = '<Disk xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        if has_operating_system is not None:
            xml += ''.join(['<HasOperatingSystem>', str(has_operating_system).lower(), '</HasOperatingSystem>'])
        if label is not None:
            xml += ''.join(['<Label>', str(label), '</Label>'])
        if media_link is not None:
            xml += ''.join(['<MediaLink>', str(media_link), '</MediaLink>'])
        if name is not None:
            xml += ''.join(['<Name>', str(name), '</Name>'])
        if os is not None:
            xml += ''.join(['<OS>', str(os), '</OS>'])
        xml += '</Disk>'
        return xml

    @staticmethod
    def restart_role_operation_to_xml():
        xml = '<RestartRoleOperation xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += '<OperationType>RestartRoleOperation</OperationType>'
        xml += '</RestartRoleOperation>'
        return xml

    @staticmethod
    def shutdown_role_operation_to_xml():
        xml = '<ShutdownRoleOperation xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += '<OperationType>ShutdownRoleOperation</OperationType>'
        xml += '</ShutdownRoleOperation>'
        return xml

    @staticmethod
    def start_role_operation_to_xml():
        xml = '<StartRoleOperation xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += '<OperationType>StartRoleOperation</OperationType>'
        xml += '</StartRoleOperation>'
        return xml

    @staticmethod
    def windows_configuration_to_xml(configuration):
        xml = ''.join(['<ConfigurationSetType>', str(configuration.configuration_set_type), '</ConfigurationSetType>'])
        if configuration.computer_name is not None:
            xml += ''.join(['<ComputerName>', str(configuration.computer_name), '</ComputerName>'])
        if configuration.admin_password is not None:
            xml += ''.join(['<AdminPassword>', base64.b64encode(str(configuration.admin_password)), '</AdminPassword>'])
        if configuration.reset_password_on_first_logon is not None:
            xml += ''.join(['<ResetPasswordOnFirstLogon>', str(configuration.reset_password_on_first_logon).lower(), '</ResetPasswordOnFirstLogon>'])
        if configuration.enable_automatic_updates is not None:
            xml += ''.join(['<EnableAutomaticUpdates>', str(configuration.enable_automatic_updates).lower(), '</EnableAutomaticUpdates>'])
        if configuration.time_zone is not None:
            xml += ''.join(['<TimeZone>', str(configuration.time_zone), '</TimeZone>'])
        if configuration.domain_join is not None:
            xml += '<DomainJoin>'
            xml += '<Credentials>'
            xml += ''.join(['<Domain>', str(configuration.domain_join.credentials.domain), '</Domain>'])
            xml += ''.join(['<Username>', str(configuration.domain_join.credentials.username), '</Username>'])
            xml += ''.join(['<Password>', str(configuration.domain_join.credentials.password), '</Password>'])
            xml += '</Credentials>'
            xml += ''.join(['<JoinDomain>', str(configuration.domain_join.join_domain), '</JoinDomain>'])
            xml += ''.join(['<MachineObjectOU>', str(configuration.domain_join.machine_object_ou), '</MachineObjectOU>'])
            xml += '</DomainJoin>'
        if configuration.stored_certificate_settings is not None:
            xml += '<StoredCertificateSettings>'
            for cert in configuration.stored_certificate_settings:
                xml += '<CertificateSetting>'
                xml += ''.join(['<StoreLocation>', str(cert.store_location), '</StoreLocation>'])
                xml += ''.join(['<StoreName>', str(cert.store_name), '</StoreName>'])
                xml += ''.join(['<Thumbprint>', str(cert.thumbprint), '</Thumbprint>'])
                xml += '</CertificateSetting>'
            xml += '</StoredCertificateSettings>'
        return xml

    @staticmethod
    def linux_configuration_to_xml(configuration):
        xml = ''.join(['<ConfigurationSetType>', str(configuration.configuration_set_type), '</ConfigurationSetType>'])
        if configuration.host_name is not None:
            xml += ''.join(['<HostName>', str(configuration.host_name), '</HostName>'])
        if configuration.user_name is not None:
            xml += ''.join(['<UserName>', str(configuration.user_name), '</UserName>'])
        if configuration.user_password is not None:
            xml += ''.join(['<UserPassword>', str(configuration.user_password), '</UserPassword>'])
        if configuration.disable_ssh_password_authentication is not None:
            xml += ''.join(['<DisableSshPasswordAuthentication>', str(configuration.disable_ssh_password_authentication).lower(), '</DisableSshPasswordAuthentication>'])
        if configuration.ssh is not None:
            xml += '<SSH>'
            xml += '<PublicKeys>'
            for key in configuration.ssh.public_keys:
                xml += '<PublicKey>'
                xml += ''.join(['<FingerPrint>', str(key.finger_print), '</FingerPrint>'])
                xml += ''.join(['<Path>', str(key.path), '</Path>'])
                xml += '</PublicKey>'
            xml += '</PublicKeys>'
            xml += '<KeyPairs>'
            for key in configuration.ssh.key_pairs:
                xml += '<KeyPair>'
                xml += ''.join(['<FingerPrint>', str(key.finger_print), '</FingerPrint>'])
                xml += ''.join(['<Path>', str(key.path), '</Path>'])
                xml += '</KeyPair>'
        
            xml += '</KeyPairs>'
            xml += '</SSH>'
        return xml

    @staticmethod
    def network_configuration_to_xml(configuration):
        xml = ''.join(['<ConfigurationSetType>', str(configuration.configuration_set_type), '</ConfigurationSetType>'])
        xml += '<InputEndpoints>'
        for endpoint in configuration.input_endpoints:
            xml += '<InputEndpoint>'
            xml += ''.join(['<EnableDirectServerReturn>', str(endpoint.enable_direct_server_return).lower(), '</EnableDirectServerReturn>'])
            xml += ''.join(['<LoadBalancedEndpointSetName>', str(endpoint.load_balanced_endpoint_set_name), '</LoadBalancedEndpointSetName>'])
            xml += ''.join(['<LocalPort>', str(endpoint.local_port), '</LocalPort>'])
            xml += ''.join(['<Name>', str(endpoint.name), '</Name>'])
            xml += ''.join(['<Port>', str(endpoint.port), '</Port>'])
            if endpoint.load_balancer_probe.path or endpoint.load_balancer_probe.port or endpoint.load_balancer_probe.protocol:
                xml += '<LoadBalancerProbe>'
                if endpoint.load_balancer_probe.path:
                    xml += ''.join(['<Path>', str(endpoint.load_balancer_probe.path), '</Path>'])
                if endpoint.load_balancer_probe.port:
                    xml += ''.join(['<Port>', str(endpoint.load_balancer_probe.port), '</Port>'])
                if endpoint.load_balancer_probe.protocol:
                    xml += ''.join(['<Protocol>', str(endpoint.load_balancer_probe.protocol), '</Protocol>'])
                xml += '</LoadBalancerProbe>'
            xml += ''.join(['<Protocol>', str(endpoint.protocol), '</Protocol>'])
            xml += '</InputEndpoint>'
        xml += '</InputEndpoints>'
        xml += '<SubnetNames>'
        for name in configuration.subnet_names:
            xml += ''.join(['<SubnetName>', str(name), '</SubnetName>'])
        xml += '</SubnetNames>'
        return xml

    @staticmethod
    def role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, system_configuration_set):
        xml = ''.join(['<RoleName>', str(role_name), '</RoleName>'])
        xml += ''.join(['<RoleType>', str(role_type), '</RoleType>'])
        
        xml += '<ConfigurationSets>'
        
        if system_configuration_set is not None:
            xml += '<ConfigurationSet>'
            if isinstance(system_configuration_set, WindowsConfigurationSet):
                xml += _XmlSerializer.windows_configuration_to_xml(system_configuration_set)
            elif isinstance(system_configuration_set, LinuxConfigurationSet):
                xml += _XmlSerializer.linux_configuration_to_xml(system_configuration_set)
            xml += '</ConfigurationSet>'
        
        if network_configuration_set is not None:
            xml += '<ConfigurationSet>'
            xml += _XmlSerializer.network_configuration_to_xml(network_configuration_set)
            xml += '</ConfigurationSet>'
        
        xml += '</ConfigurationSets>'
        
        if availability_set_name is not None:
            xml += ''.join(['<AvailabilitySetName>', str(availability_set_name), '</AvailabilitySetName>'])
        
        if data_virtual_hard_disks is not None:
            xml += '<DataVirtualHardDisks>'
            for hd in data_virtual_hard_disks:
                xml += '<DataVirtualHardDisk>'
                if hd.host_caching is not None:
                    xml += ''.join(['<HostCaching>', str(hd.host_caching), '</HostCaching>'])
                if hd.disk_label is not None:
                    xml += ''.join(['<DiskLabel>', str(hd.disk_label), '</DiskLabel>'])
                if hd.disk_name is not None:
                    xml += ''.join(['<DiskName>', str(hd.disk_name), '</DiskName>'])
                if hd.lun is not None:
                    xml += ''.join(['<Lun>', str(hd.lun), '</Lun>'])
                if hd.logical_disk_size_in_gb is not None:
                    xml += ''.join(['<LogicalDiskSizeInGB>', str(hd.logical_disk_size_in_gb), '</LogicalDiskSizeInGB>'])
                if hd.media_link is not None:
                    xml += ''.join(['<MediaLink>', str(hd.media_link), '</MediaLink>'])
                xml += '</DataVirtualHardDisk>'
            xml += '</DataVirtualHardDisks>'
        
        if os_virtual_hard_disk is not None:
            xml += '<OSVirtualHardDisk>'
            if os_virtual_hard_disk.host_caching is not None:
                xml += ''.join(['<HostCaching>', str(os_virtual_hard_disk.host_caching), '</HostCaching>'])
            if os_virtual_hard_disk.disk_label is not None:
                xml += ''.join(['<DiskLabel>', str(os_virtual_hard_disk.disk_label), '</DiskLabel>'])
            if os_virtual_hard_disk.disk_name is not None:
                xml += ''.join(['<DiskName>', str(os_virtual_hard_disk.disk_name), '</DiskName>'])
            if os_virtual_hard_disk.media_link is not None:
                xml += ''.join(['<MediaLink>', str(os_virtual_hard_disk.media_link), '</MediaLink>'])
            if os_virtual_hard_disk.source_image_name is not None:
                xml += ''.join(['<SourceImageName>', str(os_virtual_hard_disk.source_image_name), '</SourceImageName>'])
            xml += '</OSVirtualHardDisk>'
        
        if role_size is not None:
            xml += ''.join(['<RoleSize>', str(role_size), '</RoleSize>'])
        
        return xml

    @staticmethod
    def add_role_to_xml(role_name, system_configuration_set, os_virtual_hard_disk, role_type, network_configuration_set, availability_set_name, data_virtual_hard_disks, role_size):
        xml = '<PersistentVMRole xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += _XmlSerializer.role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, system_configuration_set)
        xml += '</PersistentVMRole>'

        return xml

    @staticmethod
    def update_role_to_xml(role_name, os_virtual_hard_disk, role_type, network_configuration_set, availability_set_name, data_virtual_hard_disks, role_size):
        xml = '<PersistentVMRole xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += _XmlSerializer.role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, None)
        xml += '</PersistentVMRole>'
        
        return xml

    @staticmethod
    def capture_role_to_xml(post_capture_action, target_image_name, target_image_label, provisioning_configuration):
        xml = '<CaptureRoleOperation xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += '<OperationType>CaptureRoleOperation</OperationType>'
        xml += ''.join(['<PostCaptureAction>', str(post_capture_action), '</PostCaptureAction>'])
        if provisioning_configuration is not None:
            xml += '<ProvisioningConfiguration>'
            if isinstance(provisioning_configuration, WindowsConfigurationSet):
                xml += _XmlSerializer.windows_configuration_to_xml(provisioning_configuration)
            elif isinstance(provisioning_configuration, LinuxConfigurationSet):
                xml += _XmlSerializer.linux_configuration_to_xml(provisioning_configuration)
            xml += '</ProvisioningConfiguration>'
        xml += ''.join(['<TargetImageLabel>', str(target_image_label), '</TargetImageLabel>'])
        xml += ''.join(['<TargetImageName>', str(target_image_name), '</TargetImageName>'])
        xml += '</CaptureRoleOperation>'

        return xml

    @staticmethod
    def virtual_machine_deployment_to_xml(deployment_name, deployment_slot, label, role_name, system_configuration_set, os_virtual_hard_disk, role_type, network_configuration_set, availability_set_name, data_virtual_hard_disks, role_size):
        xml = '<Deployment xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        xml += ''.join(['<Name>', str(deployment_name), '</Name>'])
        xml += ''.join(['<DeploymentSlot>', str(deployment_slot), '</DeploymentSlot>'])
        xml += ''.join(['<Label>', base64.b64encode(str(label)), '</Label>'])
        xml += '<RoleList>'
        xml += '<Role>'
        xml += _XmlSerializer.role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, system_configuration_set)
        xml += '</Role>'
        xml += '</RoleList>'
        xml += '</Deployment>'
        
        return xml

from azure.servicemanagement.servicemanagementservice import ServiceManagementService
