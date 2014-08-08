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
import os
import time
import unittest

from azure.servicemanagement import (
    CertificateSetting,
    ConfigurationSet,
    ConfigurationSetInputEndpoint,
    KeyPair,
    LinuxConfigurationSet,
    Listener,
    OSVirtualHardDisk,
    PublicKey,
    ServiceManagementService,
    WindowsConfigurationSet,
    )
from azure.storage.blobservice import BlobService
from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
    )

SERVICE_CERT_FORMAT = 'pfx'
SERVICE_CERT_PASSWORD = 'Python'
SERVICE_CERT_DATA = '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'
SERVICE_CERT_DATA_PUBLIC = 'MIIC9jCCAeKgAwIBAgIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAMBUxEzARBgNVBAMTClB5dGhvblRlc3QwHhcNMTIwODMwMDAyNTMzWhcNMzkxMjMxMjM1OTU5WjAVMRMwEQYDVQQDEwpQeXRob25UZXN0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsjULNM53WPLkht1rbrDob/e4hZTHzj/hlLoBt2X3cNRc6dOPsMucxbMdchbCqAFa5RIaJvF5NDKqZuUSwq6bttD71twzy9bQ03EySOcRBad1VyqAZQ8DL8nUGSnXIUh+tpz4fDGM5f3Ly9NX8zfGqG3sT635rrFlUp3meJC+secCCwTLOOcIs3KQmuB+pMB5Y9rPhoxcekFfpq1pKtis6pmxnVbiL49kr6UUL6RQRDwik4t1jttatXLZqHETTmXl0Y0wS5AcJUXVAn5AL2kybULoThop2v01/E0NkPtFPAqLVs/kKBahniNn9uwUo+LS9FA8rWGu0FY4CZEYDfhb+QIDAQABo0owSDBGBgNVHQEEPzA9gBBS6knRHo54LppngxVCCzZVoRcwFTETMBEGA1UEAxMKUHl0aG9uVGVzdIIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAA4IBAQAnZbP3YV+08wI4YTg6MOVA+j1njd0kVp35FLehripmaMNE6lgk3Vu1MGGl0JnvMr3fNFGFzRske/jVtFxlHE5H/CoUzmyMQ+W06eV/e995AduwTKsS0ZgYn0VoocSXWst/nyhpKOcbJgAOohOYxgsGI1JEqQgjyeqzcCIhw/vlWiA3V8bSiPnrC9vwhH0eB025hBd2VbEGDz2nWCYkwtuOLMTvkmLi/oFw3GOfgagZKk8k/ZPffMCafz+yR3vb1nqAjncrVcJLI8amUfpxhjZYexo8MbxBA432M6w8sjXN+uLCl7ByWZ4xs4vonWgkmjeObtU37SIzolHT4dxIgaP2'
SERVICE_CERT_THUMBPRINT = 'BEA4B74BD6B915E9DD6A01FB1B8C3C1740F517F2'
SERVICE_CERT_THUMBALGO = 'sha1'

DEPLOYMENT_ORIGINAL_CONFIG = '''<ServiceConfiguration serviceName="WindowsAzure1" xmlns="http://schemas.microsoft.com/ServiceHosting/2008/10/ServiceConfiguration" osFamily="1" osVersion="*" schemaVersion="2012-05.1.7">
  <Role name="WorkerRole1">
    <Instances count="2" />
    <ConfigurationSettings>
      <Setting name="Microsoft.WindowsAzure.Plugins.Diagnostics.ConnectionString" value="UseDevelopmentStorage=true" />
    </ConfigurationSettings>
  </Role>
</ServiceConfiguration>'''

DEPLOYMENT_UPDATE_CONFIG = '''<ServiceConfiguration serviceName="WindowsAzure1" xmlns="http://schemas.microsoft.com/ServiceHosting/2008/10/ServiceConfiguration" osFamily="1" osVersion="*" schemaVersion="2012-05.1.7">
  <Role name="WorkerRole1">
    <Instances count="4" />
    <ConfigurationSettings>
      <Setting name="Microsoft.WindowsAzure.Plugins.Diagnostics.ConnectionString" value="UseDevelopmentStorage=true" />
    </ConfigurationSettings>
  </Role>
</ServiceConfiguration>'''

CSPKG_PATH = 'data/WindowsAzure1.cspkg'
DATA_VHD_PATH = 'data/testhd'

# This blob must be created manually before running the unit tests,
# they must be present in the storage account listed in the credentials file.
LINUX_OS_VHD_URL = credentials.getLinuxOSVHD()

# The easiest way to create a Linux OS vhd is to use the Azure management
# portal to create a Linux VM, and have it store the VHD in the
# storage account listed in the credentials file.  Then stop the VM,
# and use the following code to copy the VHD to another blob (if you
# try to use the VM's VHD directly without making a copy, you will get
# conflict errors).

# sourceblob = '/{0}/{1}/{2}'.format(credentials.getStorageServicesName(), 'vhdcontainername', 'vhdblobname')
# self.bc.copy_blob('vhdcontainername', 'targetvhdblobname', sourceblob)
#
# in the credentials file, set:
#    "linuxosvhd" : "http://storageservicesname.blob.core.windows.net/vhdcontainername/targetvhdblobname",


#------------------------------------------------------------------------------
class ServiceManagementServiceTest(AzureTestCase):

    def setUp(self):
        self.sms = ServiceManagementService(credentials.getSubscriptionId(),
                                            credentials.getManagementCertFile())
        set_service_options(self.sms)

        self.bc = BlobService(credentials.getStorageServicesName(),
                              credentials.getStorageServicesKey())
        set_service_options(self.bc)

        self.hosted_service_name = getUniqueName('utsvc')
        self.container_name = getUniqueName('utctnr')
        self.disk_name = getUniqueName('utdisk')
        self.os_image_name = getUniqueName('utosimg')
        self.data_disk_info = None

    def tearDown(self):
        if self.data_disk_info is not None:
            try:
                disk = self.sms.get_data_disk(
                    self.data_disk_info[0], self.data_disk_info[1],
                    self.data_disk_info[2], self.data_disk_info[3])
                try:
                    result = self.sms.delete_data_disk(
                        self.data_disk_info[0], self.data_disk_info[1],
                        self.data_disk_info[2], self.data_disk_info[3])
                    self._wait_for_async(result.request_id)
                except:
                    pass
                try:
                    self.sms.delete_disk(disk.disk_name)
                except:
                    pass
            except:
                pass

        disk_names = [self.disk_name]

        try:
            # Can't delete a hosted service if it has deployments, so delete
            # those first
            props = self.sms.get_hosted_service_properties(
                self.hosted_service_name, True)
            for deployment in props.deployments:
                try:
                    for role in deployment.role_list:
                        role_props = self.sms.get_role(
                            self.hosted_service_name,
                            deployment.name,
                            role.role_name)
                        if role_props.os_virtual_hard_disk.disk_name \
                            not in disk_names:
                            disk_names.append(
                                role_props.os_virtual_hard_disk.disk_name)
                except:
                    pass

                try:
                    result = self.sms.delete_deployment(
                        self.hosted_service_name, deployment.name)
                    self._wait_for_async(result.request_id)
                except:
                    pass
            self.sms.delete_hosted_service(self.hosted_service_name)
        except:
            pass

        try:
            result = self.sms.delete_os_image(self.os_image_name)
            self._wait_for_async(result.request_id)
        except:
            pass

        for disk_name in disk_names:
            try:
                self.sms.delete_disk(disk_name)
            except:
                pass

        try:
            self.bc.delete_container(self.container_name)
        except:
            pass

    #--Helpers-----------------------------------------------------------------
    def _wait_for_async(self, request_id):
        count = 0
        result = self.sms.get_operation_status(request_id)
        while result.status == 'InProgress':
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False, 'Timed out waiting for async operation to complete.')
            time.sleep(5)
            result = self.sms.get_operation_status(request_id)
        self.assertEqual(result.status, 'Succeeded')

    def _wait_for_deployment(self, service_name, deployment_name,
                             status='Running'):
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while props.status != status:
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False, 'Timed out waiting for deployment status.')
            time.sleep(5)
            props = self.sms.get_deployment_by_name(
                service_name, deployment_name)

    def _wait_for_role(self, service_name, deployment_name, role_instance_name,
                       status='ReadyRole'):
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while self._get_role_instance_status(props, role_instance_name) != status:
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False, 'Timed out waiting for role instance status.')
            time.sleep(5)
            props = self.sms.get_deployment_by_name(
                service_name, deployment_name)

    def _wait_for_rollback_allowed(self, service_name, deployment_name):
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while props.rollback_allowed == False:
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False, 'Timed out waiting for rollback allowed.')
            time.sleep(5)
            props = self.sms.get_deployment_by_name(
                service_name, deployment_name)

    def _get_role_instance_status(self, deployment, role_instance_name):
        for role_instance in deployment.role_instance_list:
            if role_instance.instance_name == role_instance_name:
                return role_instance.instance_status
        return None

    def _create_hosted_service(self, name, location=None, affinity_group=None):
        if not location and not affinity_group:
            location = 'West US'

        result = self.sms.create_hosted_service(
            name,
            name + 'label',
            name + 'description',
            location,
            affinity_group,
            {'ext1': 'val1', 'ext2': 42})
        self.assertIsNone(result)

    def _hosted_service_exists(self, name):
        try:
            props = self.sms.get_hosted_service_properties(name)
            return props is not None
        except:
            return False

    def _create_service_certificate(self, service_name, data, format,
                                    password):
        result = self.sms.add_service_certificate(service_name, data,
                                                  format, password)
        self._wait_for_async(result.request_id)

    def _service_certificate_exists(self, service_name, thumbalgorithm,
                                    thumbprint):
        try:
            props = self.sms.get_service_certificate(
                service_name, thumbalgorithm, thumbprint)
            return props is not None
        except:
            return False

    def _deployment_exists(self, service_name, deployment_name):
        try:
            props = self.sms.get_deployment_by_name(
                service_name, deployment_name)
            return props is not None
        except:
            return False

    def _create_container_and_block_blob(self, container_name, blob_name,
                                         blob_data):
        self.bc.create_container(container_name, None, 'container', False)
        resp = self.bc.put_blob(
            container_name, blob_name, blob_data, 'BlockBlob')
        self.assertIsNone(resp)

    def _create_container_and_page_blob(self, container_name, blob_name,
                                        content_length):
        self.bc.create_container(container_name, None, 'container', False)
        resp = self.bc.put_blob(container_name, blob_name, '',
                                'PageBlob',
                                x_ms_blob_content_length=str(content_length))
        self.assertIsNone(resp)

    def _upload_file_to_block_blob(self, file_path, blob_name):
        data = open(file_path, 'rb').read()
        url = 'http://' + \
            credentials.getStorageServicesName() + \
            '.blob.core.windows.net/' + self.container_name + '/' + blob_name
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)
        return url

    def _upload_chunks(self, file_path, blob_name, chunk_size):
        index = 0
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if data:
                    length = len(data)
                    self.bc.put_page(
                        self.container_name, blob_name, data,
                        'bytes=' + str(index) + '-' + str(index + length - 1),
                        'update')
                    index += length
                else:
                    break

    def _upload_file_to_page_blob(self, file_path, blob_name):
        url = 'http://' + \
            credentials.getStorageServicesName() + \
            '.blob.core.windows.net/' + self.container_name + '/' + blob_name
        content_length = os.path.getsize(file_path)
        self._create_container_and_page_blob(
            self.container_name, blob_name, content_length)
        self._upload_chunks(file_path, blob_name, 262144)
        return url

    def _upload_default_package_to_storage_blob(self, blob_name):
        return self._upload_file_to_block_blob(CSPKG_PATH, blob_name)

    def _upload_disk_to_storage_blob(self, blob_name):
        return self._upload_file_to_page_blob(DATA_VHD_PATH, blob_name)

    def _add_deployment(self, service_name, deployment_name,
                        deployment_slot='Production'):
        configuration = base64.b64encode(DEPLOYMENT_ORIGINAL_CONFIG)
        package_url = self._upload_default_package_to_storage_blob(
            deployment_name + 'Blob')
        result = self.sms.create_deployment(
            service_name, deployment_slot, deployment_name, package_url,
            deployment_name + 'label', configuration, False, False,
            {'dep1': 'val1', 'dep2': 'val2'})
        self._wait_for_async(result.request_id)

    def _create_hosted_service_with_deployment(self, service_name,
                                               deployment_name):
        self._create_hosted_service(service_name)
        self._add_deployment(service_name, deployment_name)

    def _role_exists(self, service_name, deployment_name, role_name):
        try:
            props = self.sms.get_role(service_name, deployment_name, role_name)
            return props is not None
        except:
            return False

    def _create_disk(self, disk_name, os, url):
        result = self.sms.add_disk(False, disk_name, url, disk_name, os)
        self.assertIsNone(result)

    def _disk_exists(self, disk_name):
        try:
            disk = self.sms.get_disk(disk_name)
            return disk is not None
        except:
            return False

    def _create_os_image(self, name, blob_url, os):
        result = self.sms.add_os_image(name + 'label', blob_url, name, os)
        self._wait_for_async(result.request_id)

    def _os_image_exists(self, image_name):
        try:
            image = self.sms.get_os_image(image_name)
            return image is not None
        except:
            return False

    def _blob_exists(self, container_name, blob_name):
        try:
            props = self.bc.get_blob_properties(container_name, blob_name)
            return props is not None
        except:
            return False

    def _data_disk_exists(self, service_name, deployment_name, role_name, lun):
        try:
            props = self.sms.get_data_disk(
                service_name, deployment_name, role_name, lun)
            return props is not None
        except:
            return False

    def _add_data_disk_from_blob_url(self, service_name, deployment_name,
                                     role_name, lun, label):
        url = self._upload_disk_to_storage_blob('disk')
        result = self.sms.add_data_disk(
            service_name, deployment_name, role_name, lun, None, None, label,
            None, None, url)
        self._wait_for_async(result.request_id)

    def _linux_image_name(self):
        return self._image_from_category('Canonical')

    def _windows_image_name(self):
        return self._image_from_category('Microsoft Windows Server Group')

    def _host_name_from_role_name(self, role_name):
        return 'hn' + role_name[-13:]

    def _image_from_category(self, category):
        # return the first one listed, which should be the most stable
        return [i.name for i in self.sms.list_os_images() \
            if category in i.category][0]

    def _windows_role(self, role_name, subnet_name=None, port='59913'):
        host_name = self._host_name_from_role_name(role_name)
        system = self._windows_config(host_name)
        os_hd = self._os_hd(self._windows_image_name(),
                            self.container_name,
                            role_name + '.vhd')
        network = self._network_config(subnet_name, port)
        return (system, os_hd, network)

    def _linux_role(self, role_name, subnet_name=None, port='59913'):
        host_name = self._host_name_from_role_name(role_name)
        system = self._linux_config(host_name)
        os_hd = self._os_hd(self._linux_image_name(),
                            self.container_name,
                            role_name + '.vhd')
        network = self._network_config(subnet_name, port)
        return (system, os_hd, network)

    def _windows_config(self, hostname):
        system = WindowsConfigurationSet(
            hostname, 'u7;9jbp!', False, False, 'Pacific Standard Time',
            'azureuser')
        system.domain_join = None
        system.stored_certificate_settings.stored_certificate_settings.append(
            CertificateSetting(SERVICE_CERT_THUMBPRINT, 'My', 'LocalMachine'))
        listener = Listener('Https', SERVICE_CERT_THUMBPRINT)
        system.win_rm.listeners.listeners.append(listener)
        return system

    def _linux_config(self, hostname):
        pk = PublicKey(SERVICE_CERT_THUMBPRINT,
                       u'/home/unittest/.ssh/authorized_keys')
        pair = KeyPair(SERVICE_CERT_THUMBPRINT, u'/home/unittest/.ssh/id_rsa')
        system = LinuxConfigurationSet(hostname, 'unittest', 'u7;9jbp!', True)
        system.ssh.public_keys.public_keys.append(pk)
        system.ssh.key_pairs.key_pairs.append(pair)
        return system

    def _network_config(self, subnet_name=None, port='59913'):
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        network.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint('utendpoint', 'tcp', port, '3394'))
        if subnet_name:
            network.subnet_names.append(subnet_name)
        return network

    def _os_hd(self, image_name, target_container_name, target_blob_name):
        media_link = 'http://' + \
            credentials.getStorageServicesName() + \
            '.blob.core.windows.net/' + target_container_name + '/' + \
            target_blob_name
        os_hd = OSVirtualHardDisk(image_name, media_link,
                                  disk_label=target_blob_name)
        return os_hd

    def _create_vm_linux(self, service_name, deployment_name, role_name):
        self._create_hosted_service(service_name)
        self._create_service_certificate(
            service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        system, os_hd, network = self._linux_role(role_name)

        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production',
            deployment_name + 'label', role_name, system, os_hd,
            network, role_size='Small')

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)
        self._assert_role_instance_endpoint(
            service_name, deployment_name, 'utendpoint', 'tcp', '59913', '3394')

    def _create_vm_windows(self, service_name, deployment_name, role_name):
        self._create_hosted_service(service_name)
        self._create_service_certificate(
            service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        system, os_hd, network = self._windows_role(role_name)

        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production',
            deployment_name + 'label', role_name, system, os_hd,
            network, role_size='Small')

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)
        self._assert_role_instance_endpoint(
            service_name, deployment_name, 'utendpoint', 'tcp', '59913', '3394')

    def _assert_role_instance_endpoint(self, service_name, deployment_name,
                                       endpoint_name, protocol,
                                       public_port, local_port):
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(len(deployment.role_instance_list), 1)
        role_instance = deployment.role_instance_list[0]
        self.assertEqual(len(role_instance.instance_endpoints), 1)
        endpoint = role_instance.instance_endpoints[0]
        self.assertEqual(endpoint.name, endpoint_name)
        self.assertEqual(endpoint.protocol, protocol)
        self.assertEqual(endpoint.public_port, public_port)
        self.assertEqual(endpoint.local_port, local_port)

    def _add_role_windows(self, service_name, deployment_name, role_name, port):
        system, os_hd, network = self._windows_role(role_name, port=port)

        result = self.sms.add_role(service_name, deployment_name, role_name,
                                   system, os_hd, network)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name)

    #--Test cases for hosted services ------------------------------------
    def test_list_hosted_services(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        result = self.sms.list_hosted_services()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        service = None
        for temp in result:
            if temp.service_name == self.hosted_service_name:
                service = temp
                break

        self.assertIsNotNone(service)
        self.assertIsNotNone(service.service_name)
        self.assertIsNotNone(service.url)
        self.assertIsNotNone(service.hosted_service_properties)
        self.assertIsNotNone(service.hosted_service_properties.affinity_group)
        self.assertIsNotNone(service.hosted_service_properties.date_created)
        self.assertIsNotNone(
            service.hosted_service_properties.date_last_modified)
        self.assertIsNotNone(service.hosted_service_properties.description)
        self.assertIsNotNone(service.hosted_service_properties.label)
        self.assertIsNotNone(service.hosted_service_properties.location)
        self.assertIsNotNone(service.hosted_service_properties.status)
        self.assertIsNotNone(
            service.hosted_service_properties.extended_properties['ext1'])
        self.assertIsNotNone(
            service.hosted_service_properties.extended_properties['ext2'])
        self.assertIsNone(service.deployments)

    def test_get_hosted_service_properties(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        result = self.sms.get_hosted_service_properties(
            self.hosted_service_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.service_name)
        self.assertIsNotNone(result.url)
        self.assertIsNotNone(result.hosted_service_properties)
        self.assertIsNotNone(result.hosted_service_properties.affinity_group)
        self.assertIsNotNone(result.hosted_service_properties.date_created)
        self.assertIsNotNone(
            result.hosted_service_properties.date_last_modified)
        self.assertIsNotNone(result.hosted_service_properties.description)
        self.assertIsNotNone(result.hosted_service_properties.label)
        self.assertIsNotNone(result.hosted_service_properties.location)
        self.assertIsNotNone(result.hosted_service_properties.status)
        self.assertIsNotNone(
            result.hosted_service_properties.extended_properties['ext1'])
        self.assertIsNotNone(
            result.hosted_service_properties.extended_properties['ext2'])
        self.assertIsNone(result.deployments)

    def test_get_hosted_service_properties_with_embed_detail(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)

        # Act
        result = self.sms.get_hosted_service_properties(
            self.hosted_service_name, True)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.service_name)
        self.assertIsNotNone(result.url)
        self.assertIsNotNone(result.hosted_service_properties)
        self.assertIsNotNone(result.hosted_service_properties.affinity_group)
        self.assertIsNotNone(result.hosted_service_properties.date_created)
        self.assertIsNotNone(
            result.hosted_service_properties.date_last_modified)
        self.assertIsNotNone(result.hosted_service_properties.description)
        self.assertIsNotNone(result.hosted_service_properties.label)
        self.assertIsNotNone(result.hosted_service_properties.location)
        self.assertIsNotNone(result.hosted_service_properties.status)
        self.assertIsNotNone(
            result.hosted_service_properties.extended_properties['ext1'])
        self.assertIsNotNone(
            result.hosted_service_properties.extended_properties['ext2'])

        self.assertIsNotNone(result.deployments)
        self.assertIsNotNone(result.deployments[0].configuration)
        self.assertIsNotNone(result.deployments[0].created_time)
        self.assertIsNotNone(result.deployments[0].deployment_slot)
        self.assertIsNotNone(result.deployments[0].extended_properties['dep1'])
        self.assertIsNotNone(result.deployments[0].extended_properties['dep2'])
        self.assertIsNotNone(result.deployments[0].label)
        self.assertIsNotNone(result.deployments[0].last_modified_time)
        self.assertFalse(result.deployments[0].locked)
        self.assertEqual(result.deployments[0].name, deployment_name)
        self.assertIsNone(result.deployments[0].persistent_vm_downtime_info)
        self.assertIsNotNone(result.deployments[0].private_id)
        self.assertIsNotNone(result.deployments[0].role_list[0].os_version)
        self.assertEqual(result.deployments[0]
                         .role_list[0].role_name, 'WorkerRole1')
        self.assertFalse(result.deployments[0].rollback_allowed)
        self.assertIsNotNone(result.deployments[0].sdk_version)
        self.assertIsNotNone(result.deployments[0].status)
        self.assertIsNotNone(result.deployments[0].upgrade_domain_count)
        self.assertIsNone(result.deployments[0].upgrade_status)
        self.assertIsNotNone(result.deployments[0].url)
        self.assertIsNotNone(result.deployments[0].role_instance_list[0].fqdn)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_error_code)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_fault_domain)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_name)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_size)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_state_details)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_status)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].instance_upgrade_domain)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].ip_address)
        self.assertIsNotNone(
            result.deployments[0].role_instance_list[0].power_state)
        self.assertEqual(
            result.deployments[0].role_instance_list[0].role_name, 'WorkerRole1')

    def test_create_hosted_service(self):
        # Arrange
        label = 'pythonlabel'
        description = 'python hosted service description'
        location = 'West US'

        # Act
        result = self.sms.create_hosted_service(
            self.hosted_service_name, label, description, location, None,
            {'ext1': 'val1', 'ext2': 'val2'})

        # Assert
        self.assertIsNone(result)
        self.assertTrue(self._hosted_service_exists(self.hosted_service_name))

    def test_update_hosted_service(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)
        label = 'ptvslabelupdate'
        description = 'ptvs description update'

        # Act
        result = self.sms.update_hosted_service(
            self.hosted_service_name, label, description,
            {'ext1': 'val1update', 'ext2': 'val2update', 'ext3': 'brandnew'})

        # Assert
        self.assertIsNone(result)
        props = self.sms.get_hosted_service_properties(
            self.hosted_service_name)
        self.assertEqual(props.hosted_service_properties.label, label)
        self.assertEqual(
            props.hosted_service_properties.description, description)
        self.assertEqual(
            props.hosted_service_properties.extended_properties['ext1'],
            'val1update')
        self.assertEqual(
            props.hosted_service_properties.extended_properties['ext2'],
            'val2update')
        self.assertEqual(
            props.hosted_service_properties.extended_properties['ext3'],
            'brandnew')

    def test_delete_hosted_service(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        result = self.sms.delete_hosted_service(self.hosted_service_name)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._hosted_service_exists(self.hosted_service_name))

    def test_get_deployment_by_slot(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)

        # Act
        result = self.sms.get_deployment_by_slot(
            self.hosted_service_name, 'Production')

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, deployment_name)
        self.assertEqual(result.deployment_slot, 'Production')
        self.assertIsNotNone(result.label)
        self.assertIsNotNone(result.configuration)

    def test_get_deployment_by_name(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)

        # Act
        result = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, deployment_name)
        self.assertEqual(result.deployment_slot, 'Production')
        self.assertIsNotNone(result.label)
        self.assertIsNotNone(result.configuration)

    def test_create_deployment(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)
        configuration = base64.b64encode(DEPLOYMENT_ORIGINAL_CONFIG)
        package_url = self._upload_default_package_to_storage_blob(
            'WindowsAzure1Blob')

        # Act
        result = self.sms.create_deployment(
            self.hosted_service_name, 'production', 'WindowsAzure1',
            package_url, 'deploylabel', configuration)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._deployment_exists(self.hosted_service_name, 'WindowsAzure1'))

    def test_delete_deployment(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)

        # Act
        result = self.sms.delete_deployment(
            self.hosted_service_name, deployment_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(
            self._deployment_exists(self.hosted_service_name, deployment_name))

    def test_swap_deployment(self):
        # Arrange
        production_deployment_name = 'utdeployprod'
        staging_deployment_name = 'utdeploystag'
        self._create_hosted_service(self.hosted_service_name)
        self._add_deployment(self.hosted_service_name,
                             production_deployment_name, 'Production')
        self._add_deployment(self.hosted_service_name,
                             staging_deployment_name, 'Staging')

        # Act
        result = self.sms.swap_deployment(
            self.hosted_service_name,
            production_deployment_name,
            staging_deployment_name)
        self._wait_for_async(result.request_id)

        # Assert
        deploy = self.sms.get_deployment_by_slot(
            self.hosted_service_name, 'Production')
        self.assertIsNotNone(deploy)
        self.assertEqual(deploy.name, staging_deployment_name)
        self.assertEqual(deploy.deployment_slot, 'Production')

        deploy = self.sms.get_deployment_by_slot(
            self.hosted_service_name, 'Staging')
        self.assertIsNotNone(deploy)
        self.assertEqual(deploy.name, production_deployment_name)
        self.assertEqual(deploy.deployment_slot, 'Staging')

    def test_change_deployment_configuration(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        configuration = base64.b64encode(DEPLOYMENT_UPDATE_CONFIG)

        # Act
        result = self.sms.change_deployment_configuration(
            self.hosted_service_name, deployment_name, configuration)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        self.assertTrue(props.configuration.find('Instances count="4"') >= 0)

    def test_update_deployment_status(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)

        # Act
        result = self.sms.update_deployment_status(
            self.hosted_service_name, deployment_name, 'Suspended')
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        self.assertEqual(props.status, 'Suspended')

    def test_upgrade_deployment(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        package_url = self._upload_default_package_to_storage_blob('updated')
        configuration = base64.b64encode(DEPLOYMENT_UPDATE_CONFIG)

        # Act
        result = self.sms.upgrade_deployment(
            self.hosted_service_name, deployment_name, 'Auto',
            package_url, configuration, 'upgraded', True)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        self.assertEqual(props.label, 'upgraded')
        self.assertTrue(props.configuration.find('Instances count="4"') >= 0)

    def test_walk_upgrade_domain(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        package_url = self._upload_default_package_to_storage_blob('updated')
        configuration = base64.b64encode(DEPLOYMENT_UPDATE_CONFIG)
        result = self.sms.upgrade_deployment(
            self.hosted_service_name, deployment_name, 'Manual',
            package_url, configuration, 'upgraded', True)
        self._wait_for_async(result.request_id)

        # Act
        result = self.sms.walk_upgrade_domain(
            self.hosted_service_name, deployment_name, 0)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        self.assertEqual(props.label, 'upgraded')
        self.assertTrue(props.configuration.find('Instances count="4"') >= 0)

    def test_rollback_update_or_upgrade(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        package_url = self._upload_default_package_to_storage_blob(
            'updated207')
        configuration = base64.b64encode(DEPLOYMENT_UPDATE_CONFIG)

        self.sms.upgrade_deployment(self.hosted_service_name, deployment_name,
                                    'Auto', package_url, configuration,
                                    'upgraded', True)
        self._wait_for_rollback_allowed(
            self.hosted_service_name, deployment_name)

        # Act
        result = self.sms.rollback_update_or_upgrade(
            self.hosted_service_name, deployment_name, 'Auto', True)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        self.assertTrue(props.configuration.find('Instances count="2"') >= 0)

    def test_reboot_role_instance(self):
        # Arrange
        role_instance_name = 'WorkerRole1_IN_0'
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        result = self.sms.update_deployment_status(
            self.hosted_service_name, deployment_name, 'Running')
        self._wait_for_async(result.request_id)
        self._wait_for_deployment(self.hosted_service_name, deployment_name)
        self._wait_for_role(self.hosted_service_name, deployment_name,
                            role_instance_name)

        # Act
        result = self.sms.reboot_role_instance(
            self.hosted_service_name, deployment_name, role_instance_name)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        status = self._get_role_instance_status(props, role_instance_name)
        self.assertTrue(status == 'StoppedVM' or status == 'ReadyRole')

    def test_reimage_role_instance(self):
        # Arrange
        role_instance_name = 'WorkerRole1_IN_0'
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        result = self.sms.update_deployment_status(
            self.hosted_service_name, deployment_name, 'Running')
        self._wait_for_async(result.request_id)
        self._wait_for_deployment(self.hosted_service_name, deployment_name)
        self._wait_for_role(self.hosted_service_name, deployment_name,
                            role_instance_name)

        # Act
        result = self.sms.reimage_role_instance(
            self.hosted_service_name, deployment_name, role_instance_name)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        status = self._get_role_instance_status(props, role_instance_name)
        self.assertTrue(status == 'StoppedVM' or status == 'ReadyRole')

    def test_check_hosted_service_name_availability_not_available(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        result = self.sms.check_hosted_service_name_availability(
            self.hosted_service_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertFalse(result.result)

    def test_check_hosted_service_name_availability_available(self):
        # Arrange

        # Act
        result = self.sms.check_hosted_service_name_availability(
            self.hosted_service_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(result.result)

    #--Test cases for service certificates -------------------------------
    def test_list_service_certificates(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)
        self._create_service_certificate(
            self.hosted_service_name, SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        # Act
        result = self.sms.list_service_certificates(self.hosted_service_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        url_part = '/' + self.hosted_service_name + '/'
        cert = None
        for temp in result:
            if url_part in temp.certificate_url:
                cert = temp
                break

        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert.certificate_url)
        self.assertEqual(cert.thumbprint, SERVICE_CERT_THUMBPRINT)
        self.assertEqual(cert.thumbprint_algorithm, SERVICE_CERT_THUMBALGO)
        self.assertEqual(cert.data, SERVICE_CERT_DATA_PUBLIC)

    def test_get_service_certificate(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)
        self._create_service_certificate(
            self.hosted_service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        # Act
        result = self.sms.get_service_certificate(
            self.hosted_service_name,
            SERVICE_CERT_THUMBALGO, SERVICE_CERT_THUMBPRINT)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.certificate_url, '')
        self.assertEqual(result.thumbprint, '')
        self.assertEqual(result.thumbprint_algorithm, '')
        self.assertEqual(result.data, SERVICE_CERT_DATA_PUBLIC)

    def test_add_service_certificate(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        result = self.sms.add_service_certificate(
            self.hosted_service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._service_certificate_exists(
            self.hosted_service_name,
            SERVICE_CERT_THUMBALGO, SERVICE_CERT_THUMBPRINT))

    def test_delete_service_certificate(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)
        self._create_service_certificate(
            self.hosted_service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        # Act
        result = self.sms.delete_service_certificate(
            self.hosted_service_name,
            SERVICE_CERT_THUMBALGO, SERVICE_CERT_THUMBPRINT)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(self._service_certificate_exists(
            self.hosted_service_name,
            SERVICE_CERT_THUMBALGO, SERVICE_CERT_THUMBPRINT))

    #--Test cases for retrieving operating system information ------------
    def test_list_operating_systems(self):
        # Arrange

        # Act
        result = self.sms.list_operating_systems()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 20)
        self.assertIsNotNone(result[0].family)
        self.assertIsNotNone(result[0].family_label)
        self.assertIsNotNone(result[0].is_active)
        self.assertIsNotNone(result[0].is_default)
        self.assertIsNotNone(result[0].label)
        self.assertIsNotNone(result[0].version)

    def test_list_operating_system_families(self):
        # Arrange

        # Act
        result = self.sms.list_operating_system_families()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertIsNotNone(result[0].name)
        self.assertIsNotNone(result[0].label)
        self.assertTrue(len(result[0].operating_systems) > 0)
        self.assertIsNotNone(result[0].operating_systems[0].version)
        self.assertIsNotNone(result[0].operating_systems[0].label)
        self.assertIsNotNone(result[0].operating_systems[0].is_default)
        self.assertIsNotNone(result[0].operating_systems[0].is_active)

    #--Test cases for retrieving subscription history --------------------
    def test_get_subscription(self):
        # Arrange

        # Act
        result = self.sms.get_subscription()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.subscription_id,
                         credentials.getSubscriptionId())
        self.assertIsNotNone(result.account_admin_live_email_id)
        self.assertIsNotNone(result.service_admin_live_email_id)
        self.assertIsNotNone(result.subscription_name)
        self.assertIsNotNone(result.subscription_status)
        self.assertTrue(result.current_core_count >= 0)
        self.assertTrue(result.current_hosted_services >= 0)
        self.assertTrue(result.current_storage_accounts >= 0)
        self.assertTrue(result.max_core_count > 0)
        self.assertTrue(result.max_dns_servers > 0)
        self.assertTrue(result.max_hosted_services > 0)
        self.assertTrue(result.max_local_network_sites > 0)
        self.assertTrue(result.max_storage_accounts > 0)
        self.assertTrue(result.max_virtual_network_sites > 0)

    #--Test cases for virtual machines -----------------------------------
    def test_get_role_linux(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_linux(service_name, deployment_name, role_name)

        # Act
        result = self.sms.get_role(service_name, deployment_name, role_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.role_name, role_name)
        self.assertIsNotNone(result.role_size)
        self.assertIsNotNone(result.role_type)
        self.assertIsNotNone(result.os_virtual_hard_disk)
        self.assertIsNotNone(result.os_virtual_hard_disk.disk_label)
        self.assertIsNotNone(result.os_virtual_hard_disk.disk_name)
        self.assertIsNotNone(result.os_virtual_hard_disk.host_caching)
        self.assertIsNotNone(result.os_virtual_hard_disk.media_link)
        self.assertIsNotNone(result.os_virtual_hard_disk.os)
        self.assertIsNotNone(result.os_virtual_hard_disk.source_image_name)
        self.assertIsNotNone(result.data_virtual_hard_disks)
        self.assertIsNotNone(result.configuration_sets)
        self.assertIsNotNone(result.configuration_sets[0])
        self.assertIsNotNone(
            result.configuration_sets[0].configuration_set_type)
        self.assertIsNotNone(result.configuration_sets[0].input_endpoints)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].protocol)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].port)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].name)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].local_port)

    def test_get_role_windows(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        # Act
        result = self.sms.get_role(service_name, deployment_name, role_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.role_name, role_name)
        self.assertIsNotNone(result.role_size)
        self.assertIsNotNone(result.role_type)
        self.assertIsNotNone(result.os_virtual_hard_disk)
        self.assertIsNotNone(result.os_virtual_hard_disk.disk_label)
        self.assertIsNotNone(result.os_virtual_hard_disk.disk_name)
        self.assertIsNotNone(result.os_virtual_hard_disk.host_caching)
        self.assertIsNotNone(result.os_virtual_hard_disk.media_link)
        self.assertIsNotNone(result.os_virtual_hard_disk.os)
        self.assertIsNotNone(result.os_virtual_hard_disk.source_image_name)
        self.assertIsNotNone(result.data_virtual_hard_disks)
        self.assertIsNotNone(result.configuration_sets)
        self.assertIsNotNone(result.configuration_sets[0])
        self.assertIsNotNone(
            result.configuration_sets[0].configuration_set_type)
        self.assertIsNotNone(result.configuration_sets[0].input_endpoints)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].protocol)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].port)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].name)
        self.assertIsNotNone(
            result.configuration_sets[0].input_endpoints[0].local_port)
        self.assertTrue(len(result.default_win_rm_certificate_thumbprint) > 0)

    def test_create_virtual_machine_deployment_linux(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name
        deployment_label = deployment_name + 'label'

        self._create_hosted_service(service_name)
        self._create_service_certificate(
            service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        # Act
        system, os_hd, network = self._linux_role(role_name)

        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production', deployment_label,
            role_name, system, os_hd, network, role_size='Small')

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name))
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(deployment.label, deployment_label)

    def test_create_virtual_machine_deployment_windows(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name
        deployment_label = deployment_name + 'label'

        self._create_hosted_service(service_name)
        self._create_service_certificate(
            service_name,
            SERVICE_CERT_DATA, SERVICE_CERT_FORMAT, SERVICE_CERT_PASSWORD)

        # Act
        system, os_hd, network = self._windows_role(role_name)

        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production', deployment_label,
            role_name, system, os_hd, network, role_size='Small')

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name))
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(deployment.label, deployment_label)

    def test_create_virtual_machine_deployment_windows_virtual_network(self):
        # this test requires the following manual resources to be created
        # use the azure portal to create them
        affinity_group = 'utaffgrpdonotdelete'    # affinity group, any region
        # storage account in affinity group
        storage_name = 'utstoragedonotdelete'
        # virtual network in affinity group
        virtual_network_name = 'utnetdonotdelete'
        subnet_name = 'Subnet-1'                  # subnet in virtual network

        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name
        deployment_label = deployment_name + 'label'

        self._create_hosted_service(
            service_name, affinity_group=affinity_group)
        self._create_service_certificate(
            service_name, SERVICE_CERT_DATA, 'pfx', SERVICE_CERT_PASSWORD)

        # Act
        system, os_hd, network = self._windows_role(role_name, subnet_name)

        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production', deployment_label,
            role_name, system, os_hd, network,
            role_size='Small', virtual_network_name=virtual_network_name)

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name))
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(deployment.label, deployment_label)

    def test_add_role_linux(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_linux(service_name, deployment_name, role_name1)

        # Act
        system, os_hd, network = self._linux_role(role_name2, port='59914')
        network = None

        result = self.sms.add_role(service_name, deployment_name, role_name2,
                                   system, os_hd, network)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name2)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name1))
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name2))

        svc = self.sms.get_hosted_service_properties(service_name, True)
        role_instances = svc.deployments[0].role_instance_list
        self.assertEqual(role_instances[0].host_name,
                         self._host_name_from_role_name(role_name1))
        self.assertEqual(role_instances[1].host_name,
                         self._host_name_from_role_name(role_name2))

    def test_add_role_windows(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_windows(service_name, deployment_name, role_name1)

        # Act
        system, os_hd, network = self._windows_role(role_name2, port='59914')

        result = self.sms.add_role(service_name, deployment_name, role_name2, 
                                   system, os_hd, network)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name2)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name1))
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name2))

        svc = self.sms.get_hosted_service_properties(service_name, True)
        role_instances = svc.deployments[0].role_instance_list
        self.assertEqual(role_instances[0].host_name,
                         self._host_name_from_role_name(role_name1))
        self.assertEqual(role_instances[1].host_name,
                         self._host_name_from_role_name(role_name2))

    def test_update_role(self):
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        network.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint('endupdate', 'tcp', '50055', '5555'))

        # Act
        result = self.sms.update_role(service_name, deployment_name, role_name,
                                      network_config=network,
                                      role_size='Medium')
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Assert
        role = self.sms.get_role(service_name, deployment_name, role_name)
        self.assertEqual(role.role_size, 'Medium')

    def test_delete_role(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_windows(service_name, deployment_name, role_name1)
        self._add_role_windows(service_name, deployment_name, role_name2, '59914')

        # Act
        result = self.sms.delete_role(service_name, deployment_name, role_name2)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name1))
        self.assertFalse(
            self._role_exists(service_name, deployment_name, role_name2))

    def test_shutdown_start_and_restart_role(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        # Act
        result = self.sms.shutdown_role(service_name, deployment_name, role_name)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name, 'StoppedVM')

        # Act
        result = self.sms.start_role(service_name, deployment_name, role_name)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Act
        result = self.sms.restart_role(service_name, deployment_name, role_name)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Act
        result = self.sms.shutdown_role(service_name, deployment_name,
                                        role_name, 'StoppedDeallocated')
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name,
                            'StoppedDeallocated')

    def test_shutdown_and_start_roles(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_windows(service_name, deployment_name, role_name1)
        self._add_role_windows(service_name, deployment_name, role_name2, '59914')

        # Act
        result = self.sms.shutdown_roles(service_name, deployment_name,
                                         [role_name1, role_name2])
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1,
                            'StoppedVM')
        self._wait_for_role(service_name, deployment_name, role_name2,
                            'StoppedVM')

        # Act
        result = self.sms.start_roles(service_name, deployment_name,
                                      [role_name1, role_name2])
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1)
        self._wait_for_role(service_name, deployment_name, role_name2)

    def test_capture_role(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        result = self.sms.shutdown_role(service_name, deployment_name, role_name)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name, 'StoppedVM')

        image_name = self.os_image_name
        image_label = role_name + 'captured'

        # Act
        result = self.sms.capture_role(
            service_name, deployment_name, role_name, 'Delete', image_name,
            image_label)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._os_image_exists(self.os_image_name))

    #--Test cases for virtual machine images -----------------------------
    def test_list_os_images(self):
        # Arrange
        media_url = LINUX_OS_VHD_URL
        os = 'Linux'
        self._create_os_image(self.os_image_name, media_url, os)

        # Act
        result = self.sms.list_os_images()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        image = None
        for temp in result:
            if temp.name == self.os_image_name:
                image = temp
                break

        self.assertIsNotNone(image)
        self.assertIsNotNone(image.affinity_group)
        self.assertIsNotNone(image.category)
        self.assertIsNotNone(image.description)
        self.assertIsNotNone(image.eula)
        self.assertIsNotNone(image.label)
        self.assertIsNotNone(image.location)
        self.assertIsNotNone(image.logical_size_in_gb)
        self.assertEqual(image.media_link, media_url)
        self.assertEqual(image.name, self.os_image_name)
        self.assertEqual(image.os, os)

    def test_get_os_image(self):
        # Arrange
        media_url = LINUX_OS_VHD_URL
        os = 'Linux'
        self._create_os_image(self.os_image_name, media_url, os)

        # Act
        result = self.sms.get_os_image(self.os_image_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.affinity_group)
        self.assertIsNotNone(result.category)
        self.assertIsNotNone(result.description)
        self.assertIsNotNone(result.eula)
        self.assertIsNotNone(result.label)
        self.assertIsNotNone(result.location)
        self.assertIsNotNone(result.logical_size_in_gb)
        self.assertEqual(result.media_link, media_url)
        self.assertEqual(result.name, self.os_image_name)
        self.assertEqual(result.os, os)

    def test_add_os_image(self):
        # Arrange

        # Act
        result = self.sms.add_os_image(
            'utcentosimg', LINUX_OS_VHD_URL, self.os_image_name, 'Linux')
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._os_image_exists(self.os_image_name))

    def test_update_os_image(self):
        # Arrange
        self._create_os_image(self.os_image_name, LINUX_OS_VHD_URL, 'Linux')

        # Act
        result = self.sms.update_os_image(
            self.os_image_name, 'newlabel', LINUX_OS_VHD_URL,
            self.os_image_name, 'Linux')
        self._wait_for_async(result.request_id)

        # Assert
        image = self.sms.get_os_image(self.os_image_name)
        self.assertEqual(image.label, 'newlabel')
        self.assertEqual(image.os, 'Linux')

    def test_delete_os_image(self):
        # Arrange
        self._create_os_image(self.os_image_name, LINUX_OS_VHD_URL, 'Linux')

        # Act
        result = self.sms.delete_os_image(self.os_image_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(self._os_image_exists(self.os_image_name))

    #--Test cases for virtual machine disks ------------------------------
    def test_get_data_disk(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        lun = 1
        self._add_data_disk_from_blob_url(
            service_name, deployment_name, role_name, lun, 'mylabel')
        self.data_disk_info = (service_name, deployment_name, role_name, lun)

        # Act
        result = self.sms.get_data_disk(
            service_name, deployment_name, role_name, lun)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.disk_label, 'mylabel')
        self.assertIsNotNone(result.disk_name)
        self.assertIsNotNone(result.host_caching)
        self.assertIsNotNone(result.logical_disk_size_in_gb)
        self.assertEqual(result.lun, lun)
        self.assertIsNotNone(result.media_link)

        service_props = self.sms.get_hosted_service_properties(service_name, True)
        hd = service_props.deployments[0].role_list[0].data_virtual_hard_disks[0]
        self.assertEqual(result.disk_label, hd.disk_label)
        self.assertEqual(result.disk_name, hd.disk_name)
        self.assertEqual(result.host_caching, hd.host_caching)
        self.assertEqual(result.logical_disk_size_in_gb, hd.logical_disk_size_in_gb)
        self.assertEqual(result.lun, hd.lun)
        self.assertEqual(result.media_link, hd.media_link)

    def test_add_data_disk_from_disk_name(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        lun = 2
        url = self._upload_disk_to_storage_blob('disk')
        self._create_disk(self.disk_name, 'Windows', url)
        self.data_disk_info = (service_name, deployment_name, role_name, lun)

        # Act
        result = self.sms.add_data_disk(
            service_name, deployment_name, role_name, lun, None, None,
            'testdisklabel', self.disk_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._data_disk_exists(service_name, deployment_name,
                                   role_name, lun))

    def test_add_data_disk_from_blob_url(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        lun = 3
        label = 'disk' + str(lun)
        url = self._upload_disk_to_storage_blob('disk')
        self.data_disk_info = (service_name, deployment_name, role_name, lun)

        # Act
        result = self.sms.add_data_disk(
            service_name, deployment_name, role_name, lun, None, None, label,
            None, None, url)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._data_disk_exists(service_name, deployment_name,
                                   role_name, lun))

    def test_update_data_disk(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        lun = 1
        updated_lun = 10
        self._add_data_disk_from_blob_url(
            service_name, deployment_name, role_name, lun, 'mylabel')
        self.data_disk_info = (service_name, deployment_name, role_name, lun)

        # Act
        result = self.sms.update_data_disk(
            service_name, deployment_name, role_name, lun, None, None,
            updated_lun)
        self._wait_for_async(result.request_id)
        self.data_disk_info = (
            service_name, deployment_name, role_name, updated_lun)

        # Assert
        self.assertFalse(
            self._data_disk_exists(service_name, deployment_name,
                                   role_name, lun))
        self.assertTrue(
            self._data_disk_exists(service_name, deployment_name,
                                   role_name, updated_lun))

    def test_delete_data_disk(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        lun = 5
        url = self._upload_disk_to_storage_blob('disk')
        self._create_disk(self.disk_name, 'Windows', url)
        result = self.sms.add_data_disk(
            service_name, deployment_name, role_name, lun, None, None,
            'testdisklabel', self.disk_name)
        self._wait_for_async(result.request_id)

        # Act
        result = self.sms.delete_data_disk(
            service_name, deployment_name, role_name, lun)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(
            self._data_disk_exists(service_name, deployment_name,
                                   role_name, lun))

    #--Test cases for virtual machine disks ------------------------------
    def test_list_disks(self):
        # Arrange
        url = self._upload_disk_to_storage_blob('disk')
        self._create_disk(self.disk_name, 'Windows', url)

        # Act
        result = self.sms.list_disks()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        disk = None
        for temp in result:
            if temp.name == self.disk_name:
                disk = temp
                break

        self.assertIsNotNone(disk)
        self.assertIsNotNone(disk.os)
        self.assertIsNotNone(disk.location)
        self.assertIsNotNone(disk.logical_disk_size_in_gb)
        self.assertIsNotNone(disk.media_link)
        self.assertIsNotNone(disk.name)
        self.assertIsNotNone(disk.source_image_name)

    def test_get_disk_unattached(self):
        # Arrange
        url = self._upload_disk_to_storage_blob('disk')
        self._create_disk(self.disk_name, 'Windows', url)

        # Act
        result = self.sms.get_disk(self.disk_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.os)
        self.assertIsNotNone(result.location)
        self.assertIsNotNone(result.logical_disk_size_in_gb)
        self.assertEqual(result.media_link, url)
        self.assertEqual(result.name, self.disk_name)
        self.assertIsNotNone(result.source_image_name)
        self.assertIsNone(result.attached_to)

    def test_get_disk_attached(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        lun = 6
        url = self._upload_disk_to_storage_blob('disk')
        self._create_disk(self.disk_name, 'Windows', url)
        self.data_disk_info = (service_name, deployment_name, role_name, lun)
        result = self.sms.add_data_disk(
            service_name, deployment_name, role_name, lun, None, None,
            'testdisklabel', self.disk_name)
        self._wait_for_async(result.request_id)

        # Act
        result = self.sms.get_disk(self.disk_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.os)
        self.assertIsNotNone(result.location)
        self.assertIsNotNone(result.logical_disk_size_in_gb)
        self.assertIsNotNone(result.media_link)
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.source_image_name)
        self.assertIsNotNone(result.attached_to)
        self.assertEqual(result.attached_to.deployment_name, deployment_name)
        self.assertEqual(result.attached_to.hosted_service_name, service_name)
        self.assertEqual(result.attached_to.role_name, role_name)

    def test_add_disk(self):
        # Arrange
        url = self._upload_disk_to_storage_blob('disk')

        # Act
        result = self.sms.add_disk(
            False, 'ptvslabel', url, self.disk_name, 'Windows')

        # Assert
        self.assertIsNone(result)
        self.assertTrue(self._disk_exists(self.disk_name))

    def test_update_disk(self):
        # Arrange
        url = self._upload_disk_to_storage_blob('disk')
        urlupdate = self._upload_disk_to_storage_blob('diskupdate')
        self._create_disk(self.disk_name, 'Windows', url)

        # Act
        result = self.sms.update_disk(
            self.disk_name, False, 'ptvslabelupdate', urlupdate,
            self.disk_name, 'Windows')

        # Assert
        self.assertIsNone(result)
        disk = self.sms.get_disk(self.disk_name)
        self.assertEqual(disk.name, self.disk_name)
        self.assertEqual(disk.label, 'ptvslabelupdate')
        self.assertEqual(disk.media_link, url)

    def test_delete_disk(self):
        # Arrange
        url = self._upload_disk_to_storage_blob('disk')
        self._create_disk(self.disk_name, 'Windows', url)

        # Act
        result = self.sms.delete_disk(self.disk_name)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._disk_exists(self.disk_name))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
