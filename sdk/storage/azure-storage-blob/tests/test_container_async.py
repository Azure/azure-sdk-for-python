# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from time import sleep

import pytest
import unittest
import asyncio
from dateutil.tz import tzutc

import requests
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer

from azure.storage.blob import (
    PublicAccess,
    AccessPolicy,
    StorageErrorCode,
    BlobBlock,
    BlobType,
    ContentSettings,
    BlobProperties,
    ContainerSasPermissions,
    StandardBlobTier,
    PremiumPageBlobTier,
    generate_container_sas,
    PartialBatchErrorException,
    generate_account_sas, ResourceTypes, AccountSasPermissions)

from _shared.testcase import LogCaptured, GlobalStorageAccountPreparer, GlobalResourceGroupPreparer
from _shared.asynctestcase import AsyncStorageTestCase
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'acontainer'
#------------------------------------------------------------------------------

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageContainerAsyncTest(AsyncStorageTestCase):

    #--Helpers-----------------------------------------------------------------
    def _get_container_reference(self, prefix=TEST_CONTAINER_PREFIX):
        container_name = self.get_resource_name(prefix)
        return container_name

    async def _create_container(self, bsc, prefix=TEST_CONTAINER_PREFIX):
        container_name = self._get_container_reference(prefix)
        container = bsc.get_container_client(container_name)
        try:
            await container.create_container()
        except ResourceExistsError:
            pass
        return container

    async def _to_list(self, async_iterator):
        result = []
        async for item in async_iterator:
            result.append(item)
        return result

    #--Test cases for containers -----------------------------------------
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container()

        # Assert
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_cntnr_w_existing_cntnr_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container()
        with self.assertRaises(HttpResponseError):
            await container.create_container()

        # Assert
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_container_with_public_access_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container(public_access='container')

        # Assert
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_container_with_public_access_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container(public_access='blob')

        blob = container.get_blob_client("blob1")
        await blob.upload_blob(u'xyz')

        anonymous_service = BlobClient(
            self.account_url(storage_account, "blob"),
            container_name=container_name,
            blob_name="blob1")

        # Assert
        self.assertTrue(created)
        await anonymous_service.download_blob()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_container_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container(metadata)

        # Assert
        self.assertTrue(created)
        md_cr = await container.get_container_properties()
        md = md_cr.metadata
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_container_exists_with_lease(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        await container.acquire_lease()

        # Act
        exists = await container.get_container_properties()

        # Assert
        self.assertTrue(exists)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        old_name1 = self._get_container_reference(prefix="oldcontainer1")
        old_name2 = self._get_container_reference(prefix="oldcontainer2")
        new_name = self._get_container_reference(prefix="newcontainer")
        container1 = bsc.get_container_client(old_name1)
        container2 = bsc.get_container_client(old_name2)

        await container1.create_container()
        await container2.create_container()

        new_container = await bsc._rename_container(name=old_name1, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await bsc._rename_container(name=old_name2, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await container1.get_container_properties()
        with self.assertRaises(HttpResponseError):
            await bsc._rename_container(name="badcontainer", new_name="container")
        props = await new_container.get_container_properties()
        self.assertEqual(new_name, props.name)

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_container_with_container_client(
            self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        old_name1 = self._get_container_reference(prefix="oldcontainer1")
        old_name2 = self._get_container_reference(prefix="oldcontainer2")
        new_name = self._get_container_reference(prefix="newcontainer")
        bad_name = self._get_container_reference(prefix="badcontainer")
        container1 = bsc.get_container_client(old_name1)
        container2 = bsc.get_container_client(old_name2)
        bad_container = bsc.get_container_client(bad_name)

        await container1.create_container()
        await container2.create_container()

        new_container = await container1._rename_container(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await container2._rename_container(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await container1.get_container_properties()
        with self.assertRaises(HttpResponseError):
            await bad_container._rename_container(name="badcontainer", new_name="container")
        new_container_props = await new_container.get_container_properties()
        self.assertEqual(new_name, new_container_props.name)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_container_with_source_lease(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        old_name = self._get_container_reference(prefix="old")
        new_name = self._get_container_reference(prefix="new")
        container = bsc.get_container_client(old_name)
        await container.create_container()
        container_lease_id = await container.acquire_lease()
        with self.assertRaises(HttpResponseError):
            await bsc._rename_container(name=old_name, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await bsc._rename_container(name=old_name, new_name=new_name, lease="bad_id")
        new_container = await bsc._rename_container(name=old_name, new_name=new_name, lease=container_lease_id)
        props = await new_container.get_container_properties()
        self.assertEqual(new_name, props.name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_unicode_create_container_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = u'啊齄丂狛狜'

        container = bsc.get_container_client(container_name)
        # Act
        with self.assertRaises(HttpResponseError):
            # not supported - container name must be alphanumeric, lowercase
            await container.create_container()

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_containers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        containers = []
        async for c in bsc.list_containers():
            containers.append(c)


        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, container.container_name)
        self.assertIsNotNone(containers[0].has_immutability_policy)
        self.assertIsNotNone(containers[0].has_legal_hold)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_containers_with_prefix(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        containers = []
        async for c in bsc.list_containers(name_starts_with=container.container_name):
            containers.append(c)

        # Assert
        self.assertIsNotNone(containers)
        self.assertEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertEqual(containers[0].name, container.container_name)
        self.assertIsNone(containers[0].metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_containers_with_include_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        metadata = {'hello': 'world', 'number': '42'}
        resp = await container.set_container_metadata(metadata)

        # Act
        containers = []
        async for c in bsc.list_containers(
            name_starts_with=container.container_name,
            include_metadata=True):
            containers.append(c)

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, container.container_name)
        self.assertDictEqual(containers[0].metadata, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_containers_with_public_access(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}
        resp = await container.set_container_access_policy(signed_identifier, public_access=PublicAccess.Blob)

        # Act
        containers = []
        async for c in bsc.list_containers(name_starts_with=container.container_name):
            containers.append(c)

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, container.container_name)
        self.assertEqual(containers[0].public_access, PublicAccess.Blob)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_containers_with_num_results_and_marker(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        prefix = 'listcontainerasync'
        container_names = []
        for i in range(0, 4):
            cr = await self._create_container(bsc, prefix + str(i))
            container_names.append(cr.container_name)

        container_names.sort()

        # Act
        generator1 = bsc.list_containers(name_starts_with=prefix, results_per_page=2).by_page()
        containers1 = []
        async for c in await generator1.__anext__():
            containers1.append(c)

        generator2 = bsc.list_containers(
            name_starts_with=prefix, results_per_page=2).by_page(generator1.continuation_token)
        containers2 = []
        async for c in await generator2.__anext__():
            containers2.append(c)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '43'}
        container = await self._create_container(bsc)

        # Act
        await container.set_container_metadata(metadata)
        md = await container.get_container_properties()
        metadata_from_response = md.metadata
        # Assert
        self.assertDictEqual(metadata_from_response, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_metadata_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '43'}
        container = await self._create_container(bsc)
        lease_id = await container.acquire_lease()

        # Act
        await container.set_container_metadata(metadata, lease=lease_id)

        # Assert
        md = await container.get_container_properties()
        md = md.metadata
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_metadata_with_non_existing_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()
        container = bsc.get_container_client(container_name)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await container.set_container_metadata({'hello': 'world', 'number': '43'})

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_container_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '42'}
        container = await self._create_container(bsc)
        await container.set_container_metadata(metadata)

        # Act
        md_cr = await container.get_container_properties()
        md = md_cr.metadata

        # Assert
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_container_metadata_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '42'}
        container = await self._create_container(bsc)
        await container.set_container_metadata(metadata)
        lease_id = await container.acquire_lease()

        # Act
        md = await container.get_container_properties(lease=lease_id)
        md = md.metadata

        # Assert
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_container_exists(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(
            storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())

        container1 = await self._create_container(bsc, prefix="container1")
        container2_name = self._get_container_reference(prefix="container2")
        container2 = bsc.get_container_client(container2_name)

        self.assertTrue(await container1.exists())
        self.assertFalse(await container2.exists())

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_container_properties(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '42'}
        container = await self._create_container(bsc)
        await container.set_container_metadata(metadata)

        # Act
        props = await container.get_container_properties()

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_container_properties_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '42'}
        container = await self._create_container(bsc)
        await container.set_container_metadata(metadata)
        lease_id = await container.acquire_lease()

        # Act
        props = await container.get_container_properties(lease=lease_id)
        await lease_id.break_lease()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        self.assertEqual(props.lease.duration, 'infinite')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.status, 'locked')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_container_acl(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        acl = await container.get_container_access_policy()

        # Assert
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))
        self.assertEqual(len(acl.get('signed_identifiers')), 0)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_container_acl_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        lease_id = await container.acquire_lease()

        # Act
        acl = await container.get_container_access_policy(lease=lease_id)

        # Assert
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}
        response = await container.set_container_access_policy(signed_identifier)

        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 1)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_one_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        from dateutil.tz import tzutc
        container = await self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}

        response = await container.set_container_access_policy(signed_identifier)

        # Assert
        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        lease_id = await container.acquire_lease()

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}
        await container.set_container_access_policy(signed_identifier, lease=lease_id)

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_public_access(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier = {'testid': access_policy}
        await container.set_container_access_policy(signed_identifier, public_access='container')

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual('container', acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        await container.set_container_access_policy(signed_identifiers=dict())

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 0)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=1))
        identifiers = {'testid': access_policy}
        await container.set_container_access_policy(identifiers)

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual('testid', acl.get('signed_identifiers')[0].id)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_empty_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        identifiers = {i: None for i in range(0, 3)}

        # Act
        await container.set_container_access_policy(identifiers)

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 3)
        self.assertEqual('0', acl.get('signed_identifiers')[0].id)
        self.assertIsNone(acl.get('signed_identifiers')[0].access_policy)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_with_three_identifiers(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=1))
        identifiers = {i: access_policy for i in range(2)}

        # Act
        await container.set_container_access_policy(identifiers)

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 2)
        self.assertEqual('0', acl.get('signed_identifiers')[0].id)
        self.assertIsNotNone(acl.get('signed_identifiers')[0].access_policy)
        self.assertIsNone(acl.get('public_access'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_container_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = await self._create_container(bsc)

        # Act
        identifiers = dict()
        for i in range(0, 6):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError) as e:
            await container_name.set_container_access_policy(identifiers)
        self.assertEqual(
            str(e.exception),
            'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'
        )

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_acquire_and_release(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        lease = await container.acquire_lease()
        await lease.release()

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_renew(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        lease = await container.acquire_lease(lease_duration=15)
        self.sleep(10)
        lease_id_start = lease.id

        # Act
        await lease.renew()

        # Assert
        self.assertEqual(lease.id, lease_id_start)
        self.sleep(5)
        with self.assertRaises(HttpResponseError):
            await container.delete_container()
        self.sleep(10)
        await container.delete_container()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_break_period(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        lease = await container.acquire_lease(lease_duration=15)

        # Assert
        await lease.break_lease(lease_break_period=5)
        self.sleep(6)
        with self.assertRaises(HttpResponseError):
            await container.delete_container(lease=lease)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_break_released_lease_fails(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        lease = await container.acquire_lease()
        await lease.release()

        # Act
        with self.assertRaises(HttpResponseError):
            await lease.break_lease()

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_with_duration(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        lease = await container.acquire_lease(lease_duration=15)

        # Assert
        with self.assertRaises(HttpResponseError):
            await container.acquire_lease()
        self.sleep(15)
        await container.acquire_lease()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_twice(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        lease = await container.acquire_lease(lease_duration=15)

        # Assert
        lease2 = await container.acquire_lease(lease_id=lease.id)
        self.assertEqual(lease.id, lease2.id)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_with_proposed_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        proposed_lease_id = '55e97f64-73e8-4390-838d-d9e84a374321'
        lease = await container.acquire_lease(lease_id=proposed_lease_id)

        # Assert
        self.assertEqual(proposed_lease_id, lease.id)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_container_change_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        lease_id = '29e0b239-ecda-4f69-bfa3-95f6af91464c'
        lease = await container.acquire_lease()
        lease_id1 = lease.id
        await lease.change(proposed_lease_id=lease_id)
        await lease.renew()
        lease_id2 = lease.id

        # Assert
        self.assertIsNotNone(lease_id1)
        self.assertIsNotNone(lease_id2)
        self.assertNotEqual(lease_id1, lease_id)
        self.assertEqual(lease_id2, lease_id)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_container_with_existing_container(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)

        # Act
        deleted = await container.delete_container()

        # Assert
        self.assertIsNone(deleted)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_cntnr_w_nonexisting_cntnr_fail_not_exist(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container_name = self._get_container_reference()
        container = bsc.get_container_client(container_name)

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(ResourceNotFoundError):
                await container.delete_container()

            log_as_str = log_captured.getvalue()
            #self.assertTrue('ERROR' in log_as_str)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_container_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        lease = await container.acquire_lease(lease_duration=15)

        # Act
        deleted = await container.delete_container(lease=lease)

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            await container.get_container_properties()

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_undelete_container(self, resource_group, location, storage_account, storage_account_key):
        # container soft delete should enabled by SRP call or use armclient, so make this test as playback only.
        pytest.skip('This will be added back along with STG74 features')
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_client = await self._create_container(bsc)

        # Act
        await container_client.delete_container()
        # to make sure the container deleted
        with self.assertRaises(ResourceNotFoundError):
            await container_client.get_container_properties()

        container_list = list()
        async for c in bsc.list_containers(include_deleted=True):
            container_list.append(c)
        self.assertTrue(len(container_list) >= 1)

        restored_version = 0
        for container in container_list:
            # find the deleted container and restore it
            if container.deleted and container.name == container_client.container_name:
                restored_ctn_client = await bsc.undelete_container(container.name, container.version,
                                                                    new_name="restoredctn" + str(restored_version))
                restored_version += 1

                # to make sure the deleted container is restored
                props = await restored_ctn_client.get_container_properties()
                self.assertIsNotNone(props)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_restore_to_existing_container(self, resource_group, location, storage_account, storage_account_key):
        pytest.skip('This will be added back along with STG74 features')
        # container soft delete should enabled by SRP call or use armclient, so make this test as playback only.

        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        # get an existing container
        existing_container_client = await self._create_container(bsc, prefix="existing")
        container_client = await self._create_container(bsc)

        # Act
        await container_client.delete_container()
        # to make sure the container deleted
        with self.assertRaises(ResourceNotFoundError):
            await container_client.get_container_properties()

        container_list = list()
        async for c in bsc.list_containers(include_deleted=True):
            container_list.append(c)
        self.assertTrue(len(container_list) >= 1)

        for container in container_list:
            # find the deleted container and restore it
            if container.deleted and container.name == container_client.container_name:
                with self.assertRaises(HttpResponseError):
                    await bsc.undelete_container(container.name, container.version,
                                                  new_name=existing_container_client.container_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_names(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        await (container.get_blob_client('blob1')).upload_blob(data)
        await (container.get_blob_client('blob2')).upload_blob(data)


        # Act
        blobs = []
        async for b in container.list_blobs():
            blobs.append(b.name)

        self.assertEqual(blobs, ['blob1', 'blob2'])

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_returns_rehydrate_priority(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        blob_client = container.get_blob_client('blob1')
        await blob_client.upload_blob(data, standard_blob_tier=StandardBlobTier.Archive)
        await blob_client.set_standard_blob_tier(StandardBlobTier.Hot)

        # Act
        async for blob_properties in container.list_blobs():
            if blob_properties.name == blob_client.blob_name:
                self.assertEqual(blob_properties.rehydrate_priority, "Standard")

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        cr0 = container.get_blob_client('blob1')
        await cr0.upload_blob(data)
        cr1 = container.get_blob_client('blob2')
        await cr1.upload_blob(data)

        # Act
        blobs = []
        async for b in container.list_blobs():
            blobs.append(b)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_object_replication_policy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = await self._create_container(bsc)
        data = b'hello world'
        b_c = container.get_blob_client('blob1')
        await b_c.upload_blob(data, overwrite=True)
        metadata = {'hello': 'world', 'number': '42'}
        await b_c.set_blob_metadata(metadata)

        prop = await b_c.get_blob_properties()

        await container.get_blob_client('blob2').upload_blob(data, overwrite=True)

        # Act
        blobs_list = container.list_blobs()
        number_of_blobs_with_policy = 0
        async for blob in blobs_list:
            if blob.object_replication_source_properties is not None:
                number_of_blobs_with_policy += 1

        # Assert
        self.assertIsNot(number_of_blobs_with_policy, 0)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_leased_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        await blob1.upload_blob(data)
        lease = await blob1.acquire_lease()

        # Act
        resp = []
        async for b in container.list_blobs():
            resp.append(b)
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
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_prefix(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        c0 = container.get_blob_client('blob_a1')
        await c0.upload_blob(data)
        c1 = container.get_blob_client('blob_a2')
        await c1.upload_blob(data)
        c2 = container.get_blob_client('blob_b1')
        await c2.upload_blob(data)

        # Act
        resp = []
        async for b in container.list_blobs(name_starts_with='blob_a'):
            resp.append(b)

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertNamedItemInContainer(resp, 'blob_a1')
        self.assertNamedItemInContainer(resp, 'blob_a2')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_num_results(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        c0 = container.get_blob_client('blob_a1')
        await c0.upload_blob(data)
        c1 = container.get_blob_client('blob_a2')
        await c1.upload_blob(data)
        c2 = container.get_blob_client('blob_a3')
        await c2.upload_blob(data)
        c3 = container.get_blob_client('blob_b1')
        await c3.upload_blob(data)

        # Act
        generator = container.list_blobs(results_per_page=2).by_page()
        blobs = []
        async for b in await generator.__anext__():
            blobs.append(b)

        # Assert
        self.assertIsNotNone(blobs)
        self.assertEqual(len(blobs), 2)
        self.assertNamedItemInContainer(generator.current_page, 'blob_a1')
        self.assertNamedItemInContainer(generator.current_page, 'blob_a2')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_include_snapshots(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        await blob1.upload_blob(data)
        await blob1.create_snapshot()
        await (container.get_blob_client('blob2')).upload_blob(data)

        # Act
        blobs = []
        async for b in container.list_blobs(include="snapshots"):
            blobs.append(b)

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertIsNotNone(blobs[0].snapshot)
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertIsNone(blobs[1].snapshot)
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertIsNone(blobs[2].snapshot)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_include_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        await blob1.upload_blob(data, metadata={'number': '1', 'name': 'bob'})
        await blob1.create_snapshot()
        cr = container.get_blob_client('blob2')
        await cr.upload_blob(data, metadata={'number': '2', 'name': 'car'})

        # Act
        blobs = []
        async for b in container.list_blobs(include="metadata"):
            blobs.append(b)

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[0].metadata['number'], '1')
        self.assertEqual(blobs[0].metadata['name'], 'bob')
        self.assertEqual(blobs[1].name, 'blob2')
        self.assertEqual(blobs[1].metadata['number'], '2')
        self.assertEqual(blobs[1].metadata['name'], 'car')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_include_uncommittedblobs(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        await blob1.stage_block('1', b'AAA')
        await blob1.stage_block('2', b'BBB')
        await blob1.stage_block('3', b'CCC')

        blob2 = container.get_blob_client('blob2')
        await blob2.upload_blob(data, metadata={'number': '2', 'name': 'car'})

        # Act
        blobs = []
        async for b in container.list_blobs(include="uncommittedblobs"):
            blobs.append(b)

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob2')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_include_copy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        await (container.get_blob_client('blob1')).upload_blob(data, metadata={'status': 'original'})
        sourceblob = 'https://{0}.blob.core.windows.net/{1}/blob1'.format(
            storage_account.name,
            container.container_name)

        blobcopy = container.get_blob_client('blob1copy')
        await blobcopy.start_copy_from_url(sourceblob, metadata={'status': 'copy'})

        # Act
        blobs = []
        async for b in container.list_blobs(include="copy"):
            blobs.append(b)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_delimiter(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        cr0 = container.get_blob_client('a/blob1')
        await cr0.upload_blob(data)
        cr1 = container.get_blob_client('a/blob2')
        await cr1.upload_blob(data)
        cr2 = container.get_blob_client('b/blob3')
        await cr2.upload_blob(data)
        cr4 = container.get_blob_client('blob4')
        await cr4.upload_blob(data)

        # Act
        resp = []
        async for w in container.walk_blobs():
            resp.append(w)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blobs_simple(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        try:
            blob_client1 = container.get_blob_client('blob1')
            await blob_client1.upload_blob(data)
            await container.get_blob_client('blob2').upload_blob(data)
            await container.get_blob_client('blob3').upload_blob(data)
        except:
            pass

        # Act
        response = await self._to_list(await container.delete_blobs(
            await blob_client1.get_blob_properties(),
            'blob2',
            'blob3',
        ))
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_batch_blobs_with_container_sas(
            self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container_name = self._get_container_reference("testcont")
        sas_token = generate_container_sas(
            storage_account.name,
            container_name,
            account_key=storage_account_key,
            permission=ContainerSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        container_client = bsc.get_container_client(container_name)
        await container_client.create_container()
        container = ContainerClient.from_container_url(container_client.url, credential=sas_token)
        data = b'hello world'

        try:
            blob_client1 = container.get_blob_client('blob1')
            await blob_client1.upload_blob(data)
            await container.get_blob_client('blob2').upload_blob(data)
            await container.get_blob_client('blob3').upload_blob(data)
        except:
            pass

        # Act
        response = await self._to_list(await container.delete_blobs(
            await blob_client1.get_blob_properties(),
            'blob2',
            'blob3'
        ))
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blobs_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = await self._create_container(bsc)
        data = b'hello world'
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}

        try:
            blob_client1 = container.get_blob_client('blob1')
            await blob_client1.upload_blob(data, overwrite=True, tags=tags)
            await container.get_blob_client('blob2').upload_blob(data, overwrite=True, tags=tags)
            await container.get_blob_client('blob3').upload_blob(data,  overwrite=True, tags=tags)
        except:
            pass

        if self.is_live:
            sleep(10)

        # Act
        with self.assertRaises(PartialBatchErrorException):
            await container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                if_tags_match_condition="\"tag1\"='firsttag WRONG'"
            )
        blob_list = await container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            if_tags_match_condition="\"tag1\"='firsttag'"
        )

        response = list()
        async for sub_resp in blob_list:
            response.append(sub_resp)

        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blobs_and_snapshot_using_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        sas_token = generate_account_sas(
            storage_account.name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), sas_token)
        container = await self._create_container(bsc)
        data = b'hello world'

        # blob with snapshot
        blob_client1 = container.get_blob_client('bloba')
        await blob_client1.upload_blob(data, overwrite=True)
        snapshot = await blob_client1.create_snapshot()

        blob_client2 = container.get_blob_client('blobb')
        await blob_client2.upload_blob(data, overwrite=True)
        blob_client3 = container.get_blob_client('blobc')
        await blob_client3.upload_blob(data, overwrite=True)

        # blob with lease
        blob_client4 = container.get_blob_client('blobd')
        await blob_client4.upload_blob(data, overwrite=True)
        lease = await blob_client4.acquire_lease()

        # Act
        blob_props = await blob_client1.get_blob_properties()
        blob_props.snapshot = snapshot['snapshot']

        blob_props_d = dict()
        blob_props_d['name'] = "blobd"
        blob_props_d['delete_snapshots'] = "include"
        blob_props_d['lease_id'] = lease.id

        response = await self._to_list(await container.delete_blobs(
            blob_props,
            'blobb',
            'blobc',
            blob_props_d,
            timeout=3
        ))
        response = list(response)
        assert len(response) == 4
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202
        assert response[3].status_code == 202

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blobs_simple_no_raise(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        try:
            await container.get_blob_client('blob1').upload_blob(data)
            await container.get_blob_client('blob2').upload_blob(data)
            await container.get_blob_client('blob3').upload_blob(data)
        except:
            pass

        # Act
        response = await self._to_list(await container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        ))
        assert len(response) == 3
        assert response[0].status_code == 202
        assert response[1].status_code == 202
        assert response[2].status_code == 202

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blobs_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        try:
            blob1_client = container.get_blob_client('blob1')
            await blob1_client.upload_blob(data)
            await blob1_client.create_snapshot()
            await container.get_blob_client('blob2').upload_blob(data)
            await container.get_blob_client('blob3').upload_blob(data)
        except:
            pass
        blobs = await self._to_list(container.list_blobs(include='snapshots'))
        assert len(blobs) == 4  # 3 blobs + 1 snapshot

        # Act
        try:
            response = await self._to_list(await container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                delete_snapshots='only'
            ))
        except PartialBatchErrorException as err:
            parts_list = err.parts
            assert len(parts_list) == 3
            assert parts_list[0].status_code == 202
            assert parts_list[1].status_code == 404  # There was no snapshot
            assert parts_list[2].status_code == 404  # There was no snapshot

            blobs = await self._to_list(container.list_blobs(include='snapshots'))
            assert len(blobs) == 3  # 3 blobs

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_standard_blob_tier_set_tier_api_batch(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            try:
                blob = container.get_blob_client('blob1')
                data = b'hello world'
                await blob.upload_blob(data)
                await container.get_blob_client('blob2').upload_blob(data)
                await container.get_blob_client('blob3').upload_blob(data)

                blob_ref = await blob.get_blob_properties()
                assert blob_ref.blob_tier is not None
                assert blob_ref.blob_tier_inferred
                assert blob_ref.blob_tier_change_time is None

                parts = await self._to_list(await container.set_standard_blob_tier_blobs(
                    tier,
                    'blob1',
                    'blob2',
                    'blob3',
                ))

                assert len(parts) == 3

                assert parts[0].status_code in [200, 202]
                assert parts[1].status_code in [200, 202]
                assert parts[2].status_code in [200, 202]

                blob_ref2 = await blob.get_blob_properties()
                assert tier == blob_ref2.blob_tier
                assert not blob_ref2.blob_tier_inferred
                assert blob_ref2.blob_tier_change_time is not None

            finally:
                await container.delete_blobs(
                    'blob1',
                    'blob2',
                    'blob3',
                )

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    @AsyncStorageTestCase.await_prepared_test
    async def test_standard_blob_tier_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key)
        container = await self._create_container(bsc)
        tier = StandardBlobTier.Cool
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob = container.get_blob_client('blob1')
        data = b'hello world'
        await blob.upload_blob(data, overwrite=True, tags=tags)
        await container.get_blob_client('blob2').upload_blob(data, overwrite=True, tags=tags)
        await container.get_blob_client('blob3').upload_blob(data, overwrite=True, tags=tags)

        blob_ref = await blob.get_blob_properties()
        assert blob_ref.blob_tier is not None
        assert blob_ref.blob_tier_inferred
        assert blob_ref.blob_tier_change_time is None

        with self.assertRaises(PartialBatchErrorException):
            await container.set_standard_blob_tier_blobs(
                tier,
                'blob1',
                'blob2',
                'blob3',
                if_tags_match_condition="\"tag1\"='firsttag WRONG'"
            )

        parts_list = await container.set_standard_blob_tier_blobs(
            tier,
            'blob1',
            'blob2',
            'blob3',
            if_tags_match_condition="\"tag1\"='firsttag'"
        )

        parts = list()
        async for part in parts_list:
            parts.append(part)
        assert len(parts) == 3

        assert parts[0].status_code in [200, 202]
        assert parts[1].status_code in [200, 202]
        assert parts[2].status_code in [200, 202]

        blob_ref2 = await blob.get_blob_properties()
        assert tier == blob_ref2.blob_tier
        assert not blob_ref2.blob_tier_inferred
        assert blob_ref2.blob_tier_change_time is not None

        await container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_standard_blob_tier_set_tiers_with_sas(self, resource_group, location, storage_account,
                                                   storage_account_key):
        sas_token = generate_account_sas(
            storage_account.name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), sas_token)
        container = await self._create_container(bsc)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            response = await container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
                raise_on_any_failure=False
            )
            blob = container.get_blob_client('blob1')
            data = b'hello world'
            await blob.upload_blob(data)
            await container.get_blob_client('blob2').upload_blob(data)
            await container.get_blob_client('blob3').upload_blob(data)

            blob_ref = await blob.get_blob_properties()

            parts = await self._to_list(await container.set_standard_blob_tier_blobs(
                    tier,
                    blob_ref,
                    'blob2',
                    'blob3',
                ))

            parts = list(parts)
            assert len(parts) == 3

            assert parts[0].status_code in [200, 202]
            assert parts[1].status_code in [200, 202]
            assert parts[2].status_code in [200, 202]

            blob_ref2 = await blob.get_blob_properties()
            assert tier == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred
            assert blob_ref2.blob_tier_change_time is not None

        response = await container.delete_blobs(
            'blob1',
            'blob2',
            'blob3',
            raise_on_any_failure=False
        )

    @pytest.mark.skip(reason="Wasn't able to get premium account with batch enabled")
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_premium_tier_set_tier_api_batch(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        url = self._get_premium_account_url()
        credential = self._get_premium_shared_key_credential()
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if not self.is_playback():
                try:
                    await container.create_container()
                except ResourceExistsError:
                    pass

            pblob = container.get_blob_client('blob1')
            await pblob.create_page_blob(1024)
            await container.get_blob_client('blob2').create_page_blob(1024)
            await container.get_blob_client('blob3').create_page_blob(1024)

            blob_ref = await pblob.get_blob_properties()
            assert PremiumPageBlobTier.P10 == blob_ref.blob_tier
            assert blob_ref.blob_tier is not None
            assert blob_ref.blob_tier_inferred

            parts = await self._to_list(container.set_premium_page_blob_tier_blobs(
                PremiumPageBlobTier.P50,
                'blob1',
                'blob2',
                'blob3',
            ))

            assert len(parts) == 3

            assert parts[0].status_code in [200, 202]
            assert parts[1].status_code in [200, 202]
            assert parts[2].status_code in [200, 202]


            blob_ref2 = await pblob.get_blob_properties()
            assert PremiumPageBlobTier.P50 == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred

        finally:
            await container.delete_blobs(
                'blob1',
                'blob2',
                'blob3',
            )

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_walk_blobs_with_delimiter(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'

        cr0 = container.get_blob_client('a/blob1')
        await cr0.upload_blob(data)
        cr1 = container.get_blob_client('a/blob2')
        await cr1.upload_blob(data)
        cr2 = container.get_blob_client('b/c/blob3')
        await cr2.upload_blob(data)
        cr3 = container.get_blob_client('blob4')
        await cr3.upload_blob(data)

        blob_list = []
        async def recursive_walk(prefix):
            async for b in prefix:
                if b.get('prefix'):
                    await recursive_walk(b)
                else:
                    blob_list.append(b.name)

        # Act
        await recursive_walk(container.walk_blobs())

        # Assert
        self.assertEqual(len(blob_list), 4)
        self.assertEqual(blob_list, ['a/blob1', 'a/blob2', 'b/c/blob3', 'blob4'])

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_with_include_multiple(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        blob1 = container.get_blob_client('blob1')
        await blob1.upload_blob(data, metadata={'number': '1', 'name': 'bob'})
        await blob1.create_snapshot()

        client = container.get_blob_client('blob2')
        await client.upload_blob(data, metadata={'number': '2', 'name': 'car'})

        # Act
        blobs = []
        async for b in container.list_blobs(include=["snapshots", "metadata"]):
            blobs.append(b)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_shared_access_container(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        blob_name  = 'blob1'
        data = b'hello world'

        blob = container.get_blob_client(blob_name)
        await blob.upload_blob(data)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_web_container_normal_operations_working(self, resource_group, location, storage_account, storage_account_key):
        web_container = "web"
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())

        # create the web container in case it does not exist yet
        container = bsc.get_container_client(web_container)
        try:
            try:
                created = await container.create_container()
                self.assertIsNotNone(created)
            except ResourceExistsError:
                pass

            # test if web container exists
            exist = await container.get_container_properties()
            self.assertTrue(exist)

            # create a blob
            blob_name = self.get_resource_name("blob")
            blob_content = self.get_random_text_data(1024)
            blob = container.get_blob_client(blob_name)
            await blob.upload_blob(blob_content)

            # get a blob
            blob_data = await (await blob.download_blob()).readall()
            self.assertIsNotNone(blob)
            self.assertEqual(blob_data.decode('utf-8'), blob_content)

        finally:
            # delete container
            await container.delete_container()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_download_blob_async(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, transport=AiohttpTestTransport())
        container = await self._create_container(bsc)
        data = b'hello world'
        blob_name = self.get_resource_name("blob")

        blob = container.get_blob_client(blob_name)
        await blob.upload_blob(data)

        # Act
        downloaded = await container.download_blob(blob_name)
        raw = await downloaded.readall()
        assert raw == data

    @GlobalStorageAccountPreparer()
    async def test_download_blob_in_chunks_where_maxsinglegetsize_is_multiple_of_chunksize(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                transport=AiohttpTestTransport(),
                                max_single_get_size=1024,
                                max_chunk_get_size=512)
        container = await self._create_container(bsc)
        data = b'hello world python storage test chunks' * 1024
        blob_name = self.get_resource_name("testiteratechunks")

        await container.get_blob_client(blob_name).upload_blob(data, overwrite=True)

        # Act
        downloader = await container.download_blob(blob_name)
        downloaded_data = b''
        chunk_size_list = list()
        async for chunk in downloader.chunks():
            chunk_size_list.append(len(chunk))
            downloaded_data += chunk

        # the last chunk is not guaranteed to be 666
        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], 512)

        self.assertEqual(downloaded_data, data)

    @GlobalStorageAccountPreparer()
    async def test_download_blob_in_chunks_where_maxsinglegetsize_not_multiple_of_chunksize(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                transport=AiohttpTestTransport(),
                                max_single_get_size=1024,
                                max_chunk_get_size=666)
        container = await self._create_container(bsc)
        data = b'hello world python storage test chunks' * 1024
        blob_name = self.get_resource_name("testiteratechunks")

        await container.get_blob_client(blob_name).upload_blob(data, overwrite=True)

        # Act
        downloader= await container.download_blob(blob_name)
        downloaded_data = b''
        chunk_size_list = list()
        async for chunk in downloader.chunks():
            chunk_size_list.append(len(chunk))
            downloaded_data += chunk

        # the last chunk is not guaranteed to be 666
        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], 666)

        self.assertEqual(downloaded_data, data)

    @GlobalStorageAccountPreparer()
    async def test_download_blob_in_chunks_where_maxsinglegetsize_smallert_than_chunksize(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                transport=AiohttpTestTransport(),
                                max_single_get_size=215,
                                max_chunk_get_size=512)
        container = await self._create_container(bsc)
        data = b'hello world python storage test chunks' * 1024
        blob_name = self.get_resource_name("testiteratechunks")

        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(data, overwrite=True)

        downloader = await container.download_blob(blob_name)
        downloaded_data = b''
        chunk_size_list = list()
        async for chunk in downloader.chunks():
            chunk_size_list.append(len(chunk))
            downloaded_data += chunk

        # the last chunk is not guaranteed to be 666
        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], 512)

        self.assertEqual(downloaded_data, data)

#------------------------------------------------------------------------------
