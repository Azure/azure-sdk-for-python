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

import os
import os.path
import requests
import unittest
from datetime import datetime, timedelta

from azure.servicemanagement._common_conversion import (
    _encode_base64,
)
from azure.servicemanagement import (
    CaptureRoleAsVMImage,
    CertificateSetting,
    ConfigurationSet,
    ConfigurationSetInputEndpoint,
    KeyPair,
    LinuxConfigurationSet,
    Listener,
    OSVirtualHardDisk,
    PublicKey,
    ResourceExtensionReference,
    ResourceExtensionReferences,
    ServiceManagementService,
    VMImage,
    WindowsConfigurationSet,
    parse_response_for_async_op,
    get_certificate_from_publish_settings,
)
from azure.storage.blob import PageBlobService, BlockBlobService
from azure.storage.blob.models import PublicAccess
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.legacy_mgmt_testcase import LegacyMgmtTestCase


SERVICE_CERT_FORMAT = 'pfx'
SERVICE_CERT_PASSWORD = 'Python'
SERVICE_CERT_DATA = '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'
SERVICE_CERT_DATA_PUBLIC = 'MIIC9jCCAeKgAwIBAgIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAMBUxEzARBgNVBAMTClB5dGhvblRlc3QwHhcNMTIwODMwMDAyNTMzWhcNMzkxMjMxMjM1OTU5WjAVMRMwEQYDVQQDEwpQeXRob25UZXN0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsjULNM53WPLkht1rbrDob/e4hZTHzj/hlLoBt2X3cNRc6dOPsMucxbMdchbCqAFa5RIaJvF5NDKqZuUSwq6bttD71twzy9bQ03EySOcRBad1VyqAZQ8DL8nUGSnXIUh+tpz4fDGM5f3Ly9NX8zfGqG3sT635rrFlUp3meJC+secCCwTLOOcIs3KQmuB+pMB5Y9rPhoxcekFfpq1pKtis6pmxnVbiL49kr6UUL6RQRDwik4t1jttatXLZqHETTmXl0Y0wS5AcJUXVAn5AL2kybULoThop2v01/E0NkPtFPAqLVs/kKBahniNn9uwUo+LS9FA8rWGu0FY4CZEYDfhb+QIDAQABo0owSDBGBgNVHQEEPzA9gBBS6knRHo54LppngxVCCzZVoRcwFTETMBEGA1UEAxMKUHl0aG9uVGVzdIIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAA4IBAQAnZbP3YV+08wI4YTg6MOVA+j1njd0kVp35FLehripmaMNE6lgk3Vu1MGGl0JnvMr3fNFGFzRske/jVtFxlHE5H/CoUzmyMQ+W06eV/e995AduwTKsS0ZgYn0VoocSXWst/nyhpKOcbJgAOohOYxgsGI1JEqQgjyeqzcCIhw/vlWiA3V8bSiPnrC9vwhH0eB025hBd2VbEGDz2nWCYkwtuOLMTvkmLi/oFw3GOfgagZKk8k/ZPffMCafz+yR3vb1nqAjncrVcJLI8amUfpxhjZYexo8MbxBA432M6w8sjXN+uLCl7ByWZ4xs4vonWgkmjeObtU37SIzolHT4dxIgaP2'
SERVICE_CERT_THUMBPRINT = 'BEA4B74BD6B915E9DD6A01FB1B8C3C1740F517F2'
SERVICE_CERT_THUMBALGO = 'sha1'

DEPLOYMENT_ORIGINAL_CONFIG = '''<ServiceConfiguration serviceName="WindowsAzure1" xmlns="http://schemas.microsoft.com/ServiceHosting/2008/10/ServiceConfiguration" osFamily="2" osVersion="*" schemaVersion="2012-05.1.7">
  <Role name="WorkerRole1">
    <Instances count="2" />
    <ConfigurationSettings>
      <Setting name="Microsoft.WindowsAzure.Plugins.Diagnostics.ConnectionString" value="UseDevelopmentStorage=true" />
    </ConfigurationSettings>
  </Role>
</ServiceConfiguration>'''

DEPLOYMENT_UPDATE_CONFIG = '''<ServiceConfiguration serviceName="WindowsAzure1" xmlns="http://schemas.microsoft.com/ServiceHosting/2008/10/ServiceConfiguration" osFamily="2" osVersion="*" schemaVersion="2012-05.1.7">
  <Role name="WorkerRole1">
    <Instances count="4" />
    <ConfigurationSettings>
      <Setting name="Microsoft.WindowsAzure.Plugins.Diagnostics.ConnectionString" value="UseDevelopmentStorage=true" />
    </ConfigurationSettings>
  </Role>
</ServiceConfiguration>'''

CSPKG_PATH = 'data/WindowsAzure1.cspkg'
DATA_VHD_PATH = 'data/testhd'


#------------------------------------------------------------------------------
class LegacyMgmtMiscTest(LegacyMgmtTestCase):

    def setUp(self):
        super(LegacyMgmtMiscTest, self).setUp()

        self.sms = self.create_service_management(ServiceManagementService)

        self.bc = self._create_storage_service(PageBlobService, self.settings)
        self.bbc = self._create_storage_service(BlockBlobService, self.settings)

        self.hosted_service_name = self.get_resource_name('utsvc')
        self.container_name = self.get_resource_name('utctnr')
        self.disk_name = self.get_resource_name('utdisk')
        self.os_image_name = self.get_resource_name('utosimg')
        self.data_disk_infos = []
        self.reserved_ip_address = None

    def tearDown(self):
        if not self.is_playback():
            for data_disk_info in self.data_disk_infos:
                try:
                    disk = self.sms.get_data_disk(
                        data_disk_info[0], data_disk_info[1],
                        data_disk_info[2], data_disk_info[3])
                    try:
                        result = self.sms.delete_data_disk(
                            data_disk_info[0], data_disk_info[1],
                            data_disk_info[2], data_disk_info[3],
                            delete_vhd=True)
                        self._wait_for_async(result.request_id)
                    except:
                        pass
                    try:
                        self.sms.delete_disk(disk.disk_name, delete_vhd=True)
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
                                role.role_name,
                            )
                            if role_props.os_virtual_hard_disk.disk_name \
                                not in disk_names:
                                disk_names.append(
                                    role_props.os_virtual_hard_disk.disk_name)
                    except:
                        pass

                    try:
                        result = self.sms.delete_deployment(
                            self.hosted_service_name,
                            deployment.name,
                            delete_vhd=True,
                        )
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
                    self.sms.delete_disk(disk_name, delete_vhd=True)
                except:
                    pass

            try:
                self.bc.delete_container(self.container_name)
            except:
                pass

            if self.reserved_ip_address:
                try:
                    result = self.sms.delete_reserved_ip_address(self.reserved_ip_address)
                    self._wait_for_async(result.request_id)
                except:
                    pass

        return super(LegacyMgmtMiscTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _wait_for_async(self, request_id):
        # Note that we keep the same ratio of timeout/sleep_interval in
        # live and playback so we end up with same number of loops/requests
        if self.is_playback():
            self.sms.wait_for_operation_status(request_id, timeout=1.2, sleep_interval=0.01)
        else:
            self.sms.wait_for_operation_status(request_id, timeout=600, sleep_interval=5)

    def _wait_for_deployment(self, service_name, deployment_name,
                             status='Running'):
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while props.status != status:
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False, 'Timed out waiting for deployment status.')
            self.sleep(5)
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
            self.sleep(5)
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
            self.sleep(5)
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
        self._wait_for_async(result.request_id)

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

    def _make_blob_url(self, storage_account_name, container_name, blob_name):
        return 'http://{0}.blob.core.windows.net/{1}/{2}'.format(
            storage_account_name,
            container_name,
            blob_name
        )

    def _create_container_and_block_blob(self, container_name, blob_name,
                                         blob_data):
        self.bc.create_container(container_name, None, 'container', False)
        self.bbc.create_blob_from_bytes(
            container_name, blob_name, blob_data)

    def _create_container_and_page_blob(self, container_name, blob_name,
                                        content_length):
        self.bc.create_container(container_name, None, 'container', False)
        self.bc.create_blob_from_bytes(container_name, blob_name, b'')

    def _upload_file_to_block_blob(self, file_path, blob_name):
        data = open(file_path, 'rb').read()
        url = self._make_blob_url(self.settings.STORAGE_ACCOUNT_NAME,
                                  self.container_name, blob_name)
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
                    self.bc.update_page(
                        self.container_name, blob_name, data,
                        index, index + length - 1)
                    index += length
                else:
                    break

    def _upload_file_to_page_blob(self, file_path, blob_name):
        url = self._make_blob_url(self.settings.STORAGE_ACCOUNT_NAME,
                                  self.container_name, blob_name)
        content_length = os.path.getsize(file_path)
        self._create_container_and_page_blob(
            self.container_name, blob_name, content_length)
        self._upload_chunks(file_path, blob_name, 262144)
        return url

    def _upload_default_package_to_storage_blob(self, blob_name):
        file_path = os.path.join(self.working_folder, CSPKG_PATH)
        return self._upload_file_to_block_blob(file_path, blob_name)

    def _upload_disk_to_storage_blob(self, blob_name):
        file_path = os.path.join(self.working_folder, DATA_VHD_PATH)
        return self._upload_file_to_page_blob(file_path, blob_name)

    def _add_deployment(self, service_name, deployment_name,
                        deployment_slot='Production'):
        configuration = _encode_base64(DEPLOYMENT_ORIGINAL_CONFIG)
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
        result = self.sms.add_disk(None, disk_name, url, disk_name, os)
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
        return self._image_from_publisher_name('Canonical')

    def _windows_image_name(self):
        return self._image_from_publisher_name('Microsoft Windows Server Group')

    def _host_name_from_role_name(self, role_name):
        return 'hn' + role_name[-13:]

    def _image_from_publisher_name(self, publisher):
        images = self.sms.list_os_images()
        images_from_publisher = [i for i in images if publisher in i.publisher_name]
        images_in_gui = [i for i in images_from_publisher if i.show_in_gui]
        return images_in_gui[-1].name

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
        system.disable_ssh_password_authentication = False
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
        media_link = self._make_blob_url(
            self.settings.STORAGE_ACCOUNT_NAME,
            target_container_name, target_blob_name)
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

    def _create_reserved_ip_address(self):
        self.reserved_ip_address = self.get_resource_name('ip')
        result = self.sms.create_reserved_ip_address(
            self.reserved_ip_address,
            'mylabel',
            'West US')
        self._wait_for_async(result.request_id)

    def _reserved_ip_address_exists(self, name):
        try:
            result = self.sms.get_reserved_ip_address(name)
            return result is not None
        except:
            return False

    def _create_vm_image(self, image_name):
        media_link = self._copy_linux_os_vhd_to_container()

        img = VMImage()
        img.name = image_name
        img.label = image_name + 'label'
        img.description = image_name + 'description'
        img.os_disk_configuration.os_state = 'Specialized'
        img.os_disk_configuration.os = 'Linux'
        img.os_disk_configuration.media_link = media_link
        img.language = 'English'
        img.show_in_gui = True

        result = self.sms.create_vm_image(img)
        self._wait_for_async(result.request_id)

    def _copy_linux_os_vhd_to_container(self):
        blob_name = 'imagecopy.vhd'
        self.bc.create_container(self.container_name,
                                 public_access=PublicAccess.Blob)
        resp = self.bc.copy_blob(self.container_name, blob_name,
                                 self.settings.LINUX_OS_VHD)
        return self.bc.make_blob_url(self.container_name, blob_name)

    #--Test cases for http passthroughs --------------------------------------
    @record
    def test_perform_get(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        response = self.sms.perform_get(
            '/{0}/services/hostedservices/{1}'.format(
                self.settings.SUBSCRIPTION_ID,
                self.hosted_service_name
            )
        )

        # Assert
        self.assertEqual(response.status, 200)
        self.assertEqual(response.message, 'OK')
        self.assertGreater(len(response.body), 0)
        self.assertNotEqual(
            response.body.decode().find(self.hosted_service_name), -1)

    @record
    def test_perform_post(self):
        # Arrange

        # Act
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<CreateHostedService xmlns="http://schemas.microsoft.com/windowsazure">
  <ServiceName>{0}</ServiceName>
  <Label>{1}</Label>
  <Description>{2}</Description>
  <Location>{3}</Location>
</CreateHostedService>'''

        response = self.sms.perform_post(
            '/{0}/services/hostedservices'.format(
                self.settings.SUBSCRIPTION_ID
            ),
            xml.format(
                self.hosted_service_name,
                _encode_base64(self.hosted_service_name + 'label'),
                'mydescription',
                'West US'
            )
        )

        as_async = parse_response_for_async_op(response)
        self._wait_for_async(as_async.request_id)

        # Assert
        self.assertEqual(response.status, 201)
        self.assertEqual(response.message, 'Created')
        self.assertTrue(self._hosted_service_exists(self.hosted_service_name))

    @record
    def test_perform_put(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<UpdateHostedService xmlns="http://schemas.microsoft.com/windowsazure">
  <Label>{0}</Label>
</UpdateHostedService>'''

        response = self.sms.perform_put(
            '/{0}/services/hostedservices/{1}'.format(
                self.settings.SUBSCRIPTION_ID,
                self.hosted_service_name
            ),
            xml.format(
                _encode_base64(self.hosted_service_name + 'new')
            )
        )

        as_async = parse_response_for_async_op(response)
        self._wait_for_async(as_async.request_id)

        # Assert
        self.assertEqual(response.status, 200)
        self.assertEqual(response.message, 'OK')
        props = self.sms.get_hosted_service_properties(self.hosted_service_name)
        self.assertEqual(props.hosted_service_properties.label,
                         self.hosted_service_name + 'new')

    @record
    def test_perform_delete(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        response = self.sms.perform_delete(
            '/{0}/services/hostedservices/{1}'.format(
                self.settings.SUBSCRIPTION_ID,
                self.hosted_service_name
            )
        )

        as_async = parse_response_for_async_op(response)
        self._wait_for_async(as_async.request_id)

        # Assert
        self.assertEqual(response.status, 200)
        self.assertEqual(response.message, 'OK')
        self.assertFalse(self._hosted_service_exists(self.hosted_service_name))

    #--Test cases for subscriptions --------------------------------------
    @record
    def test_list_role_sizes(self):
        # Arrange

        # Act
        result = self.sms.list_role_sizes()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        role_size = result[0]
        self.assertTrue(len(role_size.name) > 0)
        self.assertTrue(len(role_size.label) > 0)
        self.assertTrue(role_size.cores > 0)
        self.assertTrue(role_size.max_data_disk_count > 0)
        self.assertTrue(role_size.memory_in_mb > 0)
        self.assertTrue(role_size.virtual_machine_resource_disk_size_in_mb > 0)
        self.assertTrue(role_size.web_worker_resource_disk_size_in_mb > 0)
        self.assertIsInstance(role_size.supported_by_virtual_machines, bool)
        self.assertIsInstance(role_size.supported_by_web_worker_roles, bool)

    @unittest.skip('Can only be used with oauth')
    @record
    def test_list_subscriptions(self):
        # Arrange

        # Act
        result = self.sms.list_subscriptions()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

    #--Test cases for hosted services ------------------------------------
    @record
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

    @record
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

    @record
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

    @record
    def test_create_update_delete_hosted_service(self):
        # Arrange
        label = 'pythonlabel'
        description = 'python hosted service description'
        location = 'West US'

        # Act
        result = self.sms.create_hosted_service(
            self.hosted_service_name, label, description, location, None,
            {'ext1': 'val1', 'ext2': 'val2'})
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._hosted_service_exists(self.hosted_service_name))

        # Act
        label = 'ptvslabelupdate'
        description = 'ptvs description update'
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

        # Act
        result = self.sms.delete_hosted_service(self.hosted_service_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(self._hosted_service_exists(self.hosted_service_name))

    @record
    def test_create_get_delete_deployment(self):
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

        # Act
        result = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, deployment_name)
        self.assertEqual(result.deployment_slot, 'Production')
        self.assertIsNotNone(result.label)
        self.assertIsNotNone(result.configuration)

        # Act
        result = self.sms.delete_deployment(
            self.hosted_service_name, deployment_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(
            self._deployment_exists(self.hosted_service_name, deployment_name))

    @record
    def test_delete_deployment_with_vhd(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_linux(service_name, deployment_name, role_name)
        self.assertTrue(
            self._blob_exists(self.container_name, role_name + '.vhd'))

        # Act
        result = self.sms.delete_deployment(
            self.hosted_service_name, deployment_name, delete_vhd=True)
        self._wait_for_async(result.request_id)

        # Assert
        # Blob is taking 30 minutes to delete currently after the async id comes back
        timeToSleep = 30 * 60
        count = 0
        while self._blob_exists(self.container_name, role_name + '.vhd'):
            if count >= timeToSleep:
                self.assertFalse(True, "Blob exists")
            else:
                self.sleep(5)
                count += 5
        print("Time to run:", count)
        self.assertFalse(
            self._deployment_exists(self.hosted_service_name, deployment_name))

    @record
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

    @record
    def test_change_deployment_configuration(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        configuration = _encode_base64(DEPLOYMENT_UPDATE_CONFIG)

        # Act
        result = self.sms.change_deployment_configuration(
            self.hosted_service_name, deployment_name, configuration)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        self.assertTrue(props.configuration.find('Instances count="4"') >= 0)

    @record
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

    @record
    def test_upgrade_deployment(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        package_url = self._upload_default_package_to_storage_blob('updated')
        configuration = _encode_base64(DEPLOYMENT_UPDATE_CONFIG)

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

    @record
    def test_walk_upgrade_domain(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        package_url = self._upload_default_package_to_storage_blob('updated')
        configuration = _encode_base64(DEPLOYMENT_UPDATE_CONFIG)
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

    @record
    @unittest.skip('no longer works, upgrade completes too quickly?')
    def test_rollback_update_or_upgrade(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        package_url = self._upload_default_package_to_storage_blob(
            'updated207')
        configuration = _encode_base64(DEPLOYMENT_UPDATE_CONFIG)

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

    @record
    def test_reboot_rebuild_reimage_delete_role_instance(self):
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

        # Act
        result = self.sms.rebuild_role_instance(
            self.hosted_service_name, deployment_name, role_instance_name)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        status = self._get_role_instance_status(props, role_instance_name)
        self.assertTrue(status == 'StoppedVM' or status == 'ReadyRole')

        # Act
        result = self.sms.reimage_role_instance(
            self.hosted_service_name, deployment_name, role_instance_name)
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        status = self._get_role_instance_status(props, role_instance_name)
        self.assertTrue(status == 'StoppedVM' or status == 'ReadyRole')

        # Act
        result = self.sms.delete_role_instances(
            self.hosted_service_name, deployment_name, [role_instance_name])
        self._wait_for_async(result.request_id)

        # Assert
        props = self.sms.get_deployment_by_name(
            self.hosted_service_name, deployment_name)
        status = self._get_role_instance_status(props, role_instance_name)
        self.assertIsNone(status)

    @record
    def test_check_hosted_service_name_availability_not_available(self):
        # Arrange
        self._create_hosted_service(self.hosted_service_name)

        # Act
        result = self.sms.check_hosted_service_name_availability(
            self.hosted_service_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertFalse(result.result)

    @record
    def test_check_hosted_service_name_availability_available(self):
        # Arrange

        # Act
        result = self.sms.check_hosted_service_name_availability(
            self.hosted_service_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(result.result)

    #--Test cases for service certificates -------------------------------
    @record
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

    @record
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

    @record
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

    @record
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
    @record
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

    @record
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
    @record
    def test_get_subscription(self):
        # Arrange

        # Act
        result = self.sms.get_subscription()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.subscription_id,
                         self.settings.SUBSCRIPTION_ID)
        self.assertIsNotNone(result.account_admin_live_email_id)
        self.assertIsNotNone(result.service_admin_live_email_id)
        self.assertIsNotNone(result.subscription_name)
        self.assertIsNotNone(result.subscription_status)
        self.assertTrue(result.current_core_count >= 0)
        self.assertTrue(result.current_hosted_services >= 0)
        self.assertTrue(result.current_storage_accounts >= 0)
        self.assertTrue(result.current_virtual_network_sites >= 0)
        self.assertTrue(result.max_core_count > 0)
        self.assertTrue(result.max_dns_servers > 0)
        self.assertTrue(result.max_hosted_services > 0)
        self.assertTrue(result.max_local_network_sites > 0)
        self.assertTrue(result.max_storage_accounts > 0)
        self.assertTrue(result.max_virtual_network_sites > 0)
        self.assertGreater(len(result.aad_tenant_id), 0)

    #--Test cases for retrieving subscription operations --------------------
    @record
    def test_list_subscription_operations(self):
        # This is based on the current date, so this test runs live only
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange

        # Act
        now = datetime.now()
        one_month_before = now - timedelta(30)
        result = self.sms.list_subscription_operations(one_month_before.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))
        # Assert
        self.assertIsNotNone(result)
        for operation in result.subscription_operations:
            self.assertTrue(operation.operation_id)
            self.assertTrue(operation.operation_status.status_id)


    #--Test cases for reserved ip addresses  -----------------------------
    @record
    def test_create_reserved_ip_address(self):
        # Arrange
        self.reserved_ip_address = self.get_resource_name('ip')

        # Act
        result = self.sms.create_reserved_ip_address(
            self.reserved_ip_address,
            'mylabel',
            'West US')
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._reserved_ip_address_exists(self.reserved_ip_address))

    @record
    def test_delete_reserved_ip_address(self):
        # Arrange
        self._create_reserved_ip_address()

        # Act
        result = self.sms.delete_reserved_ip_address(self.reserved_ip_address)
        self._wait_for_async(result.request_id)
        self.reserved_ip_address = None

        # Assert
        self.assertFalse(
            self._reserved_ip_address_exists(self.reserved_ip_address))

    @record
    def test_associate_reserved_ip_address(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        update_result = self.sms.update_deployment_status(
            self.hosted_service_name,
            deployment_name,
            'Running'
        )
        self._create_reserved_ip_address()
        self._wait_for_async(update_result.request_id)

        # Act
        result = self.sms.associate_reserved_ip_address(
            self.reserved_ip_address,
            self.hosted_service_name,
            deployment_name
        )
        self._wait_for_async(result.request_id)
        result = self.sms.get_hosted_service_properties(
            self.hosted_service_name, True
        )

        # Assert
        self.assertTrue(
            result.deployments[0].virtual_ips[0].is_reserved
        )

    @record
    def test_disassociate_reserved_ip_address(self):
        # Arrange
        deployment_name = 'utdeployment'
        self._create_hosted_service_with_deployment(
            self.hosted_service_name, deployment_name)
        self._create_reserved_ip_address()
        update_result = self.sms.update_deployment_status(
            self.hosted_service_name,
            deployment_name,
            'Running'
        )
        self._wait_for_async(update_result.request_id)
        result = self.sms.associate_reserved_ip_address(
            self.reserved_ip_address,
            self.hosted_service_name,
            deployment_name
        )
        self._wait_for_async(result.request_id)

        # Assert
        result = self.sms.disassociate_reserved_ip_address(
            self.reserved_ip_address,
            self.hosted_service_name,
            deployment_name
        )
        self._wait_for_async(result.request_id)
        result = self.sms.get_hosted_service_properties(
            self.hosted_service_name, True
        )
        self.assertFalse(
            result.deployments[0].virtual_ips[0].is_reserved
        )


    @record
    def test_get_reserved_ip_address(self):
        # Arrange
        self._create_reserved_ip_address()

        # Act
        result = self.sms.get_reserved_ip_address(self.reserved_ip_address)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, self.reserved_ip_address)
        self.assertEqual(result.label, 'mylabel')
        self.assertEqual(result.location, 'West US')
        self.assertGreater(len(result.address), 0)
        self.assertGreater(len(result.id), 0)
        self.assertGreater(len(result.state), 0)
        self.assertFalse(result.in_use)
        self.assertEqual(len(result.service_name), 0)
        self.assertEqual(len(result.deployment_name), 0)

    @record
    def test_list_reserved_ip_addresses(self):
        # Arrange
        self._create_reserved_ip_address()

        # Act
        result = self.sms.list_reserved_ip_addresses()

        # Assert
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

        found = [ip for ip in result if ip.name == self.reserved_ip_address]
        self.assertEqual(len(found), 1)

    #--Test cases for virtual machines -----------------------------------
    @record
    def test_create_virtual_machine_deployment_linux_vm_image(self):
        vm_image_name = self.settings.LINUX_VM_IMAGE_NAME
        if not vm_image_name:
            self.assertTrue(False, 'LINUX_VM_IMAGE_NAME not set in test settings file.')

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
        host_name = self._host_name_from_role_name(role_name)
        system = self._linux_config(host_name)
        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production', deployment_label,
            role_name, system_config=system, os_virtual_hard_disk=None,
            role_size='Small', vm_image_name=vm_image_name
            )

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name))
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(deployment.label, deployment_label)

    @unittest.skip('The resource extension used here no longer exists, need to find a new one')
    @record
    def test_create_virtual_machine_deployment_linux_resource_extension(self):
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
        extensions = ResourceExtensionReferences()
        extensions.resource_extension_references.append(
            ResourceExtensionReference('LinuxChefClientReference',
                                       'Chef.Bootstrap.WindowsAzure',
                                       'LinuxChefClient',
                                       '11.16'))

        result = self.sms.create_virtual_machine_deployment(
            service_name, deployment_name, 'production', deployment_label,
            role_name, system, os_hd, network, role_size='Small',
            resource_extension_references=extensions,
            provision_guest_agent=True
            )

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(service_name, deployment_name)
        self._wait_for_role(service_name, deployment_name, role_name)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name))
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(deployment.label, deployment_label)

    @record
    def test_create_virtual_machine_deployment_linux_remote_source_image(self):
        source_image_link = self.settings.LINUX_VM_REMOTE_SOURCE_IMAGE_LINK
        if not source_image_link:
            self.assertTrue(False,
                'LINUX_VM_REMOTE_SOURCE_IMAGE_LINK not set in test settings file.')

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
        os_hd.remote_source_image_link = source_image_link
        os_hd.os = 'Linux'
        os_hd.disk_name = role_name
        os_hd.source_image_name = None

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

    @unittest.skip('Enable this manually if you have the required virtual network')
    @record
    def test_create_virtual_machine_deployment_windows_virtual_network(self):
        # this test requires the following manual resources to be created
        # use the azure portal to create them
        affinity_group = 'utaffgrpdonotdelete'    # affinity group, any region
        # storage account in affinity group
        storage_name = 'utstoragedonotdelete'
        # virtual network in affinity group
        virtual_network_name = 'utnetdonotdelete'
        subnet_name = u'啊齄丂狛狜'                # subnet in virtual network

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
        role = self.sms.get_role(service_name, deployment_name, role_name)
        self.assertIsNotNone(role)
        self.assertEqual(role.configuration_sets.configuration_sets[0].subnet_names[0],
                         subnet_name)
        deployment = self.sms.get_deployment_by_name(
            service_name, deployment_name)
        self.assertEqual(deployment.label, deployment_label)

    @record
    def test_add_role_linux(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_linux(service_name, deployment_name, role_name1)

        # Act
        result = self.sms.get_role(service_name, deployment_name, role_name1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.role_name, role_name1)
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

    @record
    def test_add_update_delete_role_windows(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_windows(service_name, deployment_name, role_name1)
        self._add_role_windows(service_name, deployment_name, role_name2, '59914')

        # Act
        result = self.sms.get_role(service_name, deployment_name, role_name1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.role_name, role_name1)
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

        # Act
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        network.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint('endupdate', 'tcp', '50055', '5555'))
        result = self.sms.update_role(service_name, deployment_name, role_name1,
                                      network_config=network,
                                      role_size='Medium')
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1)

        # Assert
        role = self.sms.get_role(service_name, deployment_name, role_name1)
        self.assertEqual(role.role_size, 'Medium')

        # Act
        result = self.sms.delete_role(service_name, deployment_name, role_name2, False)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._role_exists(service_name, deployment_name, role_name1))
        self.assertFalse(
            self._role_exists(service_name, deployment_name, role_name2))

    @record
    def test_shutdown_start_restart_role(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name1 = self.hosted_service_name + 'a'
        role_name2 = self.hosted_service_name + 'b'

        self._create_vm_windows(service_name, deployment_name, role_name1)
        self._add_role_windows(service_name, deployment_name, role_name2, '59914')

        # Act
        result = self.sms.shutdown_role(service_name, deployment_name, role_name1)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1, 'StoppedVM')

        # Act
        result = self.sms.start_role(service_name, deployment_name, role_name1)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1)

        # Act
        result = self.sms.restart_role(service_name, deployment_name, role_name1)
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1)

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

        # Act
        result = self.sms.shutdown_role(service_name, deployment_name,
                                        role_name1, 'StoppedDeallocated')
        self._wait_for_async(result.request_id)
        self._wait_for_role(service_name, deployment_name, role_name1,
                            'StoppedDeallocated')

    @record
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

    @record
    def test_list_resource_extensions(self):
        # Arrange

        # Act
        result = self.sms.list_resource_extensions()

        # Assert
        self.assertGreater(len(result), 0)
        for ext in result:
            self.assertGreater(len(ext.description), 0)
            self.assertGreater(len(ext.label), 0)
            self.assertGreater(len(ext.name), 0)
            self.assertGreater(len(ext.publisher), 0)
            self.assertGreater(len(ext.version), 0)

    @record
    def test_list_resource_extension_versions(self):
        # Arrange
        publisher = 'Chef.Bootstrap.WindowsAzure'
        name = 'ChefClient'

        # Act
        result = self.sms.list_resource_extension_versions(
            publisher, name)

        # Assert
        self.assertGreater(len(result), 0)
        for ext in result:
            self.assertEqual(ext.name, name)
            self.assertEqual(ext.publisher, publisher)
            self.assertGreater(len(ext.description), 0)
            self.assertGreater(len(ext.label), 0)
            self.assertGreater(len(ext.version), 0)

    @record
    def test_add_update_delete_dns_server(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_windows(service_name, deployment_name, role_name)

        # Act
        result = self.sms.add_dns_server(service_name,
                                         deployment_name,
                                         'mydnsserver',
                                         '192.168.144.1')
        self._wait_for_async(result.request_id)

        result = self.sms.update_dns_server(service_name,
                                         deployment_name,
                                         'mydnsserver',
                                         '192.168.144.2')
        self._wait_for_async(result.request_id)

        result = self.sms.delete_dns_server(service_name,
                                         deployment_name,
                                         'mydnsserver')
        self._wait_for_async(result.request_id)

        # Assert

    #--Test cases for virtual machine images -----------------------------
    @record
    def test_capture_vm_image(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_linux(service_name, deployment_name, role_name)

        # Act
        image_name = role_name + 'image'
        image = CaptureRoleAsVMImage('Specialized',
                                     image_name,
                                     image_name + 'label',
                                     image_name + 'description',
                                     'english',
                                     'mygroup')

        result = self.sms.capture_vm_image(
            service_name,
            deployment_name,
            role_name,
            image)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertIsNotNone(result)
        images = self.sms.list_vm_images()
        found_image = [im for im in images if im.name == image_name][0]
        self.assertEqual(found_image.category, 'User')
        self.assertEqual(found_image.label, image.vm_image_label)
        self.assertEqual(found_image.description, image.description)
        self.assertEqual(found_image.language, image.language)
        self.assertEqual(found_image.image_family, image.image_family)
        self.assertEqual(found_image.os_disk_configuration.os_state, image.os_state)
        self.assertEqual(found_image.os_disk_configuration.os, 'Linux')

    @record
    def test_create_vm_image(self):
        # Arrange
        image_name = self.hosted_service_name + 'image'
        media_link = self._copy_linux_os_vhd_to_container()

        # Act
        img = VMImage()
        img.name = image_name
        img.label = image_name + 'label'
        img.description = image_name + 'description'
        img.os_disk_configuration.os_state = 'Specialized'
        img.os_disk_configuration.os = 'Linux'
        img.os_disk_configuration.media_link = media_link
        img.language = 'English'
        img.show_in_gui = True

        result = self.sms.create_vm_image(img)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertIsNotNone(result)
        images = self.sms.list_vm_images()
        found_image = [im for im in images if im.name == image_name][0]
        self.assertEqual(found_image.category, 'User')
        self.assertEqual(found_image.label, img.label)
        self.assertEqual(found_image.description, img.description)
        self.assertEqual(found_image.language, img.language)
        self.assertEqual(found_image.show_in_gui, img.show_in_gui)
        self.assertEqual(found_image.os_disk_configuration.os_state, 'Specialized')
        self.assertEqual(found_image.os_disk_configuration.os, 'Linux')

    @record
    def test_delete_vm_image(self):
        # Arrange
        image_name = self.hosted_service_name + 'image'
        self._create_vm_image(image_name)

        # Act
        result = self.sms.delete_vm_image(image_name, True)
        self._wait_for_async(result.request_id)

        # Assert
        images = self.sms.list_vm_images()
        found_images = [im for im in images if im.name == image_name]
        self.assertEqual(len(found_images), 0)

    @record
    def test_list_vm_images(self):
        # Arrange

        # Act
        result = self.sms.list_vm_images()

        # Assert
        self.assertGreater(len(result), 0)
        for image in result:
            if image.category == 'Public':
                self.assertGreater(len(image.name), 0)
                self.assertGreater(len(image.category), 0)
                self.assertGreater(len(image.label), 0)
                self.assertGreater(len(image.location), 0)
                self.assertGreater(len(image.publisher_name), 0)
                self.assertIsNone(image.deployment_name)
                self.assertIsNone(image.role_name)
                self.assertIsNone(image.service_name)

    @record
    def test_list_vm_images_location(self):
        # Arrange
        loc = 'West US'

        # Act
        result = self.sms.list_vm_images(location=loc)

        # Assert
        self.assertGreater(len(result), 0)
        for image in result:
            regions = image.location.split(';')
            self.assertIn(loc, regions)

    @record
    def test_list_vm_images_location_publisher(self):
        # Arrange
        pub = 'Cloudera'

        # Act
        result = self.sms.list_vm_images(publisher=pub)

        # Assert
        self.assertGreater(len(result), 0)
        for image in result:
            self.assertEqual(image.publisher_name, pub)

    @record
    def test_list_vm_images_location_category(self):
        # Arrange
        cat = 'Public'

        # Act
        result = self.sms.list_vm_images(category=cat)

        # Assert
        self.assertGreater(len(result), 0)
        for image in result:
            self.assertEqual(image.category, cat)

    @record
    def test_list_vm_images_location_publisher_and_category(self):
        # Arrange
        pub = 'Cloudera'
        cat = 'Public'

        # Act
        result = self.sms.list_vm_images(publisher=pub, category=cat)

        # Assert
        self.assertGreater(len(result), 0)
        for image in result:
            self.assertEqual(image.category, cat)
            self.assertEqual(image.publisher_name, pub)

    @record
    def test_update_vm_image(self):
        # Arrange
        image_name = self.hosted_service_name + 'image'
        self._create_vm_image(image_name)

        # Act
        updated_image = VMImage()
        updated_image.label = 'Updated label'
        updated_image.description = 'Updated description'
        updated_image.eula = 'Updated eula'
        updated_image.os_disk_configuration.host_caching = 'ReadOnly'
        result = self.sms.update_vm_image(image_name, updated_image)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertIsNotNone(result)
        images = self.sms.list_vm_images()
        found_image = [im for im in images if im.name == image_name][0]
        self.assertEqual(found_image.label, updated_image.label)
        self.assertEqual(found_image.description, updated_image.description)
        self.assertEqual(found_image.eula, updated_image.eula)
        self.assertEqual(found_image.os_disk_configuration.host_caching,
                         updated_image.os_disk_configuration.host_caching)

    #--Test cases for operating system images ----------------------------
    @record
    def test_list_os_images(self):
        # Arrange
        media_url = self.settings.LINUX_OS_VHD
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

    @record
    def test_list_os_images_public(self):
        # Arrange

        # Act
        result = self.sms.list_os_images()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        image_attributes = {}
        for temp in result:
            self.assertIn(temp.category, ['User', 'Public', 'Private', 'MSDN'])
            for attr in temp.__dict__:
                if getattr(temp, attr):
                    image_attributes[attr] = getattr(temp, attr)

        self.assertTrue(image_attributes['category'])
        self.assertTrue(image_attributes['label'])
        self.assertTrue(image_attributes['logical_size_in_gb'])
        self.assertTrue(image_attributes['name'])
        self.assertTrue(image_attributes['os'])
        self.assertTrue(image_attributes['eula'])
        self.assertTrue(image_attributes['description'])
        self.assertTrue(image_attributes['image_family'])
        self.assertTrue(image_attributes['show_in_gui'])
        self.assertTrue(image_attributes['published_date'])
        self.assertTrue(image_attributes['is_premium'])
        self.assertTrue(image_attributes['icon_uri'])
        self.assertTrue(image_attributes['privacy_uri'])
        self.assertTrue(image_attributes['recommended_vm_size'])
        self.assertTrue(image_attributes['publisher_name'])
        self.assertTrue(image_attributes['small_icon_uri'])

    @record
    def test_get_os_image(self):
        # Arrange
        media_url = self.settings.LINUX_OS_VHD
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

    @record
    def test_get_os_image_details(self):
        # Arrange
        media_url = self.settings.LINUX_OS_VHD
        os = 'Linux'
        self._create_os_image(self.os_image_name, media_url, os)
        os_image = self.sms.get_os_image(self.os_image_name)
        locations = ['West US', 'West Europe']
        result = self.sms.replicate_vm_image(
            self.os_image_name,
            locations,
            self.os_image_name,
            self.os_image_name,
            '1.2.3'
        )
        self._wait_for_async(result.request_id)

        # Act
        result = self.sms.get_os_image_details(self.os_image_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.replication_progress)
        result_locations = [e.location for e in result.replication_progress]
        self.assertEqual(locations.sort(), result_locations.sort())

    @record
    def test_add_os_image(self):
        # Arrange

        # Act
        result = self.sms.add_os_image(
            'utcentosimg', self.settings.LINUX_OS_VHD, self.os_image_name, 'Linux')
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._os_image_exists(self.os_image_name))

    @record
    def test_update_os_image(self):
        # Arrange
        self._create_os_image(self.os_image_name, self.settings.LINUX_OS_VHD, 'Linux')

        # Act
        result = self.sms.update_os_image(
            self.os_image_name, 'newlabel', self.settings.LINUX_OS_VHD,
            self.os_image_name, 'Linux')
        self._wait_for_async(result.request_id)

        # Assert
        image = self.sms.get_os_image(self.os_image_name)
        self.assertEqual(image.label, 'newlabel')
        self.assertEqual(image.os, 'Linux')

    @record
    def test_update_os_image_from_image_reference(self):
        # Arrange
        self._create_os_image(
            self.os_image_name, self.settings.LINUX_OS_VHD, 'Linux'
        )

        # Act
        os_image = self.sms.get_os_image(self.os_image_name)
        os_image.label = 'newlabel'
        os_image.media_link = self.settings.LINUX_OS_VHD
        os_image.os = 'Linux'
        os_image.name = self.os_image_name
        # Partial date, will be converted to full ISO8601 Z date
        os_image.published_date = '2016-09-09'
        # Update to the opposite of what is currently in place, to be sure we changed something
        current_show_in_gui = os_image.show_in_gui
        os_image.show_in_gui = not current_show_in_gui
        result = self.sms.update_os_image_from_image_reference(
            self.os_image_name, os_image
        )
        self._wait_for_async(result.request_id)

        # Assert
        image = self.sms.get_os_image(
            self.os_image_name
        )
        self.assertEqual(
            image.label, 'newlabel'
        )
        self.assertEqual(
            image.os, 'Linux'
        )
        self.assertEqual(
            image.published_date, '2016-09-09T00:00:00Z'
        )
        self.assertEqual(
            image.show_in_gui, not current_show_in_gui
        )

    @record
    def test_delete_os_image(self):
        # Arrange
        self._create_os_image(self.os_image_name, self.settings.LINUX_OS_VHD, 'Linux')

        # Act
        result = self.sms.delete_os_image(self.os_image_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(self._os_image_exists(self.os_image_name))

    #--Test cases for virtual machine data disks -------------------------
    @record
    def test_add_data_disk_from_url(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_linux(service_name, deployment_name, role_name)

        # Act
        lun = 0
        label = 'disk' + str(lun)
        url = self._upload_disk_to_storage_blob(label)
        result = self.sms.add_data_disk(
            service_name,
            deployment_name,
            role_name,
            lun,
            disk_label=label,
            source_media_link=url,
        )
        self.data_disk_infos.append((service_name, deployment_name, role_name, lun))
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._data_disk_exists(service_name, deployment_name, role_name, lun))

        # Act
        result = self.sms.get_data_disk(service_name, deployment_name, role_name, lun)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.disk_label, label)
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

        # Act
        result = self.sms.delete_data_disk(
            service_name,
            deployment_name,
            role_name,
            lun,
            delete_vhd=True,
        )
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(self._data_disk_exists(service_name, deployment_name, role_name, lun))

    @record
    def test_add_data_disk_from_disk_name(self):
        # Arrange
        service_name = self.hosted_service_name
        deployment_name = self.hosted_service_name
        role_name = self.hosted_service_name

        self._create_vm_linux(service_name, deployment_name, role_name)

        # Act
        lun = 0
        label = 'disk' + str(lun)
        url = self._upload_disk_to_storage_blob(label)
        self._create_disk(self.disk_name, 'Linux', url)
        result = self.sms.add_data_disk(
            service_name,
            deployment_name,
            role_name,
            lun,
            disk_label=label,
            disk_name=self.disk_name,
        )
        self.data_disk_infos.append((service_name, deployment_name, role_name, lun))
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(self._data_disk_exists(service_name, deployment_name, role_name, lun))

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

    #--Test cases for virtual machine disks ------------------------------
    @record
    def test_add_update_delete_get_list_disk(self):
        # Arrange
        url = self._upload_disk_to_storage_blob('disk')

        # Act
        result = self.sms.add_disk(
            None, 'ptvslabel', url, self.disk_name, 'Windows')

        # Assert
        self.assertIsNone(result)
        self.assertTrue(self._disk_exists(self.disk_name))

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

        # Act
        result = self.sms.update_disk(
            self.disk_name, None, 'ptvslabelupdate', None, None, None)

        # Assert
        self.assertIsNone(result)
        disk = self.sms.get_disk(self.disk_name)
        self.assertEqual(disk.name, self.disk_name)
        self.assertEqual(disk.label, 'ptvslabelupdate')
        self.assertEqual(disk.media_link, url)

        # Act
        result = self.sms.delete_disk(self.disk_name)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._disk_exists(self.disk_name))

    def test_getpublishsettings(self):
        # File Data has fake certificate that doesn't access anything...
        file_text = '''<?xml version="1.0" encoding="utf-8"?>
<PublishData>
  <PublishProfile
    SchemaVersion="2.0"
    PublishMethod="AzureServiceManagementAPI">
    <Subscription
      ServiceManagementUrl="https://management.core.windows.net"
      Id="cafecafe-cafe-1234-1234-1234cafe0001"
      Name="Microsoft Azure Internal Consumption"
      ManagementCertificate="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" />
    <Subscription
      ServiceManagementUrl="https://management.core.windows.net"
      Id="cafecafe-cafe-1234-1234-1234cafe0002"
      Name="Subscription Something Something"
      ManagementCertificate="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" />
    <Subscription
      ServiceManagementUrl="https://management.core.windows.net"
      Id="cafecafe-cafe-1234-1234-1234cafe0003"
      Name="Work Subscription Something"
      ManagementCertificate="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" />
   </PublishProfile>
</PublishData>
'''

        # PEM Data Expected
        expected_1 = '''-----BEGIN CERTIFICATE-----
MIICxDCCAaygAwIBAgIQQvBMxylMmpdO1es6dugzizANBgkqhkiG9w0BAQUFADAe
MRwwGgYDVQQDExNXaW5kb3dzIEF6dXJlIFRvb2xzMB4XDTE1MDIyNTIyMDQ0MFoX
DTE2MDIyNTIyMDQ0MFowHjEcMBoGA1UEAxMTV2luZG93cyBBenVyZSBUb29sczCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAJ7VVwiLYIuE8wtmyPXSPYph
SH4JiN+BSDTR/T7JYBi/H+MtJfTA3k9NqaQbyngoOLe66GlX4l2KlDDp+EUjjMBk
zTEce0YKSLmvcTSofxExe45HkU4tpM/RWwU1CmonrwS8+htSiN3vQcJsgqdnCBYV
+lVinWHEPjzK7kPUBK+EDynlVPCKhXoIvDu4vpjXNEIrGOiB4Lays/P1Mu9hWk67
EEVTE9Z/WEAd8XY+LJ2niRXdUHNqd4PtWU5ZrFD0Jqx3saHS7wH2cSsvvl5+qBya
Mb8j3Qzx/6oudLrutViPmUtrPPVKxfgA/SaVVJxUdT16o+6ZQCeyZ52AfrS5WR8C
AwEAATANBgkqhkiG9w0BAQUFAAOCAQEAEBNTzQcPIlRd7POPHK9WDJEoVkZkrxdH
Kt0YSbeMdLIbw6abaybNqg7t+8XLQWLHYh+AE9p24aK8c+2UO3Nrk3fbQnx3DGdA
zqZ0UnUByR/o6L4ilXQ5heMEcOPtFHueVQhCvUnX2/ug4b8ObbkUvD7Q5wUas0oJ
y4qkcsvGvK/Xb12ADYWgqFut/C0kYsjSzqqlwQ9sP98F0kP28/HrJyK5Uj4CVYNr
vxzn2mBBTaNgo8QKwhxf01kDJm/ie3a9Vz15dxz65B6Cda0Ay7uYyxz5Zd46AfkJ
cfEckDRmpyNS233CAYTx3GUG6w3iGpXVVjZfa9dYa6cqjYk/X7TElA==
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCe1VcIi2CLhPML
Zsj10j2KYUh+CYjfgUg00f0+yWAYvx/jLSX0wN5PTamkG8p4KDi3uuhpV+JdipQw
6fhFI4zAZM0xHHtGCki5r3E0qH8RMXuOR5FOLaTP0VsFNQpqJ68EvPobUojd70HC
bIKnZwgWFfpVYp1hxD48yu5D1ASvhA8p5VTwioV6CLw7uL6Y1zRCKxjogeC2srPz
9TLvYVpOuxBFUxPWf1hAHfF2Piydp4kV3VBzaneD7VlOWaxQ9Casd7Gh0u8B9nEr
L75efqgcmjG/I90M8f+qLnS67rVYj5lLazz1SsX4AP0mlVScVHU9eqPumUAnsmed
gH60uVkfAgMBAAECggEAGI5v+/Xd1v7sEKQzMluZ1iN/m1+Kq3uHwrArO3d+MEqZ
pHwzdRQTNXw9W7j25FLbn1RPYGdiVlykLVfPDD7DIRpfOwDl8jM0K+PQWHgrL75Q
avPs/C2ZteOZSJnQYrnV7kvv+HoZ3QODot/h51Mfm0KJ8do4Q4hH/bV7gZMYUluV
ul2KTShFaICtH2YiaXBQU1BKp4V4c0xG4CGqIuNKJp6ZI8XlksZt7gKXZWEzHRdE
6G2wv7FbHyZ7qpJ1zec0CX+oeARlC3IYxCnQQr/lA73fd87OcXzaZETmdCDc/NG0
YXgS4p89BKWUqtcmnwYyKjFt8mjyW4doY9LCrGhyMQKBgQDSgsqTUnnnzo746Zcb
nUoY5bqWPQFsR9Mok4Y2cJIVpeOiOJ7XfLc8mE9MnWGMGpHcf0uVTOn+xpG7bV7w
kJUc3oqSXzaw54/IJ3CiSUCvNr2hPw+Qd63F/3P58MND4o9vcgMCWk6wxUL7JolE
v/WM5hjPv/gxp5geVXeFDhp9uQKBgQDBJ880Ht8ff7ahBD9r1H9X0qIqqnztQDkO
Zwf0Y1F6XBlnkn5ASsHIQDrp8OQpGWfWjbpe3tzW0PC47bOigHuOahv/x2sf5dpy
hLrYjxYCCVIPr+8VvaIuztnXYRLMP5phRO9IHy4M7kp1xgqxwjm0Do9Yd/6uIAxx
VqSqm3M5lwKBgHmOIpFtN41eHfqnT6UXbxjvVo24TmELHGg6v24iFIjBkK80iKwf
jONFg8zWt+Qh14X+T1O35QpD+RTEM+UvZ5sS+etJZZhDLihCdeyP5fUG4/r/Ieqm
4MYLGxoBJ4/EfFS6/ffW08eJMIM7nln/ijfBCiS0UgnCH7msWmaPXUapAoGAWkTk
jRMwa2QgUbfOe/JfYQfLSe1LXQV6pMR57zjLR0frh3/rCNjnH1MFNXei6aI56Qdr
ZhL5WltjZMmR/gvVsoTcePkVk160bHijabnVKzZ352Ttc1egiAebvxBa3KGM4JB6
01XfC6QBoHDhZpnCped4DnxlxbKsnftEEYd8nhkCgYEAh2dYaZMqyJaa6dIj4Avl
J8UKCxH979Vj6eApDep8XlS5h0ChRJaeu/eX4oFDWLFPmtbCJfe2j2Ps2kETCFny
fWF6qke/UVOElVpXW1yafCMIhrOjK7BbABY7j86raU1LEbsLJbP04Dm3a8avsFOA
O9XErMuCOGgE+bN+tU73mEk=
-----END PRIVATE KEY-----
'''

        expected_3 = '''-----BEGIN CERTIFICATE-----
MIICxDCCAaygAwIBAgIQFPbRBG46y71I+QhH1J8KDTANBgkqhkiG9w0BAQUFADAe
MRwwGgYDVQQDExNXaW5kb3dzIEF6dXJlIFRvb2xzMB4XDTE1MDIyNTIyMDQ0MVoX
DTE2MDIyNTIyMDQ0MVowHjEcMBoGA1UEAxMTV2luZG93cyBBenVyZSBUb29sczCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKjwMItYomg5PyXaDZ97fRMw
A8yG7R+F9w2qM0n0gySaIN04JFxN+j0KQ72JeM20ij5kFvH3nN2PaNSvZyuj/Ix4
nbK+4joORtJ0HK8ZYWN7Fz0ANOB8kyqD+fk/4dHd6HBvyqJexoHWfMBxd7KFi+xC
bM3e0rf9rx4Pec8adU7Xj8RH1IP4tOmabqUSUyI5tg0d+wE/D3j8uMkzPGT4IZLk
f+H6j9HovnJoShVGTOUDe6+lkCLmLkxNBo32fU1FJPLWJcAsz9YumZCQud18YUsf
BKQ40sdDtDcEYQZGVltKeJjqhlcLEf6/B9MmdTgEABIKx7b6mDwI3h1zdVc0lO0C
AwEAATANBgkqhkiG9w0BAQUFAAOCAQEADYAhe7KMz77/Lm9hr+hjboM2JZJ85MI8
NEPQQBDJcZn96d8jkY5ycokcqHCjhw+D8zpXJ+krpxJ341crWNV1MH7qLUu+JVj4
XVXeT28pIFtQqmwSJ90UYggPBSgSS8aB1A1m3ka0K8GrEMtHTZxTc35YTGeAf+96
l8sGBMoySeVDJSD/bJVoI7EWceYUGvCMeF8Ef88LR+3SgPdZmoyoa4lhlyeeabRJ
saif2eu6kbESVIc4UEe5DnzUjy+/S6oT3wmL4tuYc7kQAXaqWx9RYewL2d6QddaU
si3Ihl9xNOFcA7vMBFyKJYQweBVY5ix+CSRg/qt1zRNMiCwlG3uQXQ==
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCo8DCLWKJoOT8l
2g2fe30TMAPMhu0fhfcNqjNJ9IMkmiDdOCRcTfo9CkO9iXjNtIo+ZBbx95zdj2jU
r2cro/yMeJ2yvuI6DkbSdByvGWFjexc9ADTgfJMqg/n5P+HR3ehwb8qiXsaB1nzA
cXeyhYvsQmzN3tK3/a8eD3nPGnVO14/ER9SD+LTpmm6lElMiObYNHfsBPw94/LjJ
Mzxk+CGS5H/h+o/R6L5yaEoVRkzlA3uvpZAi5i5MTQaN9n1NRSTy1iXALM/WLpmQ
kLndfGFLHwSkONLHQ7Q3BGEGRlZbSniY6oZXCxH+vwfTJnU4BAASCse2+pg8CN4d
c3VXNJTtAgMBAAECggEAG5DbvvUWxQ5oRy8iL26JPWcFi6tNiGoF4sEtrsja2E9d
AvPc/QHNTgX9gTEsGNa3gxA2bUOj4UQ8DQ5U9ZpDxJEO3GKIzAPV2xPOtWSdD0w/
wbilqCazpcmUsa7SlHnS6nvXUvDHj9qVjxpEt4jSiNna4qnT9OlMWImabOiKkTNX
ZqheHw6cK15JQ2zUpjUj39jAh+PPVNaVZjsvf9HjnIPZT2NAaiP8uOs/I5X2Y5Tn
HeeyvovimA/FUheNIstgAIaJ9VNHFckh3NU73iLLvPPLRF14j9z61d4rnbg9tNR/
PYv11KwWmwUjd07f2BqUepnm58DB1QzE6eCkvxUoiQKBgQDsrnTcQpZ7aqTPm8z1
4+ysiUXjakjXkYvOmMU1TmP2Kb4GCuytRZoY6LxJ/XOk7aMXTS5qrvEptXzQ7ExH
YqVusdiXIrOWsLiuvnY8wJJTER2p6OmV0TSv3rrign3EHgwL7G77mUDHrhynJRxx
IXX9jfNwpxiQ/2Cg+3B3ToAu9QKBgQC2ujbZdZuHl5gOwWc2ZqxotzJaFuWTSFGy
x8JwFeGYvMn0fjJFdJ2gGY8tGMi0ON4Dr8+8XCP1mTRZnYznT05UVsAOwMc5rvZX
dSzTzMqyvi9WHpwUKq6aXp5uUQknsKfqvhvoYF6NGlD8EhElbhKEdCaHhG1XKyrK
zTe1oWKjGQKBgQCcfWz/BXgB+i0mp9kI677dBZaUGv42qiFKZHBgIoithkQCMs7y
cgbFWXzFXzNLZWRkT7/VAf6qmTkB2ntE59CCNE0FAQjFJeu2fnAnExysl7CJW1q2
mDDB5/6hLa6CMWu9poJrEJVocZK4YS1BD+K311eSsKjpljEJv7ZI7DqM0QKBgHHH
ce/mc3nywxQtCX+uXxy1Nf0y1LDpDzYrfL8eYOMiav56tgLZomzWfXivPgo6fsP8
7XV0Sk/bneVPXTWLBFMv0VdeYq9garP6mncnxe+WzRLq7HUCPsaQtEYs325/aY+Z
4PbJSxbBlDvhZBvSdmVTjcpEg3ELyBGPx2ipnSnBAoGBAIX6J2Lmc8JPTh9U6BZs
K1buQBvOWeX87eUdNECSc9L9FFYLCutn57s4sqswhakIJsymNvaZpb4s0efYfNss
LyO+hc+q0iX3ecCQLUL1Laxj1bEohVvS31uuzQH9yCBwllJBx8EyufK/lDhu72md
5U+yFG+enNOhmdpu5YFn2jVo
-----END PRIVATE KEY-----
'''
        # write file somewhere
        import tempfile
        infile = tempfile.mktemp('.publishsettings')
        with open(infile, 'w') as f:
            f.write(file_text)

        # Test Default (picks first subscription)
        outfile = tempfile.mktemp('.pem')
        id = get_certificate_from_publish_settings(infile, outfile)
        sms = ServiceManagementService(id, outfile)
        self.assertEqual(open(outfile).read(), expected_1)

        # Test Select First Subscription
        outfile = tempfile.mktemp('.pem')
        id = get_certificate_from_publish_settings(infile, outfile, 'cafecafe-cafe-1234-1234-1234cafe0001')
        sms = ServiceManagementService(id, outfile)
        self.assertEqual(open(outfile).read(), expected_1)

        # Test Select Last Subscription
        outfile = tempfile.mktemp('.pem')
        id = get_certificate_from_publish_settings(infile, outfile, 'cafecafe-cafe-1234-1234-1234cafe0003')
        sms = ServiceManagementService(id, outfile)
        self.assertEqual(open(outfile).read(), expected_3)

        # Test Invalid Subscription ID
        outfile = tempfile.mktemp('.pem')
        try:
            id = get_certificate_from_publish_settings(infile, outfile, 'DEADDEAD-DEAD-DEAD-DEAD-DEADDEADDEAD')
            self.assertFalse(true, "Subscription should not have been found")
        except ValueError as e:
            expected_msg = "The provided subscription_id '{}' was not found in the publish settings file provided at '{}'".format('DEADDEAD-DEAD-DEAD-DEAD-DEADDEADDEAD', infile)
            self.assertEqual(str(e), expected_msg)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
