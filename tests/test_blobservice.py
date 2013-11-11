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
import datetime
import httplib
import os
import time
import unittest

from azure import (WindowsAzureError,
                   BLOB_SERVICE_HOST_BASE,
                   )
from azure.http import (HTTPRequest,
                        HTTPResponse,
                        )
from azure.storage import (AccessPolicy,
                           BlobBlockList,
                           BlobResult,
                           Logging,
                           Metrics,
                           PageList,
                           PageRange,
                           SignedIdentifier,
                           SignedIdentifiers,
                           StorageServiceProperties,
                           )
from azure.storage.blobservice import BlobService
from azure.storage.storageclient import (AZURE_STORAGE_ACCESS_KEY,
                                         AZURE_STORAGE_ACCOUNT,
                                         EMULATED,
                                         DEV_ACCOUNT_NAME,
                                         DEV_ACCOUNT_KEY,
                                         )
from azure.storage.sharedaccesssignature import (Permission,
                                                 SharedAccessSignature,
                                                 SharedAccessPolicy,
                                                 WebResource,
                                                 RESOURCE_BLOB,
                                                 RESOURCE_CONTAINER,
                                                 SHARED_ACCESS_PERMISSION,
                                                 SIGNED_EXPIRY,
                                                 SIGNED_IDENTIFIER,
                                                 SIGNED_PERMISSION,
                                                 SIGNED_RESOURCE,
                                                 SIGNED_RESOURCE_TYPE,
                                                 SIGNED_SIGNATURE,
                                                 SIGNED_START,
                                                 )
from util import (AzureTestCase,
                  credentials,
                  getUniqueTestRunID,
                  getUniqueNameBasedOnCurrentTime,
                  )

#------------------------------------------------------------------------------
class BlobServiceTest(AzureTestCase):

    def setUp(self):
        self.bc = BlobService(credentials.getStorageServicesName(), 
                              credentials.getStorageServicesKey())

        self.bc.set_proxy(credentials.getProxyHost(),
                          credentials.getProxyPort(),
                          credentials.getProxyUser(), 
                          credentials.getProxyPassword())

        __uid = getUniqueTestRunID()

        container_base_name = u'mytestcontainer%s' % (__uid)

        self.container_name = getUniqueNameBasedOnCurrentTime(container_base_name)
        self.additional_container_names = []

    def tearDown(self):
        self.cleanup()
        return super(BlobServiceTest, self).tearDown()

    def cleanup(self):
        try:
            self.bc.delete_container(self.container_name)
        except: pass

        for name in self.additional_container_names:
            try:
                self.bc.delete_container(name)
            except: pass

    #--Helpers-----------------------------------------------------------------
    def _create_container(self, container_name):
        self.bc.create_container(container_name, None, None, True)

    def _create_container_and_block_blob(self, container_name, blob_name, blob_data):
        self._create_container(container_name)
        resp = self.bc.put_blob(container_name, blob_name, blob_data, 'BlockBlob')
        self.assertIsNone(resp)

    def _create_container_and_page_blob(self, container_name, blob_name, content_length):
        self._create_container(container_name)
        resp = self.bc.put_blob(self.container_name, blob_name, '', 'PageBlob', x_ms_blob_content_length=str(content_length))
        self.assertIsNone(resp)

    def _get_permission(self, sas, resource_type, resource_path, permission):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        expiry = start + datetime.timedelta(hours=1)
        
        sap = SharedAccessPolicy(AccessPolicy(start.strftime(date_format),
                                              expiry.strftime(date_format),
                                              permission))
        
        signed_query = sas.generate_signed_query_string(resource_path, 
                                                   resource_type, 
                                                   sap)
        
        return Permission('/' + resource_path, signed_query)

    def _get_signed_web_resource(self, sas, resource_type, resource_path, permission):
        web_rsrc = WebResource()
        web_rsrc.properties[SIGNED_RESOURCE_TYPE] = resource_type
        web_rsrc.properties[SHARED_ACCESS_PERMISSION] = permission
        web_rsrc.path = '/' + resource_path
        web_rsrc.request_url = '/' + resource_path
        
        return sas.sign_request(web_rsrc)

    def _get_request(self, host, url):
        return self._web_request('GET', host, url, None)

    def _put_request(self, host, url, content):
        return self._web_request('PUT', host, url, content)

    def _del_request(self, host, url):
        return self._web_request('DELETE', host, url, None)

    def _web_request(self, method, host, url, content):
        connection = httplib.HTTPConnection(host)
        connection.putrequest(method, url)
        connection.putheader('Content-Type', 'application/octet-stream;Charset=UTF-8')
        if content is not None:
            connection.putheader('Content-Length', str(len(content)))  
        connection.endheaders()
        if content is not None:
            connection.send(content)

        resp = connection.getresponse()
        resp.getheaders()
        respbody = None
        if resp.length is None:
            respbody = resp.read()
        elif resp.length > 0:
            respbody = resp.read(resp.length)

        return respbody

    #--Test cases for blob service --------------------------------------------
    def test_create_blob_service_missing_arguments(self):
        # Arrange
        if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
            del os.environ[AZURE_STORAGE_ACCESS_KEY]
        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]

        # Act
        with self.assertRaises(WindowsAzureError):
            bs = BlobService()

        # Assert

    def test_create_blob_service_env_variables(self):
        # Arrange
        os.environ[AZURE_STORAGE_ACCOUNT] = credentials.getStorageServicesName()
        os.environ[AZURE_STORAGE_ACCESS_KEY] = credentials.getStorageServicesKey()

        # Act
        bs = BlobService()

        if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEquals(bs.account_name, credentials.getStorageServicesName())
        self.assertEquals(bs.account_key, credentials.getStorageServicesKey())
        self.assertEquals(bs.is_emulated, False)

    def test_create_blob_service_emulated_true(self):
        # Arrange
        os.environ[EMULATED] = 'true'

        # Act
        bs = BlobService()

        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEquals(bs.account_name, DEV_ACCOUNT_NAME)
        self.assertEquals(bs.account_key, DEV_ACCOUNT_KEY)
        self.assertEquals(bs.is_emulated, True)

    def test_create_blob_service_emulated_false(self):
        # Arrange
        os.environ[EMULATED] = 'false'

        # Act
        with self.assertRaises(WindowsAzureError):
            bs = BlobService()

        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]

        # Assert

    def test_create_blob_service_emulated_false_env_variables(self):
        # Arrange
        os.environ[EMULATED] = 'false'
        os.environ[AZURE_STORAGE_ACCOUNT] = credentials.getStorageServicesName()
        os.environ[AZURE_STORAGE_ACCESS_KEY] = credentials.getStorageServicesKey()

        # Act
        bs = BlobService()

        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]
        if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEquals(bs.account_name, credentials.getStorageServicesName())
        self.assertEquals(bs.account_key, credentials.getStorageServicesKey())
        self.assertEquals(bs.is_emulated, False)

    #--Test cases for containers -----------------------------------------
    def test_create_container_no_options(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name)

        # Assert
        self.assertTrue(created)

    def test_create_container_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, None, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_container_with_already_existing_container(self):
        # Arrange

        # Act
        created1 = self.bc.create_container(self.container_name)
        created2 = self.bc.create_container(self.container_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_container_with_already_existing_container_fail_on_exist(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name)
        with self.assertRaises(WindowsAzureError):
            self.bc.create_container(self.container_name, None, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_container_with_public_access_container(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, None, 'container')

        # Assert
        self.assertTrue(created)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_create_container_with_public_access_blob(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, None, 'blob')

        # Assert
        self.assertTrue(created)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_create_container_with_metadata(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, {'hello':'world', 'foo':'42'})

        # Assert
        self.assertTrue(created)
        md = self.bc.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_list_containers_no_options(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        containers = self.bc.list_containers()
        for container in containers:
            name = container.name

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, self.container_name)

    def test_list_containers_with_prefix(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        containers = self.bc.list_containers(self.container_name)

        # Assert
        self.assertIsNotNone(containers)
        self.assertEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertEqual(containers[0].name, self.container_name)
        self.assertIsNone(containers[0].metadata);

    def test_list_containers_with_include_metadata(self):
        # Arrange
        self.bc.create_container(self.container_name)
        resp = self.bc.set_container_metadata(self.container_name, {'hello':'world', 'bar':'43'})

        # Act
        containers = self.bc.list_containers(self.container_name, None, None, 'metadata')

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, self.container_name)
        self.assertEqual(containers[0].metadata['hello'], 'world')
        self.assertEqual(containers[0].metadata['bar'], '43')

    def test_list_containers_with_maxresults_and_marker(self):
        # Arrange
        self.additional_container_names = [self.container_name + 'a', 
                                           self.container_name + 'b', 
                                           self.container_name + 'c', 
                                           self.container_name + 'd']
        for name in self.additional_container_names:
            self.bc.create_container(name)

        # Act
        containers1 = self.bc.list_containers(self.container_name, None, 2)
        containers2 = self.bc.list_containers(self.container_name, containers1.next_marker, 2)

        # Assert
        self.assertIsNotNone(containers1)
        self.assertEqual(len(containers1), 2)
        self.assertNamedItemInContainer(containers1, self.container_name + 'a')
        self.assertNamedItemInContainer(containers1, self.container_name + 'b')
        self.assertIsNotNone(containers2)
        self.assertEqual(len(containers2), 2)
        self.assertNamedItemInContainer(containers2, self.container_name + 'c')
        self.assertNamedItemInContainer(containers2, self.container_name + 'd')

    def test_set_container_metadata(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_metadata(self.container_name, {'hello':'world', 'bar':'43'})

        # Assert
        self.assertIsNone(resp)
        md = self.bc.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-bar'], '43')

    def test_set_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_container_metadata(self.container_name, {'hello':'world', 'bar':'43'})

        # Assert

    def test_get_container_metadata(self):
        # Arrange
        self.bc.create_container(self.container_name)
        self.bc.set_container_acl(self.container_name, None, 'container')
        self.bc.set_container_metadata(self.container_name, {'hello':'world','foo':'42'})

        # Act
        md = self.bc.get_container_metadata(self.container_name)

        # Assert
        self.assertIsNotNone(md)
        self.assertEquals(2, len(md))
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_get_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_metadata(self.container_name)

        # Assert

    def test_get_container_properties(self):
        # Arrange
        self.bc.create_container(self.container_name)
        self.bc.set_container_acl(self.container_name, None, 'container')
        self.bc.set_container_metadata(self.container_name, {'hello':'world','foo':'42'})

        # Act
        props = self.bc.get_container_properties(self.container_name)

        # Assert
        self.assertIsNotNone(props)
        self.assertEquals(props['x-ms-meta-hello'], 'world')
        self.assertEquals(props['x-ms-meta-foo'], '42')
        # TODO:
        # get_container_properties returns container lease information whereas get_container_metadata doesn't
        # we should lease the container in the arrange section and verify that we receive that info

    def test_get_container_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_properties(self.container_name)

        # Assert

    def test_get_container_acl(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        acl = self.bc.get_container_acl(self.container_name)

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_get_container_acl_iter(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        acl = self.bc.get_container_acl(self.container_name)
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)
        self.assertEqual(len(acl), 0)

    def test_get_container_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_acl(self.container_name)

        # Assert

    def test_set_container_acl(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_acl(self.container_name)

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_public_access_container(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_acl(self.container_name, None, 'container')

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_public_access_blob(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_acl(self.container_name, None, 'blob')

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_empty_signed_identifiers(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        identifiers = SignedIdentifiers()

        resp = self.bc.set_container_acl(self.container_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_set_container_acl_with_signed_identifiers(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2011-10-12'
        si.access_policy.permission = 'r'
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.bc.set_container_acl(self.container_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 1)
        self.assertEqual(len(acl), 1)
        self.assertEqual(acl.signed_identifiers[0].id, 'testid')
        self.assertEqual(acl[0].id, 'testid')

    def test_set_container_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_container_acl(self.container_name, None, 'container')

        # Assert

    def test_delete_container_with_existing_container(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        deleted = self.bc.delete_container(self.container_name)

        # Assert
        self.assertTrue(deleted)
        containers = self.bc.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_with_existing_container_fail_not_exist(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        deleted = self.bc.delete_container(self.container_name, True)

        # Assert
        self.assertTrue(deleted)
        containers = self.bc.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_with_non_existing_container(self):
        # Arrange

        # Act
        deleted = self.bc.delete_container(self.container_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_container_with_non_existing_container_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.delete_container(self.container_name, True)

        # Assert

    #--Test cases for blob service ---------------------------------------
    def test_set_blob_service_properties(self):
        # Arrange

        # Act
        props = StorageServiceProperties()
        props.metrics.enabled = False
        resp = self.bc.set_blob_service_properties(props)

        # Assert
        self.assertIsNone(resp)
        received_props = self.bc.get_blob_service_properties()
        self.assertFalse(received_props.metrics.enabled)

    def test_set_blob_service_properties_with_timeout(self):
        # Arrange

        # Act
        props = StorageServiceProperties()
        props.logging.write = True
        resp = self.bc.set_blob_service_properties(props, 5)

        # Assert
        self.assertIsNone(resp)
        received_props = self.bc.get_blob_service_properties()
        self.assertTrue(received_props.logging.write)

    def test_get_blob_service_properties(self):
        # Arrange

        # Act
        props = self.bc.get_blob_service_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsInstance(props.logging, Logging)
        self.assertIsInstance(props.metrics, Metrics)

    def test_get_blob_service_properties_with_timeout(self):
        # Arrange

        # Act
        props = self.bc.get_blob_service_properties(5)

        # Assert
        self.assertIsNotNone(props)
        self.assertIsInstance(props.logging, Logging)
        self.assertIsInstance(props.metrics, Metrics)

    #--Test cases for blobs ----------------------------------------------
    def test_list_blobs(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob')

        # Act
        resp = self.bc.list_blobs(self.container_name)
        for blob in resp:
            name = blob.name

        # Assert
        self.assertIsNotNone(resp)
        self.assertGreaterEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'blob1')
        self.assertNamedItemInContainer(resp, 'blob2')
        self.assertEqual(resp[0].properties.content_length, 11)
        self.assertEqual(resp[1].properties.content_type, 'application/octet-stream Charset=UTF-8')

    def test_list_blobs_with_prefix(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        resp = self.bc.list_blobs(self.container_name, 'bloba')

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertEqual(len(resp.blobs), 2)
        self.assertEqual(len(resp.prefixes), 0)
        self.assertEqual(resp.prefix, 'bloba')
        self.assertNamedItemInContainer(resp, 'bloba1')
        self.assertNamedItemInContainer(resp, 'bloba2')

    def test_list_blobs_with_prefix_and_delimiter(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'documents/music/pop/thriller.mp3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/music/rock/stairwaytoheaven.mp3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/music/rock/hurt.mp3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/music/rock/metallica/one.mp3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/music/unsorted1.mp3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/music/unsorted2.mp3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/pictures/birthday/kid.jpg', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'documents/pictures/birthday/cake.jpg', data, 'BlockBlob')

        # Act
        resp = self.bc.list_blobs(self.container_name, 'documents/music/', delimiter='/')

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertEqual(len(resp.blobs), 2)
        self.assertEqual(len(resp.prefixes), 2)
        self.assertEqual(resp.prefix, 'documents/music/')
        self.assertEqual(resp.delimiter, '/')
        self.assertNamedItemInContainer(resp, 'documents/music/unsorted1.mp3')
        self.assertNamedItemInContainer(resp, 'documents/music/unsorted2.mp3')
        self.assertNamedItemInContainer(resp.blobs, 'documents/music/unsorted1.mp3')
        self.assertNamedItemInContainer(resp.blobs, 'documents/music/unsorted2.mp3')
        self.assertNamedItemInContainer(resp.prefixes, 'documents/music/pop/')
        self.assertNamedItemInContainer(resp.prefixes, 'documents/music/rock/')

    def test_list_blobs_with_maxresults(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs = self.bc.list_blobs(self.container_name, None, None, 2)

        # Assert
        self.assertIsNotNone(blobs)
        self.assertEqual(len(blobs), 2)
        self.assertNamedItemInContainer(blobs, 'bloba1')
        self.assertNamedItemInContainer(blobs, 'bloba2')

    def test_list_blobs_with_maxresults_and_marker(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs1 = self.bc.list_blobs(self.container_name, None, None, 2)
        blobs2 = self.bc.list_blobs(self.container_name, None, blobs1.next_marker, 2)

        # Assert
        self.assertEqual(len(blobs1), 2)
        self.assertEqual(len(blobs2), 2)
        self.assertNamedItemInContainer(blobs1, 'bloba1')
        self.assertNamedItemInContainer(blobs1, 'bloba2')
        self.assertNamedItemInContainer(blobs2, 'bloba3')
        self.assertNamedItemInContainer(blobs2, 'blobb1')

    def test_list_blobs_with_include_snapshots(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob')
        self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='snapshots')

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertNotEqual(blobs[0].snapshot, '')
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertEqual(blobs[1].snapshot, '')
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertEqual(blobs[2].snapshot, '')

    def test_list_blobs_with_include_metadata(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'foo':'1','bar':'bob'})
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob', x_ms_meta_name_values={'foo':'2','bar':'car'})
        self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='metadata')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[0].metadata['foo'], '1')
        self.assertEqual(blobs[0].metadata['bar'], 'bob')
        self.assertEqual(blobs[1].name, 'blob2')
        self.assertEqual(blobs[1].metadata['foo'], '2')
        self.assertEqual(blobs[1].metadata['bar'], 'car')

    def test_list_blobs_with_include_uncommittedblobs(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob', x_ms_meta_name_values={'foo':'2','bar':'car'})

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='uncommittedblobs')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob2')

    #def test_list_blobs_with_include_copy(self):
    #    # Arrange
    #    self._create_container(self.container_name)
    #    data = 'hello world'
    #    self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'status':'original'})
    #    sourceblob = '/%s/%s/%s' % (credentials.getStorageServicesName(),
    #                                self.container_name,
    #                                'blob1')
    #    self.bc.copy_blob(self.container_name, 'blob1copy', sourceblob, {'status':'copy'})

    #    # Act
    #    blobs = self.bc.list_blobs(self.container_name, include='copy')

    #    # Assert
    #    self.assertEqual(len(blobs), 2)
    #    self.assertEqual(blobs[0].name, 'blob1')
    #    self.assertEqual(blobs[1].name, 'blob2')
    #    #TODO: check for metadata related to copy blob

    def test_list_blobs_with_include_multiple(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'foo':'1','bar':'bob'})
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob', x_ms_meta_name_values={'foo':'2','bar':'car'})
        self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='snapshots,metadata')

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertNotEqual(blobs[0].snapshot, '')
        self.assertEqual(blobs[0].metadata['foo'], '1')
        self.assertEqual(blobs[0].metadata['bar'], 'bob')
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertEqual(blobs[1].snapshot, '')
        self.assertEqual(blobs[1].metadata['foo'], '1')
        self.assertEqual(blobs[1].metadata['bar'], 'bob')
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertEqual(blobs[2].snapshot, '')
        self.assertEqual(blobs[2].metadata['foo'], '2')
        self.assertEqual(blobs[2].metadata['bar'], 'car')

    def test_put_blob_block_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = 'hello world'
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')

        # Assert
        self.assertIsNone(resp)

    def test_put_blob_page_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        resp = self.bc.put_blob(self.container_name, 'blob1', '', 'PageBlob', x_ms_blob_content_length='1024')

        # Assert
        self.assertIsNone(resp)

    def test_put_blob_with_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        lease = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        lease_id = lease['x-ms-lease-id']

        # Act
        data = 'hello world again'
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_lease_id=lease_id)

        # Assert
        self.assertIsNone(resp)
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_lease_id=lease_id)
        self.assertEqual(blob, 'hello world again')

    def test_put_blob_with_metadata(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = 'hello world'
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'hello':'world','foo':'42'})

        # Assert
        self.assertIsNone(resp)
        md = self.bc.get_blob_metadata(self.container_name, 'blob1')
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_get_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_with_snapshot(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        snapshot = self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', snapshot['x-ms-snapshot'])

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_with_snapshot_previous(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        snapshot = self.bc.snapshot_blob(self.container_name, 'blob1')
        self.bc.put_blob(self.container_name, 'blob1', 'hello world again', 'BlockBlob')

        # Act
        blob_previous = self.bc.get_blob(self.container_name, 'blob1', snapshot['x-ms-snapshot'])
        blob_latest = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob_previous, BlobResult)
        self.assertIsInstance(blob_latest, BlobResult)
        self.assertEquals(blob_previous, 'hello world')
        self.assertEquals(blob_latest, 'hello world again')

    def test_get_blob_with_range(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_range='bytes=0-5')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello ')

    def test_get_blob_with_range_and_get_content_md5(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_range='bytes=0-5', x_ms_range_get_content_md5='true')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello ')
        self.assertEquals(blob.properties['content-md5'], '+BSJN3e8wilf/wXwDlCNpg==')

    def test_get_blob_with_lease(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        lease = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        lease_id = lease['x-ms-lease-id']

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_lease_id=lease_id)
        self.bc.lease_blob(self.container_name, 'blob1', 'release', lease_id)

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_on_leased_blob_without_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        self.bc.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1') # get_blob is allowed without lease id

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob(self.container_name, 'blob1')

        # Assert

    def test_get_blob_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob(self.container_name, 'blob1')

        # Assert

    def test_set_blob_properties_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.set_blob_properties(self.container_name, 'blob1', x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        props = self.bc.get_blob_properties(self.container_name, 'blob1')
        self.assertEquals(props['content-language'], 'spanish')

    def test_set_blob_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_blob_properties(self.container_name, 'blob1', x_ms_blob_content_language='spanish')

        # Assert

    def test_set_blob_properties_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_blob_properties(self.container_name, 'blob1', x_ms_blob_content_language='spanish')

        # Assert

    def test_get_blob_properties_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        props = self.bc.get_blob_properties(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(props)
        self.assertEquals(props['x-ms-blob-type'], 'BlockBlob')
        self.assertEquals(props['x-ms-lease-status'], 'unlocked')
        self.assertEquals(props['content-length'], '11')

    def test_get_blob_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob_properties(self.container_name, 'blob1')

        # Assert

    def test_get_blob_properties_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob_properties(self.container_name, 'blob1')

        # Assert

    def test_get_blob_metadata_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        md = self.bc.get_blob_metadata(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(md)

    def test_set_blob_metadata_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.set_blob_metadata(self.container_name, 'blob1', {'hello':'world', 'foo':'42'})

        # Assert
        self.assertIsNone(resp)
        md = self.bc.get_blob_metadata(self.container_name, 'blob1')
        self.assertEquals(2, len(md))
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_delete_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.delete_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsNone(resp)

    def test_delete_blob_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.delete_blob(self.container_name, 'blob1')

        # Assert

    def test_copy_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        sourceblob = '/%s/%s/%s' % (credentials.getStorageServicesName(),
                                    self.container_name,
                                    'blob1')
        resp = self.bc.copy_blob(self.container_name, 'blob1copy', sourceblob)

        # Assert
        self.assertIsNone(resp)
        copy = self.bc.get_blob(self.container_name, 'blob1copy')
        self.assertEquals(copy, 'hello world')

    def test_snapshot_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.snapshot_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['x-ms-snapshot'])

    def test_lease_blob_acquire_and_release(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp1 = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bc.lease_blob(self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_lease_blob_acquire_twice_fails(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        resp1 = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bc.lease_blob(self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_put_block(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')

        # Act
        for i in xrange(5):
            resp = self.bc.put_block(self.container_name, 
                                     'blob1',
                                     'block %d' % (i),
                                     str(i))
            self.assertIsNone(resp)

        # Assert

    def test_put_block_list(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')

        # Act
        resp = self.bc.put_block_list(self.container_name, 'blob1', ['1', '2', '3'])

        # Assert
        self.assertIsNone(resp)
        blob = self.bc.get_blob(self.container_name, 'blob1')
        self.assertEqual(blob, 'AAABBBCCC')

    def test_get_block_list_no_blocks(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')

        # Act
        block_list = self.bc.get_block_list(self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEquals(len(block_list.uncommitted_blocks), 0)
        self.assertEquals(len(block_list.committed_blocks), 0)

    def test_get_block_list_uncommitted_blocks(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')

        # Act
        block_list = self.bc.get_block_list(self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEquals(len(block_list.uncommitted_blocks), 3)
        self.assertEquals(len(block_list.committed_blocks), 0)

    def test_get_block_list_committed_blocks(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')
        self.bc.put_block_list(self.container_name, 'blob1', ['1', '2', '3'])

        # Act
        block_list = self.bc.get_block_list(self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEquals(len(block_list.uncommitted_blocks), 0)
        self.assertEquals(len(block_list.committed_blocks), 3)

    def test_put_page_update(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 1024)

        # Act
        data = 'abcdefghijklmnop' * 32
        resp = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=0-511', 'update')

        # Assert
        self.assertIsNone(resp)

    def test_put_page_clear(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 1024)

        # Act
        resp = self.bc.put_page(self.container_name, 'blob1', '', 'bytes=0-511', 'clear')

        # Assert
        self.assertIsNone(resp)

    def test_get_page_ranges_no_pages(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 1024)

        # Act
        ranges = self.bc.get_page_ranges(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, PageList)
        self.assertEquals(len(ranges.page_ranges), 0)

    def test_get_page_ranges_2_pages(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 2048)
        data = 'abcdefghijklmnop' * 32
        resp1 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=0-511', 'update')
        resp2 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=1024-1535', 'update')

        # Act
        ranges = self.bc.get_page_ranges(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, PageList)
        self.assertEquals(len(ranges.page_ranges), 2)
        self.assertEquals(ranges.page_ranges[0].start, 0)
        self.assertEquals(ranges.page_ranges[0].end, 511)
        self.assertEquals(ranges.page_ranges[1].start, 1024)
        self.assertEquals(ranges.page_ranges[1].end, 1535)

    def test_get_page_ranges_iter(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 2048)
        data = 'abcdefghijklmnop' * 32
        resp1 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=0-511', 'update')
        resp2 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=1024-1535', 'update')

        # Act
        ranges = self.bc.get_page_ranges(self.container_name, 'blob1')
        for range in ranges:
            pass

        # Assert
        self.assertEquals(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    def test_with_filter(self):
        # Single filter
        called = []
        def my_filter(request, next):
            called.append(True)
            self.assertIsInstance(request, HTTPRequest)
            for header in request.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, (str, unicode, type(None)))
            self.assertIsInstance(request.host, (str, unicode))
            self.assertIsInstance(request.method, (str, unicode))
            self.assertIsInstance(request.path, (str, unicode))
            self.assertIsInstance(request.query, list)
            self.assertIsInstance(request.body, (str, unicode))
            response = next(request)
                
            self.assertIsInstance(response, HTTPResponse)
            self.assertIsInstance(response.body, (str, type(None)))
            self.assertIsInstance(response.headers, list)
            for header in response.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, (str, unicode))
            self.assertIsInstance(response.status, int)
            return response

        bc = self.bc.with_filter(my_filter)
        bc.create_container(self.container_name + '0', None, None, False)

        self.assertTrue(called)

        del called[:]
        
        bc.delete_container(self.container_name + '0')

        self.assertTrue(called)
        del called[:]

        # Chained filters
        def filter_a(request, next):
            called.append('a')
            return next(request)
        
        def filter_b(request, next):
            called.append('b')
            return next(request)

        bc = self.bc.with_filter(filter_a).with_filter(filter_b)
        bc.create_container(self.container_name + '1', None, None, False)

        self.assertEqual(called, ['b', 'a'])
        
        bc.delete_container(self.container_name + '1')

        self.assertEqual(called, ['b', 'a', 'b', 'a'])

    def test_unicode_create_container_unicode_name(self):
        # Arrange
        self.container_name = unicode(self.container_name) + u'啊齄丂狛狜'

        # Act
        with self.assertRaises(WindowsAzureError):
            # not supported - container name must be alphanumeric, lowercase
            self.bc.create_container(self.container_name)

        # Assert

    def test_unicode_get_blob_unicode_name(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, '啊齄丂狛狜', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, '啊齄丂狛狜')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_unicode_get_blob_unicode_data(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', u'hello world啊齄丂狛狜')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world啊齄丂狛狜')

    def test_unicode_get_blob_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        self._create_container_and_block_blob(self.container_name, 'blob1', binary_data)

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, binary_data)

    def test_no_sas_private_blob(self):
        # Arrange
        data = 'a private blob cannot be read without a shared access signature'
        self._create_container_and_block_blob(self.container_name, 'blob1.txt', data)
        res_path = self.container_name + '/blob1.txt'

        # Act
        host = credentials.getStorageServicesName() + BLOB_SERVICE_HOST_BASE
        url = '/' + res_path
        respbody = self._get_request(host, url)

        # Assert
        self.assertNotEquals(data, respbody)
        self.assertNotEquals(-1, respbody.find('ResourceNotFound'))

    def test_no_sas_public_blob(self):
        # Arrange
        data = 'a public blob can be read without a shared access signature'
        self.bc.create_container(self.container_name, None, 'blob')
        self.bc.put_blob(self.container_name, 'blob1.txt', data, 'BlockBlob')
        res_path = self.container_name + '/blob1.txt'

        # Act
        host = credentials.getStorageServicesName() + BLOB_SERVICE_HOST_BASE
        url = '/' + res_path
        respbody = self._get_request(host, url)

        # Assert
        self.assertEquals(data, respbody)

    def test_shared_read_access_blob(self):
        # Arrange
        data = 'shared access signature with read permission on blob'
        self._create_container_and_block_blob(self.container_name, 'blob1.txt', data)
        sas = SharedAccessSignature(credentials.getStorageServicesName(), 
                                    credentials.getStorageServicesKey())
        res_path = self.container_name + '/blob1.txt'
        res_type = RESOURCE_BLOB

        # Act
        sas.permission_set = [self._get_permission(sas, res_type, res_path, 'r')]
        web_rsrc = self._get_signed_web_resource(sas, res_type, res_path, 'r')
        host = credentials.getStorageServicesName() + BLOB_SERVICE_HOST_BASE
        url = web_rsrc.request_url
        respbody = self._get_request(host, url)

        # Assert
        self.assertEquals(data, respbody)

    def test_shared_write_access_blob(self):
        # Arrange
        data = 'shared access signature with write permission on blob'
        updated_data = 'updated blob data'
        self._create_container_and_block_blob(self.container_name, 'blob1.txt', data)
        sas = SharedAccessSignature(credentials.getStorageServicesName(), 
                                    credentials.getStorageServicesKey())
        res_path = self.container_name + '/blob1.txt'
        res_type = RESOURCE_BLOB

        # Act
        sas.permission_set = [self._get_permission(sas, res_type, res_path, 'w')]
        web_rsrc = self._get_signed_web_resource(sas, res_type, res_path, 'w')
        host = credentials.getStorageServicesName() + BLOB_SERVICE_HOST_BASE
        url = web_rsrc.request_url
        respbody = self._put_request(host, url, updated_data)

        # Assert
        blob = self.bc.get_blob(self.container_name, 'blob1.txt')
        self.assertEquals(updated_data, blob)

    def test_shared_delete_access_blob(self):
        # Arrange
        data = 'shared access signature with delete permission on blob'
        self._create_container_and_block_blob(self.container_name, 'blob1.txt', data)
        sas = SharedAccessSignature(credentials.getStorageServicesName(), 
                                    credentials.getStorageServicesKey())
        res_path = self.container_name + '/blob1.txt'
        res_type = RESOURCE_BLOB

        # Act
        sas.permission_set = [self._get_permission(sas, res_type, res_path, 'd')]
        web_rsrc = self._get_signed_web_resource(sas, res_type, res_path, 'd')
        host = credentials.getStorageServicesName() + BLOB_SERVICE_HOST_BASE
        url = web_rsrc.request_url
        respbody = self._del_request(host, url)

        # Assert
        with self.assertRaises(WindowsAzureError):
            blob = self.bc.get_blob(self.container_name, 'blob1.txt')

    def test_shared_access_container(self):
        # Arrange
        data = 'shared access signature with read permission on container'
        self._create_container_and_block_blob(self.container_name, 'blob1.txt', data)
        sas = SharedAccessSignature(credentials.getStorageServicesName(), 
                                    credentials.getStorageServicesKey())
        res_path = self.container_name
        res_type = RESOURCE_CONTAINER

        # Act
        sas.permission_set = [self._get_permission(sas, res_type, res_path, 'r')]
        web_rsrc = self._get_signed_web_resource(sas, res_type, res_path + '/blob1.txt', 'r')
        host = credentials.getStorageServicesName() + BLOB_SERVICE_HOST_BASE
        url = web_rsrc.request_url
        respbody = self._get_request(host, url)

        # Assert
        self.assertEquals(data, respbody)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
