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
import base64
from azure.http import HTTPError
from azure import (WindowsAzureError, WindowsAzureData, _general_error_handler,
                          _str, _list_of, _scalar_list_of, _dict_of, _Base64String)
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
        self.description = u''
        self.affinity_group = u''
        self.location = u''
        self.label = _Base64String()
        self.status = u''
        self.endpoints = _scalar_list_of(str, 'Endpoint')
        self.geo_replication_enabled = False
        self.geo_primary_region = u''
        self.status_of_primary = u''
        self.geo_secondary_region = u''
        self.status_of_secondary = u''
        self.last_geo_failover_time = u''

class StorageServiceKeys(WindowsAzureData):
    def __init__(self):
        self.primary = u''
        self.secondary = u''

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
        self.name = u''
        self.display_name = u''
        self.available_services = _scalar_list_of(str, 'AvailableService')

class AffinityGroup(WindowsAzureData):
    def __init__(self):
        self.name = ''
        self.label = _Base64String()
        self.description = u''
        self.location = u''
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
        self.url = u''
        self.service_name = u''
        self.hosted_service_properties = HostedServiceProperties()
        self.deployments = Deployments()

class HostedServiceProperties(WindowsAzureData):
    def __init__(self):
        self.description = u''
        self.location = u''
        self.affinity_group = u''
        self.label = _Base64String()
        self.status = u''
        self.date_created = u''
        self.date_last_modified = u''
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
        self.name = u''
        self.deployment_slot = u''
        self.private_id = u''
        self.status = u''
        self.label = _Base64String()
        self.url = u''
        self.configuration = _Base64String()
        self.role_instance_list = RoleInstanceList()
        self.upgrade_status = UpgradeStatus()
        self.upgrade_domain_count = u''
        self.role_list = RoleList()
        self.sdk_version = u''
        self.input_endpoint_list = InputEndpoints()
        self.locked = False
        self.rollback_allowed = False
        self.persistent_vm_downtime_info = PersistentVMDowntimeInfo()
        self.created_time = u''
        self.last_modified_time = u''
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
        self.role_name = u''
        self.instance_name = u''
        self.instance_status = u''
        self.instance_upgrade_domain = 0
        self.instance_fault_domain = 0
        self.instance_size = u''
        self.instance_state_details = u''
        self.instance_error_code = u''
        self.ip_address = u''
        self.power_state = u''
        self.fqdn = u''

class UpgradeStatus(WindowsAzureData):
    def __init__(self):
        self.upgrade_type = u''
        self.current_upgrade_domain_state = u''
        self.current_upgrade_domain = u''

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
        self.role_name = u''
        self.vip = u''
        self.port = u''

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
        self.role_name = u''
        self.os_version = u''

class PersistentVMDowntimeInfo(WindowsAzureData):
    def __init__(self):
        self.start_time = u''
        self.end_time = u''
        self.status = u''

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
        self.certificate_url = u''
        self.thumbprint = u''
        self.thumbprint_algorithm = u''
        self.data = u''

class OperationError(WindowsAzureData):
    def __init__(self):
        self.code = u''
        self.message = u''
        
class Operation(WindowsAzureData):
    def __init__(self):
        self.id = u''
        self.status = u''
        self.http_status_code = u''
        self.error = OperationError()

class OperatingSystem(WindowsAzureData):
    def __init__(self):
        self.version = u''
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
        self.name = u''
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
        self.subscription_id = u''
        self.subscription_name = u''
        self.subscription_status = u''
        self.account_admin_live_email_id = u''
        self.service_admin_live_email_id = u''
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
        self.subscription_certificate_public_key = u''
        self.subscription_certificate_thumbprint = u''
        self.subscription_certificate_data = u''
        self.created = u''

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
        self.affinity_group = u''
        self.category = u''
        self.location = u''
        self.logical_size_in_gb = 0
        self.label = u''
        self.media_link = u''
        self.name = u''
        self.os = u''
        self.eula = u''
        self.description = u''

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
        self.affinity_group = u''
        self.attached_to = AttachedTo()
        self.has_operating_system = u''
        self.is_corrupted = u''
        self.location = u''
        self.logical_disk_size_in_gb = 0
        self.label = u''
        self.media_link = u''
        self.name = u''
        self.os = u''
        self.source_image_name = u''

class AttachedTo(WindowsAzureData):
    def __init__(self):
        self.hosted_service_name = u''
        self.deployment_name = u''
        self.role_name = u''

class PersistentVMRole(WindowsAzureData):
    def __init__(self):
        self.role_name = u''
        self.role_type= u''
        self.os_version = u'' # undocumented
        self.configuration_sets = ConfigurationSets()
        self.availability_set_name = u''
        self.data_virtual_hard_disks = DataVirtualHardDisks()
        self.os_virtual_hard_disk = OSVirtualHardDisk()
        self.role_size = u''

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
        self.configuration_set_type = u''
        self.role_type= u''
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
    def __init__(self, name=u'', protocol=u'', port=u'', local_port=u'', load_balanced_endpoint_set_name=u'', enable_direct_server_return=False):
        self.enable_direct_server_return = enable_direct_server_return
        self.load_balanced_endpoint_set_name = load_balanced_endpoint_set_name
        self.local_port = local_port
        self.name = name
        self.port = port
        self.load_balancer_probe = LoadBalancerProbe()
        self.protocol = protocol

class WindowsConfigurationSet(WindowsAzureData):
    def __init__(self, computer_name=None, admin_password=None, reset_password_on_first_logon=None, enable_automatic_updates=None, time_zone=None):
        self.configuration_set_type = u'WindowsProvisioningConfiguration'
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
        self.join_domain = u''
        self.machine_object_ou = u''

class Credentials(WindowsAzureData):
    def __init(self):
        self.domain = u''
        self.username = u''
        self.password = u''

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
    def __init__(self, thumbprint=u'', store_name=u'', store_location=u''):
        self.thumbprint = thumbprint
        self.store_name = store_name
        self.store_location = store_location

class LinuxConfigurationSet(WindowsAzureData):
    def __init__(self, host_name=None, user_name=None, user_password=None, disable_ssh_password_authentication=None):
        self.configuration_set_type = u'LinuxProvisioningConfiguration'
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
        self.finger_print = u''
        self.path = u''

class LoadBalancerProbe(WindowsAzureData):
    def __init__(self):
        self.path = u''
        self.port = u''
        self.protocol = u''

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
        self.host_caching = u''
        self.disk_label = u''
        self.disk_name = u''
        self.lun = 0
        self.logical_disk_size_in_gb = 0
        self.media_link = u''

class OSVirtualHardDisk(WindowsAzureData):
    def __init__(self, source_image_name=None, media_link=None, host_caching=None, disk_label=None, disk_name=None):
        self.source_image_name = source_image_name
        self.media_link = media_link
        self.host_caching = host_caching
        self.disk_label = disk_label
        self.disk_name = disk_name
        self.os = u'' # undocumented, not used when adding a role

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
    return _general_error_handler(http_error)

def _lower(text):
    return text.lower()

class _XmlSerializer(object):
    @staticmethod
    def create_storage_service_input_to_xml(service_name, description, label, affinity_group, location, geo_replication_enabled, extended_properties):
        return _XmlSerializer.doc_from_data('CreateStorageServiceInput',
                                            [('ServiceName', service_name),
                                             ('Description', description),
                                             ('Label', label, base64.b64encode),
                                             ('AffinityGroup', affinity_group),
                                             ('Location', location),
                                             ('GeoReplicationEnabled', geo_replication_enabled, _lower)],
                                            extended_properties)

    @staticmethod
    def update_storage_service_input_to_xml(description, label, geo_replication_enabled, extended_properties):
        return _XmlSerializer.doc_from_data('UpdateStorageServiceInput',
                                            [('Description', description),
                                             ('Label', label, base64.b64encode),
                                             ('GeoReplicationEnabled', geo_replication_enabled, _lower)],
                                            extended_properties)

    @staticmethod
    def regenerate_keys_to_xml(key_type):
        return _XmlSerializer.doc_from_data('RegenerateKeys',
                                            [('KeyType', key_type)])

    @staticmethod
    def update_hosted_service_to_xml(label, description, extended_properties):
        return _XmlSerializer.doc_from_data('UpdateHostedService',
                                            [('Label', label, base64.b64encode),
                                             ('Description', description)],
                                            extended_properties)

    @staticmethod
    def create_hosted_service_to_xml(service_name, label, description, location, affinity_group, extended_properties):
        return _XmlSerializer.doc_from_data('CreateHostedService',
                                            [('ServiceName', service_name),
                                             ('Label', label, base64.b64encode),
                                             ('Description', description),
                                             ('Location', location),
                                             ('AffinityGroup', affinity_group)],
                                            extended_properties)

    @staticmethod
    def create_deployment_to_xml(name, package_url, label, configuration, start_deployment, treat_warnings_as_error, extended_properties):
        return _XmlSerializer.doc_from_data('CreateDeployment',
                                            [('Name', name),
                                             ('PackageUrl', package_url),
                                             ('Label', label, base64.b64encode),
                                             ('Configuration', configuration),
                                             ('StartDeployment', start_deployment, _lower),
                                             ('TreatWarningsAsError', treat_warnings_as_error, _lower)],
                                            extended_properties)

    @staticmethod
    def swap_deployment_to_xml(production, source_deployment):
        return _XmlSerializer.doc_from_data('Swap',
                                            [('Production', production),
                                             ('SourceDeployment', source_deployment)])

    @staticmethod
    def update_deployment_status_to_xml(status):
        return _XmlSerializer.doc_from_data('UpdateDeploymentStatus',
                                            [('Status', status)])

    @staticmethod
    def change_deployment_to_xml(configuration, treat_warnings_as_error, mode, extended_properties):
        return _XmlSerializer.doc_from_data('ChangeConfiguration',
                                            [('Configuration', configuration),
                                             ('TreatWarningsAsError', treat_warnings_as_error, _lower),
                                             ('Mode', mode)],
                                            extended_properties)

    @staticmethod
    def upgrade_deployment_to_xml(mode, package_url, configuration, label, role_to_upgrade, force, extended_properties):
        return _XmlSerializer.doc_from_data('UpgradeDeployment',
                                            [('Mode', mode),
                                             ('PackageUrl', package_url),
                                             ('Configuration', configuration),
                                             ('Label', label, base64.b64encode),
                                             ('RoleToUpgrade', role_to_upgrade),
                                             ('Force', force, _lower)],
                                            extended_properties)

    @staticmethod
    def rollback_upgrade_to_xml(mode, force):
        return _XmlSerializer.doc_from_data('RollbackUpdateOrUpgrade',
                                            [('Mode', mode),
                                             ('Force', force, _lower)])

    @staticmethod
    def walk_upgrade_domain_to_xml(upgrade_domain):
        return _XmlSerializer.doc_from_data('WalkUpgradeDomain',
                                            [('UpgradeDomain', upgrade_domain)])

    @staticmethod
    def certificate_file_to_xml(data, certificate_format, password):
        return _XmlSerializer.doc_from_data('CertificateFile',
                                            [('Data', data),
                                             ('CertificateFormat', certificate_format),
                                             ('Password', password)])

    @staticmethod
    def create_affinity_group_to_xml(name, label, description, location):
        return _XmlSerializer.doc_from_data('CreateAffinityGroup',
                                            [('Name', name),
                                             ('Label', label, base64.b64encode),
                                             ('Description', description),
                                             ('Location', location)])

    @staticmethod
    def update_affinity_group_to_xml(label, description):
        return _XmlSerializer.doc_from_data('UpdateAffinityGroup',
                                            [('Label', label, base64.b64encode),
                                             ('Description', description)])

    @staticmethod
    def subscription_certificate_to_xml(public_key, thumbprint, data):
        return _XmlSerializer.doc_from_data('SubscriptionCertificate',
                                            [('SubscriptionCertificatePublicKey', public_key),
                                             ('SubscriptionCertificateThumbprint', thumbprint),
                                             ('SubscriptionCertificateData', data)])

    @staticmethod
    def os_image_to_xml(label, media_link, name, os):
        return _XmlSerializer.doc_from_data('OSImage',
                                            [('Label', label),
                                             ('MediaLink', media_link),
                                             ('Name', name),
                                             ('OS', os)])

    @staticmethod
    def data_virtual_hard_disk_to_xml(host_caching, disk_label, disk_name, lun, logical_disk_size_in_gb, media_link, source_media_link):
        return _XmlSerializer.doc_from_data('DataVirtualHardDisk',
                                            [('HostCaching', host_caching),
                                             ('DiskLabel', disk_label),
                                             ('DiskName', disk_name),
                                             ('Lun', lun),
                                             ('LogicalDiskSizeInGB', logical_disk_size_in_gb),
                                             ('MediaLink', media_link),
                                             ('SourceMediaLink', source_media_link)])

    @staticmethod
    def disk_to_xml(has_operating_system, label, media_link, name, os):
        return _XmlSerializer.doc_from_data('Disk',
                                            [('HasOperatingSystem', has_operating_system, _lower),
                                             ('Label', label),
                                             ('MediaLink', media_link),
                                             ('Name', name),
                                             ('OS', os)])

    @staticmethod
    def restart_role_operation_to_xml():
        return _XmlSerializer.doc_from_xml('RestartRoleOperation',
                                           '<OperationType>RestartRoleOperation</OperationType>')

    @staticmethod
    def shutdown_role_operation_to_xml():
        return _XmlSerializer.doc_from_xml('ShutdownRoleOperation',
                                           '<OperationType>ShutdownRoleOperation</OperationType>')

    @staticmethod
    def start_role_operation_to_xml():
        return _XmlSerializer.doc_from_xml('StartRoleOperation',
                                           '<OperationType>StartRoleOperation</OperationType>')

    @staticmethod
    def windows_configuration_to_xml(configuration):
        xml = _XmlSerializer.data_to_xml([('ConfigurationSetType', configuration.configuration_set_type),
                                          ('ComputerName', configuration.computer_name),
                                          ('AdminPassword', configuration.admin_password, base64.b64encode),
                                          ('ResetPasswordOnFirstLogon', configuration.reset_password_on_first_logon, _lower),
                                          ('EnableAutomaticUpdates', configuration.enable_automatic_updates, _lower),
                                          ('TimeZone', configuration.time_zone)])

        if configuration.domain_join is not None:
            xml += '<DomainJoin>'
            xml += '<Credentials>'
            xml += _XmlSerializer.data_to_xml([('Domain', configuration.domain_join.credentials.domain),
                                               ('Username', configuration.domain_join.credentials.username),
                                               ('Password', configuration.domain_join.credentials.password)])
            xml += '</Credentials>'
            xml += _XmlSerializer.data_to_xml([('JoinDomain', configuration.domain_join.join_domain),
                                               ('MachineObjectOU', configuration.domain_join.machine_object_ou)])
            xml += '</DomainJoin>'
        if configuration.stored_certificate_settings is not None:
            xml += '<StoredCertificateSettings>'
            for cert in configuration.stored_certificate_settings:
                xml += '<CertificateSetting>'
                xml += _XmlSerializer.data_to_xml([('StoreLocation', cert.store_location),
                                                   ('StoreName', cert.store_name),
                                                   ('Thumbprint', cert.thumbprint)])
                xml += '</CertificateSetting>'
            xml += '</StoredCertificateSettings>'
        return xml

    @staticmethod
    def linux_configuration_to_xml(configuration):
        xml = _XmlSerializer.data_to_xml([('ConfigurationSetType', configuration.configuration_set_type),
                                          ('HostName', configuration.host_name),
                                          ('UserName', configuration.user_name),
                                          ('UserPassword', configuration.user_password),
                                          ('DisableSshPasswordAuthentication', configuration.disable_ssh_password_authentication, _lower)])

        if configuration.ssh is not None:
            xml += '<SSH>'
            xml += '<PublicKeys>'
            for key in configuration.ssh.public_keys:
                xml += '<PublicKey>'
                xml += _XmlSerializer.data_to_xml([('FingerPrint', key.finger_print),
                                                   ('Path', key.path)])
                xml += '</PublicKey>'
            xml += '</PublicKeys>'
            xml += '<KeyPairs>'
            for key in configuration.ssh.key_pairs:
                xml += '<KeyPair>'
                xml += _XmlSerializer.data_to_xml([('FingerPrint', key.finger_print),
                                                   ('Path', key.path)])
                xml += '</KeyPair>'
            xml += '</KeyPairs>'
            xml += '</SSH>'
        return xml

    @staticmethod
    def network_configuration_to_xml(configuration):
        xml = _XmlSerializer.data_to_xml([('ConfigurationSetType', configuration.configuration_set_type)])
        xml += '<InputEndpoints>'
        for endpoint in configuration.input_endpoints:
            xml += '<InputEndpoint>'
            xml += _XmlSerializer.data_to_xml([('EnableDirectServerReturn', endpoint.enable_direct_server_return, _lower),
                                               ('LoadBalancedEndpointSetName', endpoint.load_balanced_endpoint_set_name),
                                               ('LocalPort', endpoint.local_port),
                                               ('Name', endpoint.name),
                                               ('Port', endpoint.port)])

            if endpoint.load_balancer_probe.path or endpoint.load_balancer_probe.port or endpoint.load_balancer_probe.protocol:
                xml += '<LoadBalancerProbe>'
                xml += _XmlSerializer.data_to_xml([('Path', endpoint.load_balancer_probe.path),
                                                   ('Port', endpoint.load_balancer_probe.port),
                                                   ('Protocol', endpoint.load_balancer_probe.protocol)])
                xml += '</LoadBalancerProbe>'

            xml += _XmlSerializer.data_to_xml([('Protocol', endpoint.protocol)])
            xml += '</InputEndpoint>'
        xml += '</InputEndpoints>'
        xml += '<SubnetNames>'
        for name in configuration.subnet_names:
            xml += _XmlSerializer.data_to_xml([('SubnetName', name)])
        xml += '</SubnetNames>'
        return xml

    @staticmethod
    def role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, system_configuration_set):
        xml = _XmlSerializer.data_to_xml([('RoleName', role_name),
                                          ('RoleType', role_type)])

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
            xml += _XmlSerializer.data_to_xml([('AvailabilitySetName', availability_set_name)])
        
        if data_virtual_hard_disks is not None:
            xml += '<DataVirtualHardDisks>'
            for hd in data_virtual_hard_disks:
                xml += '<DataVirtualHardDisk>'
                xml += _XmlSerializer.data_to_xml([('HostCaching', hd.host_caching),
                                                   ('DiskLabel', hd.disk_label),
                                                   ('DiskName', hd.disk_name),
                                                   ('Lun', hd.lun),
                                                   ('LogicalDiskSizeInGB', hd.logical_disk_size_in_gb),
                                                   ('MediaLink', hd.media_link)])
                xml += '</DataVirtualHardDisk>'
            xml += '</DataVirtualHardDisks>'
        
        if os_virtual_hard_disk is not None:
            xml += '<OSVirtualHardDisk>'
            xml += _XmlSerializer.data_to_xml([('HostCaching', os_virtual_hard_disk.host_caching),
                                               ('DiskLabel', os_virtual_hard_disk.disk_label),
                                               ('DiskName', os_virtual_hard_disk.disk_name),
                                               ('MediaLink', os_virtual_hard_disk.media_link),
                                               ('SourceImageName', os_virtual_hard_disk.source_image_name)])
            xml += '</OSVirtualHardDisk>'
        
        if role_size is not None:
            xml += _XmlSerializer.data_to_xml([('RoleSize', role_size)])
        
        return xml

    @staticmethod
    def add_role_to_xml(role_name, system_configuration_set, os_virtual_hard_disk, role_type, network_configuration_set, availability_set_name, data_virtual_hard_disks, role_size):
        xml = _XmlSerializer.role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, system_configuration_set)
        return _XmlSerializer.doc_from_xml('PersistentVMRole', xml)

    @staticmethod
    def update_role_to_xml(role_name, os_virtual_hard_disk, role_type, network_configuration_set, availability_set_name, data_virtual_hard_disks, role_size):
        xml = _XmlSerializer.role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, None)
        return _XmlSerializer.doc_from_xml('PersistentVMRole', xml)

    @staticmethod
    def capture_role_to_xml(post_capture_action, target_image_name, target_image_label, provisioning_configuration):
        xml = _XmlSerializer.data_to_xml([('OperationType', 'CaptureRoleOperation'),
                                          ('PostCaptureAction', post_capture_action)])
        if provisioning_configuration is not None:
            xml += '<ProvisioningConfiguration>'
            if isinstance(provisioning_configuration, WindowsConfigurationSet):
                xml += _XmlSerializer.windows_configuration_to_xml(provisioning_configuration)
            elif isinstance(provisioning_configuration, LinuxConfigurationSet):
                xml += _XmlSerializer.linux_configuration_to_xml(provisioning_configuration)
            xml += '</ProvisioningConfiguration>'
        xml += _XmlSerializer.data_to_xml([('TargetImageLabel', target_image_label),
                                           ('TargetImageName', target_image_name)])
        return _XmlSerializer.doc_from_xml('CaptureRoleOperation', xml)

    @staticmethod
    def virtual_machine_deployment_to_xml(deployment_name, deployment_slot, label, role_name, system_configuration_set, os_virtual_hard_disk, role_type, network_configuration_set, availability_set_name, data_virtual_hard_disks, role_size):
        xml = _XmlSerializer.data_to_xml([('Name', deployment_name),
                                          ('DeploymentSlot', deployment_slot),
                                          ('Label', label, base64.b64encode)])
        xml += '<RoleList>'
        xml += '<Role>'
        xml += _XmlSerializer.role_to_xml(availability_set_name, data_virtual_hard_disks, network_configuration_set, os_virtual_hard_disk, role_name, role_size, role_type, system_configuration_set)
        xml += '</Role>'
        xml += '</RoleList>'
        return _XmlSerializer.doc_from_xml('Deployment', xml)

    @staticmethod
    def data_to_xml(data):
        '''Creates an xml fragment from the specified data.
           data: Array of tuples, where first: xml element name
                                        second: xml element text
                                        third: conversion function
        '''
        xml = ''
        for element in data:
            name = element[0]
            val = element[1]
            if len(element) > 2:
                converter = element[2]
            else:
                converter = None

            if val is not None:
                if converter is not None:
                    text = converter(_str(val))
                else:
                    text = _str(val)
                xml += ''.join(['<', name, '>', text, '</', name, '>'])
        return xml

    @staticmethod
    def doc_from_xml(document_element_name, inner_xml):
        '''Wraps the specified xml in an xml root element with default azure namespaces'''
        xml = ''.join(['<', document_element_name, ' xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'])
        xml += inner_xml
        xml += ''.join(['</', document_element_name, '>'])
        return xml

    @staticmethod
    def doc_from_data(document_element_name, data, extended_properties=None):
        xml = _XmlSerializer.data_to_xml(data)
        if extended_properties is not None:
            xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(extended_properties)
        return _XmlSerializer.doc_from_xml(document_element_name, xml)

    @staticmethod
    def extended_properties_dict_to_xml_fragment(extended_properties):
        xml = ''
        if extended_properties is not None and len(extended_properties) > 0:
            xml += '<ExtendedProperties>'
            for key, val in extended_properties.items():
                xml += ''.join(['<ExtendedProperty>', '<Name>', _str(key), '</Name>', '<Value>', _str(val), '</Value>', '</ExtendedProperty>'])
            xml += '</ExtendedProperties>'
        return xml

from azure.servicemanagement.servicemanagementservice import ServiceManagementService
