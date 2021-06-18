# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from datetime import datetime, timedelta
from time import sleep

import pytest
import requests

from _shared.testcase import StorageTestCase, LogCaptured, GlobalStorageAccountPreparer, GlobalResourceGroupPreparer, StorageAccountPreparer
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceExistsError, ResourceModifiedError
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    PublicAccess,
    ContainerSasPermissions,
    AccessPolicy,
    StandardBlobTier,
    PremiumPageBlobTier,
    generate_container_sas,
    PartialBatchErrorException,
    generate_account_sas, ResourceTypes, AccountSasPermissions, ContainerClient, ContentSettings)

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
#------------------------------------------------------------------------------


class StorageContainerTest(StorageTestCase):

    #--Helpers-----------------------------------------------------------------
    def _get_container_reference(self, prefix=TEST_CONTAINER_PREFIX):
        container_name = self.get_resource_name(prefix)
        return container_name

    def _create_container(self, bsc, prefix=TEST_CONTAINER_PREFIX):
        container_name = self._get_container_reference(prefix)
        container = bsc.get_container_client(container_name)
        try:
            container.create_container()
        except ResourceExistsError:
            pass
        return container

    #--Test cases for containers -----------------------------------------
    @GlobalStorageAccountPreparer()
    def test_create_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = container.create_container()

        # Assert
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    def test_create_container_with_already_existing_container_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = container.create_container()
        with self.assertRaises(HttpResponseError):
            container.create_container()

        # Assert
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    def test_create_container_with_public_access_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = container.create_container(public_access='container')

        # Assert
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    def test_create_container_with_public_access_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = container.create_container(public_access='blob')

        blob = container.get_blob_client("blob1")
        blob.upload_blob(u'xyz')

        anonymous_service = BlobClient(
            self.account_url(storage_account, "blob"),
            container_name=container_name,
            blob_name="blob1")

        # Assert
        self.assertTrue(created)
        anonymous_service.download_blob()

    @GlobalStorageAccountPreparer()
    def test_create_container_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        container = bsc.get_container_client(container_name)
        created = container.create_container(metadata)

        # Assert
        self.assertTrue(created)
        md = container.get_container_properties().metadata
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    def test_container_exists_with_lease(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        container.acquire_lease()

        # Act
        exists = container.get_container_properties()

        # Assert
        self.assertTrue(exists)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_rename_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        old_name1 = self._get_container_reference(prefix="oldcontainer1")
        old_name2 = self._get_container_reference(prefix="oldcontainer2")
        new_name = self._get_container_reference(prefix="newcontainer")
        container1 = bsc.get_container_client(old_name1)
        container2 = bsc.get_container_client(old_name2)

        container1.create_container()
        container2.create_container()

        new_container = bsc._rename_container(name=old_name1, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            bsc._rename_container(name=old_name2, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            container1.get_container_properties()
        with self.assertRaises(HttpResponseError):
            bsc._rename_container(name="badcontainer", new_name="container")
        self.assertEqual(new_name, new_container.get_container_properties().name)

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @GlobalStorageAccountPreparer()
    def test_rename_container_with_container_client(
            self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        old_name1 = self._get_container_reference(prefix="oldcontainer1")
        old_name2 = self._get_container_reference(prefix="oldcontainer2")
        new_name = self._get_container_reference(prefix="newcontainer")
        bad_name = self._get_container_reference(prefix="badcontainer")
        container1 = bsc.get_container_client(old_name1)
        container2 = bsc.get_container_client(old_name2)
        bad_container = bsc.get_container_client(bad_name)

        container1.create_container()
        container2.create_container()

        new_container = container1._rename_container(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            container2._rename_container(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            container1.get_container_properties()
        with self.assertRaises(HttpResponseError):
            bad_container._rename_container(name="badcontainer", new_name="container")
        self.assertEqual(new_name, new_container.get_container_properties().name)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_rename_container_with_source_lease(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        old_name = self._get_container_reference(prefix="old")
        new_name = self._get_container_reference(prefix="new")
        container = bsc.get_container_client(old_name)
        container.create_container()
        container_lease_id = container.acquire_lease()
        with self.assertRaises(HttpResponseError):
            bsc._rename_container(name=old_name, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            bsc._rename_container(name=old_name, new_name=new_name, lease="bad_id")
        new_container = bsc._rename_container(name=old_name, new_name=new_name, lease=container_lease_id)
        self.assertEqual(new_name, new_container.get_container_properties().name)

    @GlobalStorageAccountPreparer()
    def test_unicode_create_container_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = u'啊齄丂狛狜'

        container = bsc.get_container_client(container_name)
        # Act
        with self.assertRaises(HttpResponseError):
            # not supported - container name must be alphanumeric, lowercase
            container.create_container()

    @GlobalStorageAccountPreparer()
    def test_list_containers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        containers = list(bsc.list_containers())

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, container.container_name)
        self.assertIsNotNone(containers[0].has_immutability_policy)
        self.assertIsNotNone(containers[0].has_legal_hold)

    @GlobalStorageAccountPreparer()
    def test_list_containers_with_prefix(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        containers = list(bsc.list_containers(name_starts_with=container.container_name))

        # Assert
        self.assertIsNotNone(containers)
        self.assertEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertEqual(containers[0].name, container.container_name)
        self.assertIsNone(containers[0].metadata)

    @GlobalStorageAccountPreparer()
    def test_list_containers_with_include_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        metadata = {'hello': 'world', 'number': '42'}
        resp = container.set_container_metadata(metadata)

        # Act
        containers = list(bsc.list_containers(
            name_starts_with=container.container_name,
            include_metadata=True))

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, container.container_name)
        self.assertDictEqual(containers[0].metadata, metadata)

    @GlobalStorageAccountPreparer()
    def test_list_containers_with_public_access(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifiers = {'testid': access_policy}
        resp = container.set_container_access_policy(signed_identifiers, public_access=PublicAccess.Blob)

        # Act
        containers = list(bsc.list_containers(name_starts_with=container.container_name))

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, container.container_name)
        self.assertEqual(containers[0].public_access, PublicAccess.Blob)

    @GlobalStorageAccountPreparer()
    def test_list_containers_with_num_results_and_marker(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        prefix = 'listcontainersync'
        container_names = []
        for i in range(0, 4):
            container_names.append(self._create_container(bsc, prefix + str(i)).container_name)

        container_names.sort()

        # Act
        generator1 = bsc.list_containers(name_starts_with=prefix, results_per_page=2).by_page()
        containers1 = list(next(generator1))

        generator2 = bsc.list_containers(
            name_starts_with=prefix, results_per_page=2).by_page(generator1.continuation_token)
        containers2 = list(next(generator2))

        # Assert
        self.assertIsNotNone(containers1)
        self.assertEqual(len(containers1), 2)
        self.assertNamedItemInContainer(containers1, container_names[0])
        self.assertNamedItemInContainer(containers1, container_names[1])
        self.assertIsNotNone(containers2)
        self.assertEqual(len(containers2), 2)
        self.assertNamedItemInContainer(containers2, container_names[2])
        self.assertNamedItemInContainer(containers2, container_names[3])

    @GlobalStorageAccountPreparer()
    def test_set_container_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        metadata = {'hello': 'world', 'number': '43'}
        container = self._create_container(bsc)

        # Act
        container.set_container_metadata(metadata)
        metadata_from_response = container.get_container_properties().metadata
        # Assert
        self.assertDictEqual(metadata_from_response, metadata)

    @GlobalStorageAccountPreparer()
    def test_set_container_metadata_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        metadata = {'hello': 'world', 'number': '43'}
        container = self._create_container(bsc)
        lease_id = container.acquire_lease()

        # Act
        container.set_container_metadata(metadata, lease=lease_id)

        # Assert
        md = container.get_container_properties().metadata
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    def test_set_container_metadata_with_non_existing_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()
        container = bsc.get_container_client(container_name)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            container.set_container_metadata({'hello': 'world', 'number': '43'})

        # Assert

    @GlobalStorageAccountPreparer()
    def test_get_container_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        container = self._create_container(bsc)
        container.set_container_metadata(metadata)

        # Act
        md = container.get_container_properties().metadata

        # Assert
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    def test_get_container_metadata_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        container = self._create_container(bsc)
        container.set_container_metadata(metadata)
        lease_id = container.acquire_lease()

        # Act
        md = container.get_container_properties(lease=lease_id).metadata

        # Assert
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    def test_container_exists(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)

        container1 = self._create_container(bsc, prefix="container1")
        container2_name = self._get_container_reference(prefix="container2")
        container2 = bsc.get_container_client(container2_name)

        self.assertTrue(container1.exists())
        self.assertFalse(container2.exists())

    @GlobalStorageAccountPreparer()
    def test_get_container_properties(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        container = self._create_container(bsc)
        container.set_container_metadata(metadata)

        # Act
        props = container.get_container_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        # self.assertEqual(props.lease.duration, 'infinite')
        # self.assertEqual(props.lease.state, 'leased')
        # self.assertEqual(props.lease.status, 'locked')
        # self.assertEqual(props.public_access, 'container')
        self.assertIsNotNone(props.has_immutability_policy)
        self.assertIsNotNone(props.has_legal_hold)

    @GlobalStorageAccountPreparer()
    def test_get_container_properties_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        container = self._create_container(bsc)
        container.set_container_metadata(metadata)
        lease_id = container.acquire_lease()

        # Act
        props = container.get_container_properties(lease=lease_id)
        lease_id.break_lease()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        self.assertEqual(props.lease.duration, 'infinite')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.status, 'locked')

    @GlobalStorageAccountPreparer()
    def test_get_container_acl(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        acl = container.get_container_access_policy()

        # Assert
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))
        self.assertEqual(len(acl.get('signed_identifiers')), 0)

    @GlobalStorageAccountPreparer()
    def test_get_container_acl_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        lease_id = container.acquire_lease()

        # Act
        acl = container.get_container_access_policy(lease=lease_id)

        # Assert
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}
        response = container.set_container_access_policy(signed_identifier)

        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 1)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_one_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}

        response = container.set_container_access_policy(signed_identifier)

        # Assert
        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_one_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifiers = {'testid': access_policy}

        response = container.set_container_access_policy(signed_identifiers)

        # Assert
        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        lease_id = container.acquire_lease()

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifiers = {'testid': access_policy}

        container.set_container_access_policy(signed_identifiers, lease=lease_id)

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_public_access(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        container.set_container_access_policy(signed_identifiers=dict(), public_access='container')

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual('container', acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        container.set_container_access_policy(signed_identifiers=dict())

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 0)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_empty_access_policy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        identifier = {'empty': None}

        # Act
        container.set_container_access_policy(identifier)

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual('empty', acl.get('signed_identifiers')[0].id)
        self.assertIsNone(acl.get('signed_identifiers')[0].access_policy)

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=1))
        identifiers = {'testid': access_policy}
        container.set_container_access_policy(identifiers)

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual('testid', acl.get('signed_identifiers')[0].id)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_empty_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        identifiers = {i: None for i in range(2)}

        # Act
        container.set_container_access_policy(identifiers)

        # Assert
        acl = container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 2)
        self.assertEqual('0', acl.get('signed_identifiers')[0].id)
        self.assertIsNone(acl.get('signed_identifiers')[0].access_policy)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    def test_set_container_acl_with_three_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=1))
        identifiers = {i: access_policy for i in range(3)}

        # Act
        container.set_container_access_policy(identifiers)

        # Assert
        acl = container.get_container_access_policy()
        self.assertEqual(3, len(acl.get('signed_identifiers')))
        self.assertEqual('0', acl.get('signed_identifiers')[0].id)
        self.assertIsNotNone(acl.get('signed_identifiers')[0].access_policy)
        self.assertIsNone(acl.get('public_access'))


    @GlobalStorageAccountPreparer()
    def test_set_container_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._create_container(bsc)

        # Act
        identifiers = dict()
        for i in range(0, 6):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError) as e:
            container_name.set_container_access_policy(identifiers)
        self.assertEqual(
            str(e.exception),
            'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'
        )

    @GlobalStorageAccountPreparer()
    def test_lease_container_acquire_and_release(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        lease = container.acquire_lease()
        lease.release()

        # Assert

    @GlobalStorageAccountPreparer()
    def test_lease_container_renew(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        lease = container.acquire_lease(lease_duration=15)
        self.sleep(10)
        lease_id_start = lease.id

        # Act
        lease.renew()

        # Assert
        self.assertEqual(lease.id, lease_id_start)
        self.sleep(5)
        with self.assertRaises(HttpResponseError):
            container.delete_container()
        self.sleep(10)
        container.delete_container()

    @GlobalStorageAccountPreparer()
    def test_lease_container_break_period(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        lease = container.acquire_lease(lease_duration=15)

        # Assert
        lease.break_lease(lease_break_period=5)
        self.sleep(6)
        with self.assertRaises(HttpResponseError):
            container.delete_container(lease=lease)

    @GlobalStorageAccountPreparer()
    def test_lease_container_break_released_lease_fails(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        lease = container.acquire_lease()
        lease.release()

        # Act
        with self.assertRaises(HttpResponseError):
            lease.break_lease()

        # Assert

    @GlobalStorageAccountPreparer()
    def test_lease_container_with_duration(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        lease = container.acquire_lease(lease_duration=15)

        # Assert
        with self.assertRaises(HttpResponseError):
            container.acquire_lease()
        self.sleep(15)
        container.acquire_lease()

    @GlobalStorageAccountPreparer()
    def test_lease_container_twice(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        lease = container.acquire_lease(lease_duration=15)

        # Assert
        lease2 = container.acquire_lease(lease_id=lease.id)
        self.assertEqual(lease.id, lease2.id)

    @GlobalStorageAccountPreparer()
    def test_lease_container_with_proposed_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        proposed_lease_id = '55e97f64-73e8-4390-838d-d9e84a374321'
        lease = container.acquire_lease(lease_id=proposed_lease_id)

        # Assert
        self.assertEqual(proposed_lease_id, lease.id)

    @GlobalStorageAccountPreparer()
    def test_lease_container_change_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        lease_id = '29e0b239-ecda-4f69-bfa3-95f6af91464c'
        lease = container.acquire_lease()
        lease_id1 = lease.id
        lease.change(proposed_lease_id=lease_id)
        lease.renew()
        lease_id2 = lease.id

        # Assert
        self.assertIsNotNone(lease_id1)
        self.assertIsNotNone(lease_id2)
        self.assertNotEqual(lease_id1, lease_id)
        self.assertEqual(lease_id2, lease_id)

    @GlobalStorageAccountPreparer()
    def test_delete_container_with_existing_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)

        # Act
        deleted = container.delete_container()

        # Assert
        self.assertIsNone(deleted)

    @GlobalStorageAccountPreparer()
    def test_delete_container_with_non_existing_container_fail_not_exist(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()
        container = bsc.get_container_client(container_name)

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(ResourceNotFoundError):
                container.delete_container()

            log_as_str = log_captured.getvalue()
            #self.assertTrue('ERROR' in log_as_str)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_delete_container_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        lease = container.acquire_lease(lease_duration=15)

        # Act
        deleted = container.delete_container(lease=lease)

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            container.get_container_properties()

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_undelete_container(self, resource_group, location, storage_account, storage_account_key):
        # container soft delete should enabled by SRP call or use armclient, so make this test as playback only.

        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_client = self._create_container(bsc)

        # Act
        container_client.delete_container()
        # to make sure the container deleted
        with self.assertRaises(ResourceNotFoundError):
            container_client.get_container_properties()

        container_list = list(bsc.list_containers(include_deleted=True))
        self.assertTrue(len(container_list) >= 1)

        restored_version = 0
        for container in container_list:
            # find the deleted container and restore it
            if container.deleted and container.name == container_client.container_name:
                restored_ctn_client = bsc.undelete_container(container.name, container.version,
                                                              new_name="restored" + str(restored_version))
                restored_version += 1

                # to make sure the deleted container is restored
                props = restored_ctn_client.get_container_properties()
                self.assertIsNotNone(props)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_restore_to_existing_container(self, resource_group, location, storage_account, storage_account_key):
        # container soft delete should enabled by SRP call or use armclient, so make this test as playback only.

        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        # get an existing container
        existing_container_client = self._create_container(bsc, prefix="existing")
        container_client = self._create_container(bsc)

        # Act
        container_client.delete_container()
        # to make sure the container deleted
        with self.assertRaises(ResourceNotFoundError):
            container_client.get_container_properties()

        container_list = list(bsc.list_containers(include_deleted=True))
        self.assertTrue(len(container_list) >= 1)

        for container in container_list:
            # find the deleted container and restore it
            if container.deleted and container.name == container_client.container_name:
                with self.assertRaises(HttpResponseError):
                    bsc.undelete_container(container.name, container.version,
                                            new_name=existing_container_client.container_name)

    @pytest.mark.live_test_only  # sas token is dynamically generated
    @pytest.mark.playback_test_only  # we need container soft delete enabled account
    @GlobalStorageAccountPreparer()
    def test_restore_with_sas(self, resource_group, location, storage_account, storage_account_key):
        # container soft delete should enabled by SRP call or use armclient, so make this test as playback only.
        token = generate_account_sas(
            storage_account.name,
            storage_account_key,
            ResourceTypes(service=True, container=True),
            AccountSasPermissions(read=True, write=True, list=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), token)
        container_client = self._create_container(bsc)
        container_client.delete_container()
        # to make sure the container deleted
        with self.assertRaises(ResourceNotFoundError):
            container_client.get_container_properties()

        container_list = list(bsc.list_containers(include_deleted=True))
        self.assertTrue(len(container_list) >= 1)

        restored_version = 0
        for container in container_list:
            # find the deleted container and restore it
            if container.deleted and container.name == container_client.container_name:
                restored_ctn_client = bsc.undelete_container(container.name, container.version,
                                                              new_name="restored" + str(restored_version))
                restored_version += 1

                # to make sure the deleted container is restored
                props = restored_ctn_client.get_container_properties()
                self.assertIsNotNone(props)

    @GlobalStorageAccountPreparer()
    def test_list_names(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        container.get_blob_client('blob1').upload_blob(data)
        container.get_blob_client('blob2').upload_blob(data)


        # Act
        blobs = [b.name for b in container.list_blobs()]

        self.assertEqual(blobs, ['blob1', 'blob2'])

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_list_blobs_contains_last_access_time(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        blob_client = container.get_blob_client('blob1')
        blob_client.upload_blob(data, standard_blob_tier=StandardBlobTier.Archive)

        # Act
        for blob_properties in container.list_blobs():
            self.assertIsInstance(blob_properties.last_accessed_on, datetime)

    @GlobalStorageAccountPreparer()
    def test_list_blobs_returns_rehydrate_priority(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        blob_client = container.get_blob_client('blob1')
        blob_client.upload_blob(data, standard_blob_tier=StandardBlobTier.Archive)
        blob_client.set_standard_blob_tier(StandardBlobTier.Hot)

        # Act
        for blob_properties in container.list_blobs():
            if blob_properties.name == blob_client.blob_name:
                self.assertEqual(blob_properties.rehydrate_priority, "Standard")

    @GlobalStorageAccountPreparer()
    def test_list_blobs(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        container.get_blob_client('blob1').upload_blob(data)
        container.get_blob_client('blob2').upload_blob(data)

        # Act
        blobs = list(container.list_blobs())

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 2)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, 'blob1')
        self.assertNamedItemInContainer(blobs, 'blob2')
        self.assertEqual(blobs[0].size, 11)
        self.assertEqual(blobs[1].content_settings.content_type,
                         'application/octet-stream')
        self.assertIsNotNone(blobs[0].creation_time)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_object_replication_policy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        b_c = container.get_blob_client('blob1')
        b_c.upload_blob(data, overwrite=True)
        metadata = {'hello': 'world', 'number': '42'}
        b_c.set_blob_metadata(metadata)

        prop = b_c.get_blob_properties()

        container.get_blob_client('blob2').upload_blob(data, overwrite=True)

        # Act
        blobs_list = container.list_blobs()
        number_of_blobs_with_policy = 0
        for blob in blobs_list:
            if blob.object_replication_source_properties != None:
                number_of_blobs_with_policy += 1

        # Assert
        self.assertIsNot(number_of_blobs_with_policy, 0)

    @GlobalStorageAccountPreparer()
    def test_list_blobs_leased_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        blob1.upload_blob(data)
        lease = blob1.acquire_lease()

        # Act
        resp = list(container.list_blobs())

        # Assert
        self.assertIsNotNone(resp)
        self.assertGreaterEqual(len(resp), 1)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'blob1')
        self.assertEqual(resp[0].size, 11)
        self.assertEqual(resp[0].lease.duration, 'infinite')
        self.assertEqual(resp[0].lease.status, 'locked')
        self.assertEqual(resp[0].lease.state, 'leased')

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_prefix(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        container.get_blob_client('blob_a1').upload_blob(data)
        container.get_blob_client('blob_a2').upload_blob(data)
        container.get_blob_client('blob_b1').upload_blob(data)

        # Act
        resp = list(container.list_blobs(name_starts_with='blob_a'))

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertNamedItemInContainer(resp, 'blob_a1')
        self.assertNamedItemInContainer(resp, 'blob_a2')

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_num_results(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        container.get_blob_client('blob_a1').upload_blob(data)
        container.get_blob_client('blob_a2').upload_blob(data)
        container.get_blob_client('blob_a3').upload_blob(data)
        container.get_blob_client('blob_b1').upload_blob(data)


        # Act
        blobs = list(next(container.list_blobs(results_per_page=2).by_page()))

        # Assert
        self.assertIsNotNone(blobs)
        self.assertEqual(len(blobs), 2)
        self.assertNamedItemInContainer(blobs, 'blob_a1')
        self.assertNamedItemInContainer(blobs, 'blob_a2')

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_include_snapshots(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        blob1.upload_blob(data)
        blob1.create_snapshot()
        container.get_blob_client('blob2').upload_blob(data)

        # Act
        blobs = list(container.list_blobs(include="snapshots"))

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertIsNotNone(blobs[0].snapshot)
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertIsNone(blobs[1].snapshot)
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertIsNone(blobs[2].snapshot)

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_include_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        # pytest.skip("Waiting on metadata XML fix in msrest")
        container = self._create_container(bsc)
        data = b'hello world'
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob1 = container.get_blob_client('blob1')
        blob1.upload_blob(data, overwrite=True, content_settings=content_settings, metadata={'number': '1', 'name': 'bob'})
        blob1.create_snapshot()

        container.get_blob_client('blob2').upload_blob(data, overwrite=True, content_settings=content_settings, metadata={'number': '2', 'name': 'car'})

        # Act
        blobs =list(container.list_blobs(include="metadata"))

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[0].metadata['number'], '1')
        self.assertEqual(blobs[0].metadata['name'], 'bob')
        self.assertEqual(blobs[1].name, 'blob2')
        self.assertEqual(blobs[1].metadata['number'], '2')
        self.assertEqual(blobs[1].metadata['name'], 'car')
        self.assertEqual(blobs[1].content_settings.content_language, 'spanish')
        self.assertEqual(blobs[1].content_settings.content_disposition, 'inline')

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_include_uncommittedblobs(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        blob1.stage_block('1', b'AAA')
        blob1.stage_block('2', b'BBB')
        blob1.stage_block('3', b'CCC')

        blob2 = container.get_blob_client('blob2')
        blob2.upload_blob(data, metadata={'number': '2', 'name': 'car'})

        # Act
        blobs = list(container.list_blobs(include="uncommittedblobs"))

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob2')

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_include_copy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        container.get_blob_client('blob1').upload_blob(data, metadata={'status': 'original'})
        sourceblob = 'https://{0}.blob.core.windows.net/{1}/blob1'.format(
            storage_account.name,
            container.container_name)

        blobcopy = container.get_blob_client('blob1copy')
        blobcopy.start_copy_from_url(sourceblob, metadata={'status': 'copy'})

        # Act
        blobs = list(container.list_blobs(include="copy"))

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob1copy')
        self.assertEqual(blobs[1].blob_type, blobs[0].blob_type)
        self.assertEqual(blobs[1].size, 11)
        self.assertEqual(blobs[1].content_settings.content_type,
                         'application/octet-stream')
        self.assertEqual(blobs[1].content_settings.cache_control, None)
        self.assertEqual(blobs[1].content_settings.content_encoding, None)
        self.assertEqual(blobs[1].content_settings.content_language, None)
        self.assertEqual(blobs[1].content_settings.content_disposition, None)
        self.assertNotEqual(blobs[1].content_settings.content_md5, None)
        self.assertEqual(blobs[1].lease.status, 'unlocked')
        self.assertEqual(blobs[1].lease.state, 'available')
        self.assertNotEqual(blobs[1].copy.id, None)
        self.assertEqual(blobs[1].copy.source, sourceblob)
        self.assertEqual(blobs[1].copy.status, 'success')
        self.assertEqual(blobs[1].copy.progress, '11/11')
        self.assertNotEqual(blobs[1].copy.completion_time, None)

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_delimiter(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        container.get_blob_client('a/blob1').upload_blob(data)
        container.get_blob_client('a/blob2').upload_blob(data)
        container.get_blob_client('b/blob3').upload_blob(data)
        container.get_blob_client('blob4').upload_blob(data)

        # Act
        resp = list(container.walk_blobs())

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        self.assertNamedItemInContainer(resp, 'a/')
        self.assertNamedItemInContainer(resp, 'b/')
        self.assertNamedItemInContainer(resp, 'blob4')

    def test_batch_delete_empty_blob_list(self):
        container_client = ContainerClient("https://mystorageaccount.blob.core.windows.net", "container")
        blob_list = list()
        container_client.delete_blobs(*blob_list)

    @GlobalStorageAccountPreparer()
    def test_delete_blobs_simple(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        try:
            blob_client1 = container.get_blob_client('blob1')
            blob_client1.upload_blob(data)
            container.get_blob_client('blob2').upload_blob(data)
            container.get_blob_client('blob3').upload_blob(data)
        except:
            pass

        # Act
        response = container.delete_blobs(
            blob_client1.get_blob_properties(),
            'blob2',
            'blob3',
        )
        response = list(response)
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_batch_blobs_with_container_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference()
        sas_token = generate_container_sas(
            storage_account.name,
            container_name,
            account_key=storage_account_key,
            permission=ContainerSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        container_client = bsc.get_container_client(container_name)
        container_client.create_container()
        container = ContainerClient.from_container_url(container_client.url, credential=sas_token)
        data = b'hello world'

        try:
            blob_client1 = container.get_blob_client('blob1')
            blob_client1.upload_blob(data)
            container.get_blob_client('blob2').upload_blob(data)
            container.get_blob_client('blob3').upload_blob(data)
        except:
            pass

        # Act
        response = container.delete_blobs(
            blob_client1.get_blob_properties(),
            'blob2',
            'blob3',
        )
        response = list(response)
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_delete_blobs_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}

        try:
            blob_client1 = container.get_blob_client('blob1')
            blob_client1.upload_blob(data, overwrite=True, tags=tags)
            container.get_blob_client('blob2').upload_blob(data, overwrite=True, tags=tags)
            container.get_blob_client('blob3').upload_blob(data,  overwrite=True, tags=tags)
        except:
            pass

        if self.is_live:
            sleep(10)

        # Act
        with self.assertRaises(PartialBatchErrorException):
            container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                if_tags_match_condition="\"tag1\"='firsttag WRONG'"
            )
        response = container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            if_tags_match_condition="\"tag1\"='firsttag'"
        )
        response = list(response)
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_delete_blobs_and_snapshot_using_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        sas_token = generate_account_sas(
            storage_account.name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), sas_token)
        container = self._create_container(bsc)
        data = b'hello world'

        # blob with snapshot
        blob_client1 = container.get_blob_client('bloba')
        blob_client1.upload_blob(data, overwrite=True)
        snapshot = blob_client1.create_snapshot()

        container.get_blob_client('blobb').upload_blob(data, overwrite=True)
        container.get_blob_client('blobc').upload_blob(data, overwrite=True)

        # blob with lease
        blob_client4 = container.get_blob_client('blobd')
        blob_client4.upload_blob(data, overwrite=True)
        lease = blob_client4.acquire_lease()

        # Act
        blob_props = blob_client1.get_blob_properties()
        blob_props.snapshot = snapshot['snapshot']

        blob_props_d = dict()
        blob_props_d['name'] = "blobd"
        blob_props_d['delete_snapshots'] = "include"
        blob_props_d['lease_id'] = lease.id

        response = container.delete_blobs(
            blob_props,
            'blobb',
            'blobc',
            blob_props_d,
            timeout=3
        )
        response = list(response)
        assert len(response) == 4
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202
        assert response[3].status_code == 202

    @GlobalStorageAccountPreparer()
    def test_delete_blobs_simple_no_raise(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        try:
            container.get_blob_client('blob1').upload_blob(data)
            container.get_blob_client('blob2').upload_blob(data)
            container.get_blob_client('blob3').upload_blob(data)
        except:
            pass

        # Act
        response = container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @GlobalStorageAccountPreparer()
    def test_delete_blobs_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc, prefix="test")
        data = b'hello world'

        try:
            blob1_client = container.get_blob_client('blob1')
            blob1_client.upload_blob(data)
            blob1_client.create_snapshot()
            container.get_blob_client('blob2').upload_blob(data)
            container.get_blob_client('blob3').upload_blob(data)
        except:
            pass
        blobs = list(container.list_blobs(include='snapshots'))
        assert len(blobs) == 4  # 3 blobs + 1 snapshot

        # Act
        try:
            response = container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                delete_snapshots='only'
            )
        except PartialBatchErrorException as err:
            parts = list(err.parts)
            assert len(parts) == 3
            assert parts[0].status_code == 202
            assert parts[1].status_code == 404  # There was no snapshot
            assert parts[2].status_code == 404  # There was no snapshot

            blobs = list(container.list_blobs(include='snapshots'))
            assert len(blobs) == 3  # 3 blobs

    @GlobalStorageAccountPreparer()
    def test_standard_blob_tier_set_tier_api_batch(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            response = container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                raise_on_any_failure=False
            )
            blob = container.get_blob_client('blob1')
            data = b'hello world'
            blob.upload_blob(data)
            container.get_blob_client('blob2').upload_blob(data)
            container.get_blob_client('blob3').upload_blob(data)

            blob_ref = blob.get_blob_properties()
            assert blob_ref.blob_tier is not None
            assert blob_ref.blob_tier_inferred
            assert blob_ref.blob_tier_change_time is None

            parts = container.set_standard_blob_tier_blobs(
                tier,
                'blob1',
                'blob2',
                'blob3',
            )

            parts = list(parts)
            assert len(parts) == 3

            assert parts[0].status_code in [200, 202]
            assert parts[1].status_code in [200, 202]
            assert parts[2].status_code in [200, 202]

            blob_ref2 = blob.get_blob_properties()
            assert tier == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred
            assert blob_ref2.blob_tier_change_time is not None

        response = container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_batch_set_standard_blob_tier_for_version(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        container.upload_blob("blob1", "hello world")
        container.upload_blob("blob2", "hello world")
        container.upload_blob("blob3", "hello world")
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            response = container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                raise_on_any_failure=False
            )
            blob = container.get_blob_client('blob1')
            blob2 = container.get_blob_client('blob2')
            blob3 = container.get_blob_client('blob3')
            data = b'hello world'
            resp1 = blob.upload_blob(data, overwrite=True)
            resp2 = blob2.upload_blob(data, overwrite=True)
            resp3 = blob3.upload_blob(data, overwrite=True)
            snapshot = blob3.create_snapshot()

            data2 = b'abc'
            blob.upload_blob(data2, overwrite=True)
            blob2.upload_blob(data2, overwrite=True)
            blob3.upload_blob(data2, overwrite=True)

            prop = blob.get_blob_properties()

            parts = container.set_standard_blob_tier_blobs(
                tier,
                prop,
                {'name': 'blob2', 'version_id': resp2['version_id']},
                {'name': 'blob3', 'snapshot': snapshot['snapshot']},
                raise_on_any_failure=False
            )

            parts = list(parts)
            assert len(parts) == 3

            assert parts[0].status_code in [200, 202]
            assert parts[1].status_code in [200, 202]
            assert parts[2].status_code in [200, 202]

            blob_ref2 = blob.get_blob_properties()
            assert tier == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred
            assert blob_ref2.blob_tier_change_time is not None

        response = container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_standard_blob_tier_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        tier = StandardBlobTier.Cool
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob = container.get_blob_client('blob1')
        data = b'hello world'
        blob.upload_blob(data, overwrite=True, tags=tags)
        container.get_blob_client('blob2').upload_blob(data, overwrite=True, tags=tags)
        container.get_blob_client('blob3').upload_blob(data, overwrite=True, tags=tags)

        blob_ref = blob.get_blob_properties()
        assert blob_ref.blob_tier is not None
        assert blob_ref.blob_tier_inferred
        assert blob_ref.blob_tier_change_time is None

        with self.assertRaises(PartialBatchErrorException):
            container.set_standard_blob_tier_blobs(
                tier,
                'blob1',
                'blob2',
                'blob3',
                if_tags_match_condition="\"tag1\"='firsttag WRONG'"
            )

        parts = container.set_standard_blob_tier_blobs(
            tier,
            'blob1',
            'blob2',
            'blob3',
            if_tags_match_condition="\"tag1\"='firsttag'"
        )

        parts = list(parts)
        assert len(parts) == 3

        assert parts[0].status_code in [200, 202]
        assert parts[1].status_code in [200, 202]
        assert parts[2].status_code in [200, 202]

        blob_ref2 = blob.get_blob_properties()
        assert tier == blob_ref2.blob_tier
        assert not blob_ref2.blob_tier_inferred
        assert blob_ref2.blob_tier_change_time is not None

        container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_standard_blob_tier_set_tiers_with_sas(self, resource_group, location, storage_account,
                                                   storage_account_key):
        sas_token = generate_account_sas(
            storage_account.name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), sas_token)
        container = self._create_container(bsc)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            response = container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                raise_on_any_failure=False
            )
            blob = container.get_blob_client('blob1')
            data = b'hello world'
            blob.upload_blob(data)
            container.get_blob_client('blob2').upload_blob(data)
            container.get_blob_client('blob3').upload_blob(data)

            blob_ref = blob.get_blob_properties()

            parts = container.set_standard_blob_tier_blobs(
                tier,
                blob_ref,
                'blob2',
                'blob3',
                timeout=5
            )

            parts = list(parts)
            assert len(parts) == 3

            assert parts[0].status_code in [200, 202]
            assert parts[1].status_code in [200, 202]
            assert parts[2].status_code in [200, 202]

            blob_ref2 = blob.get_blob_properties()
            assert tier == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred
            assert blob_ref2.blob_tier_change_time is not None

        response = container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )

    @pytest.mark.skip(reason="Wasn't able to get premium account with batch enabled")
    # once we have premium tests, still we don't want to test Py 2.7
    # @pytest.mark.skipif(sys.version_info < (3, 0), reason="Batch not supported on Python 2.7")
    @GlobalStorageAccountPreparer()
    def test_premium_tier_set_tier_api_batch(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        url = self._get_premium_account_url()
        credential = self._get_premium_shared_key_credential()
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if not self.is_playback():
                try:
                    container.create_container()
                except ResourceExistsError:
                    pass

            pblob = container.get_blob_client('blob1')
            pblob.create_page_blob(1024)
            container.get_blob_client('blob2').create_page_blob(1024)
            container.get_blob_client('blob3').create_page_blob(1024)

            blob_ref = pblob.get_blob_properties()
            assert PremiumPageBlobTier.P10 == blob_ref.blob_tier
            assert blob_ref.blob_tier is not None
            assert blob_ref.blob_tier_inferred

            parts = container.set_premium_page_blob_tier_blobs(
                PremiumPageBlobTier.P50,
                'blob1',
                'blob2',
                'blob3',
            )

            parts = list(parts)
            assert len(parts) == 3

            assert parts[0].status_code in [200, 202]
            assert parts[1].status_code in [200, 202]
            assert parts[2].status_code in [200, 202]


            blob_ref2 = pblob.get_blob_properties()
            assert PremiumPageBlobTier.P50 == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred

        finally:
            container.delete_container()

    @GlobalStorageAccountPreparer()
    def test_walk_blobs_with_delimiter(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'

        container.get_blob_client('a/blob1').upload_blob(data)
        container.get_blob_client('a/blob2').upload_blob(data)
        container.get_blob_client('b/c/blob3').upload_blob(data)
        container.get_blob_client('blob4').upload_blob(data)

        blob_list = []
        def recursive_walk(prefix):
            for b in prefix:
                if b.get('prefix'):
                    recursive_walk(b)
                else:
                    blob_list.append(b.name)

        # Act
        recursive_walk(container.walk_blobs())

        # Assert
        self.assertEqual(len(blob_list), 4)
        self.assertEqual(blob_list, ['a/blob1', 'a/blob2', 'b/c/blob3', 'blob4'])

    @GlobalStorageAccountPreparer()
    def test_list_blobs_with_include_multiple(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        pytest.skip("Waiting on metadata XML fix in msrest")
        container = self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        blob1.upload_blob(data, metadata={'number': '1', 'name': 'bob'})
        blob1.create_snapshot()

        container.get_blob_client('blob2').upload_blob(data, metadata={'number': '2', 'name': 'car'})

        # Act
        blobs = list(container.list_blobs(include=["snapshots", "metadata"]))

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertIsNotNone(blobs[0].snapshot)
        self.assertEqual(blobs[0].metadata['number'], '1')
        self.assertEqual(blobs[0].metadata['name'], 'bob')
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertIsNone(blobs[1].snapshot)
        self.assertEqual(blobs[1].metadata['number'], '1')
        self.assertEqual(blobs[1].metadata['name'], 'bob')
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertIsNone(blobs[2].snapshot)
        self.assertEqual(blobs[2].metadata['number'], '2')
        self.assertEqual(blobs[2].metadata['name'], 'car')

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_shared_access_container(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        blob_name  = 'blob1'
        data = b'hello world'

        blob = container.get_blob_client(blob_name)
        blob.upload_blob(data)

        token = generate_container_sas(
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=ContainerSasPermissions(read=True),
        )
        blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)

    @GlobalStorageAccountPreparer()
    def test_web_container_normal_operations_working(self, resource_group, location, storage_account, storage_account_key):
        web_container = "$web"
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)

        # create the web container in case it does not exist yet
        container = bsc.get_container_client(web_container)
        try:
            try:
                created = container.create_container()
                self.assertIsNotNone(created)
            except ResourceExistsError:
                pass

            # test if web container exists
            exist = container.get_container_properties()
            self.assertTrue(exist)

            # create a blob
            blob_name = self.get_resource_name("blob")
            blob_content = self.get_random_text_data(1024)
            blob = container.get_blob_client(blob_name)
            blob.upload_blob(blob_content)

            # get a blob
            blob_data = blob.download_blob(encoding='utf-8')
            self.assertIsNotNone(blob)
            self.assertEqual(blob_data.readall(), blob_content)

        finally:
            # delete container
            container.delete_container()

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_user_delegation_sas_for_container(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        token_credential = self.generate_oauth_token()
        service_client = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential)
        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        container_client = service_client.create_container(self.get_resource_name('oauthcontainer'))
        token = generate_container_sas(
            container_client.account_name,
            container_client.container_name,
            account_key=storage_account_key,
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=ContainerSasPermissions(read=True),
            user_delegation_key=user_delegation_key,
        )

        blob_client = container_client.get_blob_client(self.get_resource_name('oauthblob'))
        blob_content = self.get_random_text_data(1024)
        blob_client.upload_blob(blob_content, length=len(blob_content))

        # Act
        new_blob_client = BlobClient.from_blob_url(blob_client.url, credential=token)
        content = new_blob_client.download_blob(encoding='utf-8')

        # Assert
        self.assertEqual(blob_content, content.readall())

    def test_set_container_permission_from_string(self):
        # Arrange
        permission1 = ContainerSasPermissions(read=True, write=True)
        permission2 = ContainerSasPermissions.from_string('wr')
        self.assertEqual(permission1.read, permission2.read)
        self.assertEqual(permission1.write, permission2.write)

    def test_set_container_permission(self):
        # Arrange
        permission = ContainerSasPermissions.from_string('wrlx')
        self.assertEqual(permission.read, True)
        self.assertEqual(permission.list, True)
        self.assertEqual(permission.write, True)
        self.assertEqual(permission._str, 'rwxl')

    @GlobalStorageAccountPreparer()
    def test_download_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = self._create_container(bsc)
        data = b'hello world'
        blob_name =  self.get_resource_name("blob")

        container.get_blob_client(blob_name).upload_blob(data)

        # Act
        downloaded = container.download_blob(blob_name)

        assert downloaded.readall() == data

    @GlobalStorageAccountPreparer()
    def test_download_blob_in_chunks_where_maxsinglegetsize_is_multiple_of_chunksize(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                max_single_get_size=1024,
                                max_chunk_get_size=512)
        container = self._create_container(bsc)
        data = b'hello world python storage test chunks' * 1024
        blob_name = self.get_resource_name("testiteratechunks")

        container.get_blob_client(blob_name).upload_blob(data, overwrite=True)

        # Act
        downloader= container.download_blob(blob_name)
        downloaded_data = b''
        chunk_size_list = list()
        for chunk in downloader.chunks():
            chunk_size_list.append(len(chunk))
            downloaded_data += chunk

        # the last chunk is not guaranteed to be 666
        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], 512)

        self.assertEqual(downloaded_data, data)

    @GlobalStorageAccountPreparer()
    def test_download_blob_in_chunks_where_maxsinglegetsize_not_multiple_of_chunksize(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                max_single_get_size=1024,
                                max_chunk_get_size=666)
        container = self._create_container(bsc)
        data = b'hello world python storage test chunks' * 1024
        blob_name =  self.get_resource_name("testiteratechunks")

        container.get_blob_client(blob_name).upload_blob(data, overwrite=True)

        # Act
        downloader= container.download_blob(blob_name)
        downloaded_data = b''
        chunk_size_list = list()
        for chunk in downloader.chunks():
            chunk_size_list.append(len(chunk))
            downloaded_data += chunk

        # the last chunk is not guaranteed to be 666
        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], 666)

        self.assertEqual(downloaded_data, data)

    @GlobalStorageAccountPreparer()
    def test_download_blob_in_chunks_where_maxsinglegetsize_smallert_than_chunksize(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                max_single_get_size=215,
                                max_chunk_get_size=512)
        container = self._create_container(bsc)
        data = b'hello world python storage test chunks' * 1024
        blob_name = self.get_resource_name("testiteratechunks")

        container.get_blob_client(blob_name).upload_blob(data, overwrite=True)

        # Act
        downloader= container.download_blob(blob_name)
        downloaded_data = b''
        chunk_size_list = list()
        for chunk in downloader.chunks():
            chunk_size_list.append(len(chunk))
            downloaded_data += chunk

        # the last chunk is not guaranteed to be 666
        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], 512)

        self.assertEqual(downloaded_data, data)
