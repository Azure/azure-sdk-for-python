# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
import asyncio
import time
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, \
    ResourceModifiedError, ServiceRequestError, AzureError
from azure.storage.filedatalake import ContentSettings, DirectorySasPermissions, generate_file_system_sas, \
    FileSystemSasPermissions
from azure.storage.filedatalake import generate_directory_sas
from azure.storage.filedatalake.aio import DataLakeServiceClient, DataLakeDirectoryClient
from azure.storage.filedatalake import AccessControlChangeResult, AccessControlChangeCounters

from testcase import (
    StorageTestCase,
    record,
    TestMode

)

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
REMOVE_ACL = "mask," + "default:user,default:group," + \
             "user:ec3595d6-2c17-4696-8caa-7e139758d24a,group:ec3595d6-2c17-4696-8caa-7e139758d24a," + \
             "default:user:ec3595d6-2c17-4696-8caa-7e139758d24a,default:group:ec3595d6-2c17-4696-8caa-7e139758d24a"


# ------------------------------------------------------------------------------


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """

    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class DirectoryTest(StorageTestCase):
    def setUp(self):
        super(DirectoryTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY,
                                         transport=AiohttpTestTransport())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dsc.__aenter__())
        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                loop.run_until_complete(file_system.create_file_system(timeout=5))
            except ResourceExistsError:
                pass

    def tearDown(self):
        if not self.is_playback():
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.dsc.delete_file_system(self.file_system_name))
                loop.run_until_complete(self.dsc.__aexit__())
            except:
                pass

        return super(DirectoryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    async def _create_directory_and_get_directory_client(self, directory_name=None):
        directory_name = directory_name if directory_name else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        return directory_client

    async def _create_sub_directory_and_files(self, directory_client, num_of_dirs, num_of_files_per_dir):
        # the name suffix matter since we need to avoid creating the same directories/files in record mode
        for i in range(0, num_of_dirs):
            sub_dir = await directory_client.create_sub_directory(self.get_resource_name('subdir' + str(i)))
            for j in range(0, num_of_files_per_dir):
                await sub_dir.create_file(self.get_resource_name('subfile' + str(j)))

    async def _create_file_system(self):
        return await self.dsc.create_file_system(self._get_file_system_reference())

    # --Helpers-----------------------------------------------------------------

    async def _test_create_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory())

    async def _test_using_oauth_token_credential_to_create_directory(self):
        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()

        token_credential = self.generate_async_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        response = await directory_client.create_directory()
        self.assertIsNotNone(response)

    @record
    def test_using_oauth_token_credential_to_create_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_using_oauth_token_credential_to_create_directory())

    async def _test_create_directory_with_match_conditions(self):
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(match_condition=MatchConditions.IfMissing)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_match_conditions_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_match_conditions())

    async def _test_create_directory_with_permission(self):
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(permissions="rwxr--r--", umask="0000")

        prop = await directory_client.get_access_control()

        # Assert
        self.assertTrue(created)
        self.assertEqual(prop['permissions'], 'rwxr--r--')

    @record
    def test_create_directory_with_permission_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_permission())

    async def _test_create_directory_with_content_settings(self):
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_content_settings_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_content_settings())

    async def _test_create_directory_with_metadata(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(metadata=metadata)

        properties = await directory_client.get_directory_properties()

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_metadata_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_metadata())

    async def _test_delete_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        response = await directory_client.delete_directory()
        # Assert
        self.assertIsNone(response)

    @record
    def test_delete_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_directory())

    async def _test_delete_directory_with_if_modified_since(self):
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        prop = await directory_client.get_directory_properties()

        with self.assertRaises(ResourceModifiedError):
            await directory_client.delete_directory(if_modified_since=prop['last_modified'])

    @record
    def test_delete_directory_with_if_modified_since_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_directory_with_if_modified_since())

    async def _test_create_sub_directory_and_delete_sub_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Create a directory first, to prepare for creating sub directory
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        # Create sub directory from the current directory
        sub_directory_name = 'subdir'
        sub_directory_created = await directory_client.create_sub_directory(sub_directory_name)

        # to make sure the sub directory was indeed created by get sub_directory properties from sub directory client
        sub_directory_client = self.dsc.get_directory_client(self.file_system_name,
                                                             directory_name + '/' + sub_directory_name)
        sub_properties = await sub_directory_client.get_directory_properties()

        # Assert
        self.assertTrue(sub_directory_created)
        self.assertTrue(sub_properties)

        # Act
        await directory_client.delete_sub_directory(sub_directory_name)
        with self.assertRaises(ResourceNotFoundError):
            await sub_directory_client.get_directory_properties()

    @record
    def test_create_sub_directory_and_delete_sub_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_sub_directory_and_delete_sub_directory())

    async def _test_set_access_control(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        response = await directory_client.set_access_control(permissions='0777')
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_set_access_control_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control())

    async def _test_set_access_control_with_acl(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        acl = 'user::rwx,group::r-x,other::rwx'
        await directory_client.set_access_control(acl=acl)
        access_control = await directory_client.get_access_control()

        # Assert

        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_set_access_control_with_acl_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_with_acl())

    async def _test_set_access_control_if_none_modified(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = await directory_client.create_directory()

        response = await directory_client.set_access_control(permissions='0777', etag=resp['etag'],
                                                             match_condition=MatchConditions.IfNotModified)
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_set_access_control_if_none_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_if_none_modified())

    async def _test_get_access_control(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata, permissions='0777')

        # Act
        response = await directory_client.get_access_control()
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_access_control_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_access_control())

    async def _test_get_access_control_with_match_conditions(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = await directory_client.create_directory(permissions='0777', umask='0000')

        # Act
        response = await directory_client.get_access_control(etag=resp['etag'],
                                                             match_condition=MatchConditions.IfNotModified)
        # Assert
        self.assertIsNotNone(response)
        self.assertEquals(response['permissions'], 'rwxrwxrwx')

    @record
    def test_get_access_control_with_match_conditions_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_access_control_with_match_conditions())

    @record
    def test_set_access_control_recursive_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_recursive_async())

    async def _test_set_access_control_recursive_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = await directory_client.set_access_control_recursive(acl=acl)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_set_access_control_recursive_throws_exception_containing_continuation_token_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_recursive_throws_exception_containing_continuation_token())

    async def _test_set_access_control_recursive_throws_exception_containing_continuation_token(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        response_list = list()

        def callback(response):
            response_list.append(response)
            if len(response_list) == 2:
                raise ServiceRequestError("network problem")
        acl = 'user::rwx,group::r-x,other::rwx'

        with self.assertRaises(AzureError) as acl_error:
            await directory_client.set_access_control_recursive(acl=acl, batch_size=2, max_batches=2,
                                                                raw_response_hook=callback, retry_total=0)
        self.assertIsNotNone(acl_error.exception.continuation_token)
        self.assertEqual(acl_error.exception.message, "network problem")
        self.assertIsInstance(acl_error.exception, ServiceRequestError)

    @record
    def test_set_access_control_recursive_in_batches_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_recursive_in_batches_async())

    async def _test_set_access_control_recursive_in_batches_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = await directory_client.set_access_control_recursive(acl=acl, batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_set_access_control_recursive_in_batches_with_progress_callback_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_recursive_in_batches_with_progress_callback_async())

    async def _test_set_access_control_recursive_in_batches_with_progress_callback_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        last_response = AccessControlChangeResult(None, "")

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count

            last_response.counters = resp.aggregate_counters

        summary = await directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                      batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(summary.counters.directories_successful, last_response.counters.directories_successful)
        self.assertEqual(summary.counters.files_successful, last_response.counters.files_successful)
        self.assertEqual(summary.counters.failure_count, last_response.counters.failure_count)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_set_access_control_recursive_with_failures_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_recursive_with_failures_async())

    async def _test_set_access_control_recursive_with_failures_async(self):
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        await root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_async_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        await self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = await directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                      batch_size=2)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    @record
    def test_set_access_control_recursive_in_batches_with_explicit_iteration_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_recursive_in_batches_with_explicit_iteration_async())

    async def _test_set_access_control_recursive_in_batches_with_explicit_iteration_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        result = AccessControlChangeResult(None, "")
        iteration_count = 0
        max_batches = 2
        batch_size = 2

        while result.continuation is not None:
            result = await directory_client.set_access_control_recursive(acl=acl, batch_size=batch_size,
                                                                         max_batches=max_batches,
                                                                         continuation=result.continuation)

            running_tally.directories_successful += result.counters.directories_successful
            running_tally.files_successful += result.counters.files_successful
            running_tally.failure_count += result.counters.failure_count
            iteration_count += 1

        # Assert
        self.assertEqual(running_tally.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(running_tally.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(running_tally.failure_count, 0)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_update_access_control_recursive_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_access_control_recursive_async())

    async def _test_update_access_control_recursive_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = await directory_client.update_access_control_recursive(acl=acl)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_update_access_control_recursive_in_batches_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_access_control_recursive_in_batches_async())

    async def _test_update_access_control_recursive_in_batches_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = await directory_client.update_access_control_recursive(acl=acl, batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_update_access_control_recursive_in_batches_with_progress_callback_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_access_control_recursive_in_batches_with_progress_callback_async())

    async def _test_update_access_control_recursive_in_batches_with_progress_callback_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        last_response = AccessControlChangeResult(None, "")

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count

            last_response.counters = resp.aggregate_counters

        summary = await directory_client.update_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                         batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        access_control = await directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_update_access_control_recursive_with_failures_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_access_control_recursive_with_failures_async())

    async def _test_update_access_control_recursive_with_failures_async(self):
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        await root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_async_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        await self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = await directory_client.update_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                         batch_size=2)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    @record
    def test_update_access_control_recursive_continue_on_failures_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_access_control_recursive_continue_on_failures_async())

    async def _test_update_access_control_recursive_continue_on_failures_async(self):
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        await root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_async_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        await self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.extend(resp.batch_failures)

        summary = await directory_client.update_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                         batch_size=2, continue_on_failure=True)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)
        self.assertIsNone(summary.continuation)

    @record
    def test_remove_access_control_recursive_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_remove_access_control_recursive_async())

    async def _test_remove_access_control_recursive_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        summary = await directory_client.remove_access_control_recursive(acl=REMOVE_ACL)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)

    @record
    def test_remove_access_control_recursive_in_batches_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_remove_access_control_recursive_in_batches_async())

    async def _test_remove_access_control_recursive_in_batches_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        summary = await directory_client.remove_access_control_recursive(acl=REMOVE_ACL, batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)

    @record
    def test_remove_access_control_recursive_in_batches_with_progress_callback_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_remove_access_control_recursive_in_batches_with_progress_callback_async())

    async def _test_remove_access_control_recursive_in_batches_with_progress_callback_async(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        running_tally = AccessControlChangeCounters(0, 0, 0)
        last_response = AccessControlChangeResult(None, "")

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count

            last_response.counters = resp.aggregate_counters

        summary = await directory_client.remove_access_control_recursive(acl=REMOVE_ACL,
                                                                         progress_hook=progress_callback,
                                                                         batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)

    @record
    def test_remove_access_control_recursive_with_failures_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_remove_access_control_recursive_with_failures_async())

    async def _test_remove_access_control_recursive_with_failures_async(self):
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        await root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_async_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        await directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        await self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        await self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        async def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = await directory_client.remove_access_control_recursive(acl=REMOVE_ACL,
                                                                         progress_hook=progress_callback,
                                                                         batch_size=2)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    async def _test_rename_from(self):
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        new_name = "newname"

        new_directory_client = self.dsc.get_directory_client(self.file_system_name, new_name)

        await new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name,
                                                content_settings=content_settings)
        properties = await new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)
        self.assertIsNone(properties.get('content_settings'))

    @record
    def test_rename_from_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from())

    async def _test_rename_from_a_shorter_directory_to_longer_directory(self):
        # TODO: investigate why rename shorter path to a longer one does not work
        pytest.skip("")
        directory_name = self._get_directory_reference()
        await self._create_directory_and_get_directory_client(directory_name="old")

        new_name = "newname"
        new_directory_client = await self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = await new_directory_client.create_sub_directory("newsub")

        await new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name)
        properties = await new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @record
    def test_rename_from_a_shorter_directory_to_longer_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from_a_shorter_directory_to_longer_directory())

    async def _test_rename_from_a_directory_in_another_file_system(self):
        # create a file dir1 under filesystem1
        old_file_system_name = self._get_directory_reference("oldfilesystem")
        old_dir_name = "olddir"
        old_client = self.dsc.get_file_system_client(old_file_system_name)
        if not self.is_playback():
            time.sleep(30)
        await old_client.create_file_system()
        await old_client.create_directory(old_dir_name)

        # create a dir2 under filesystem2
        new_name = "newname"
        if not self.is_playback():
            time.sleep(5)
        new_directory_client = await self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = await new_directory_client.create_sub_directory("newsub")

        # rename dir1 under filesystem1 to dir2 under filesystem2
        await new_directory_client._rename_path('/' + old_file_system_name + '/' + old_dir_name)
        properties = await new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @record
    def test_rename_from_a_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from_a_directory_in_another_file_system())

    async def _test_rename_from_an_unencoded_directory_in_another_file_system(self):
        # create a directory under filesystem1
        old_file_system_name = self._get_directory_reference("oldfilesystem")
        old_dir_name = "old dir"
        old_client = self.dsc.get_file_system_client(old_file_system_name)
        await old_client.create_file_system()
        old_dir_client =await old_client.create_directory(old_dir_name)
        file_name = "oldfile"
        await old_dir_client.create_file(file_name)

        # create a dir2 under filesystem2
        new_name = "new name/sub dir"
        new_file_system_name = self._get_directory_reference("newfilesystem")
        new_file_system_client = self.dsc.get_file_system_client(new_file_system_name)
        await new_file_system_client.create_file_system()
        # the new directory we want to rename to must exist in another file system
        await new_file_system_client.create_directory(new_name)

        # rename dir1 under filesystem1 to dir2 under filesystem2
        new_directory_client = await old_dir_client.rename_directory('/' + new_file_system_name + '/' + new_name)
        properties = await new_directory_client.get_directory_properties()
        file_properties = await new_directory_client.get_file_client(file_name).get_file_properties()

        self.assertIsNotNone(properties)
        self.assertIsNotNone(file_properties)
        await old_client.delete_file_system()

    @record
    def test_rename_from_an_unencoded_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from_an_unencoded_directory_in_another_file_system())

    async def _test_rename_to_an_existing_directory_in_another_file_system(self):
        # create a file dir1 under filesystem1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        destination_dir_name = "destdir"
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        if not self.is_playback():
            time.sleep(30)
        await fs_client.create_file_system()
        destination_directory_client = await fs_client.create_directory(destination_dir_name)

        # create a dir2 under filesystem2
        source_name = "source"
        source_directory_client = await self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = await source_directory_client.create_sub_directory("subdir")

        # rename dir2 under filesystem2 to dir1 under filesystem1
        res = await source_directory_client.rename_directory(
            '/' + destination_file_system_name + '/' + destination_dir_name)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            await source_directory_client.get_directory_properties()

        self.assertEquals(res.url, destination_directory_client.url)

    @record
    def test_rename_to_an_existing_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_to_an_existing_directory_in_another_file_system())

    async def _test_rename_with_none_existing_destination_condition_and_source_unmodified_condition(self):
        non_existing_dir_name = "nonexistingdir"

        # create a filesystem1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        await fs_client.create_file_system()

        # create a dir2 under filesystem2
        source_name = "source"
        source_directory_client = await self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = await source_directory_client.create_sub_directory("subdir")

        # rename dir2 under filesystem2 to a non existing directory under filesystem1,
        # when dir1 does not exist and dir2 wasn't modified
        properties = await source_directory_client.get_directory_properties()
        etag = properties['etag']
        res = await source_directory_client.rename_directory(
            '/' + destination_file_system_name + '/' + non_existing_dir_name,
            match_condition=MatchConditions.IfMissing,
            source_etag=etag,
            source_match_condition=MatchConditions.IfNotModified)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            await source_directory_client.get_directory_properties()

        self.assertEquals(non_existing_dir_name, res.path_name)

    @record
    def test_rename_with_none_existing_destination_condition_and_source_unmodified_condition_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._test_rename_with_none_existing_destination_condition_and_source_unmodified_condition())

    async def _test_rename_to_an_non_existing_directory_in_another_file_system(self):
        # create a file dir1 under filesystem1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        non_existing_dir_name = "nonexistingdir"
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        await fs_client.create_file_system()

        # create a dir2 under filesystem2
        source_name = "source"
        source_directory_client = await self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = await source_directory_client.create_sub_directory("subdir")

        # rename dir2 under filesystem2 to dir1 under filesystem1
        res = await source_directory_client.rename_directory(
            '/' + destination_file_system_name + '/' + non_existing_dir_name)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            await source_directory_client.get_directory_properties()

        self.assertEquals(non_existing_dir_name, res.path_name)

    @record
    def test_rename_to_an_non_existing_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_to_an_non_existing_directory_in_another_file_system())

    async def _test_rename_directory_to_non_empty_directory(self):
        # TODO: investigate why rename non empty dir doesn't work
        pytest.skip("")
        dir1 = await self._create_directory_and_get_directory_client("dir1")
        await dir1.create_sub_directory("subdir")

        dir2 = await self._create_directory_and_get_directory_client("dir2")
        await dir2.rename_directory(dir1.file_system_name + '/' + dir1.path_name)

        with self.assertRaises(HttpResponseError):
            await dir2.get_directory_properties()

    @record
    def test_rename_directory_to_non_empty_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_directory_to_non_empty_directory())

    async def _test_rename_dir_with_file_system_sas(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        token = generate_file_system_sas(
            self.dsc.account_name,
            self.file_system_name,
            self.dsc.credential.account_key,
            FileSystemSasPermissions(write=True, read=True, delete=True, move=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        dir_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, "olddir", credential=token)
        await dir_client.create_directory()
        new_client = await dir_client.rename_directory(dir_client.file_system_name+'/'+'newdir'+'?')

        properties = await new_client.get_directory_properties()
        self.assertEqual(properties.name, "newdir")

    def test_rename_dir_with_file_system_sas_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_dir_with_file_system_sas())

    async def _test_rename_dir_with_file_sas(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        token = generate_directory_sas(self.dsc.account_name,
                                       self.file_system_name,
                                       "olddir",
                                       self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY,
                                       permission=DirectorySasPermissions(read=True, create=True, write=True,
                                                                          delete=True, move=True),
                                       expiry=datetime.utcnow() + timedelta(hours=1),
                                       )

        new_token = generate_directory_sas(self.dsc.account_name,
                                           self.file_system_name,
                                           "newdir",
                                           self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY,
                                           permission=DirectorySasPermissions(read=True, create=True, write=True,
                                                                              delete=True),
                                           expiry=datetime.utcnow() + timedelta(hours=1),
                                           )

        # read the created file which is under root directory
        dir_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, "olddir", credential=token)
        await dir_client.create_directory()
        new_client = await dir_client.rename_directory(dir_client.file_system_name+'/'+'newdir'+'?'+new_token)

        properties = await new_client.get_directory_properties()
        self.assertEqual(properties.name, "newdir")

    def test_rename_dir_with_file_sas_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_dir_with_file_sas())

    async def _test_get_properties(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        properties = await directory_client.get_directory_properties()
        # Assert
        self.assertTrue(properties)
        self.assertIsNotNone(properties.metadata)
        self.assertEqual(properties.metadata['hello'], metadata['hello'])

    @record
    def test_get_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_properties())

    async def _test_using_directory_sas_to_read(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        client = await self._create_directory_and_get_directory_client()
        directory_name = client.path_name

        # generate a token with directory level read permission
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            self.dsc.credential.account_key,
            permission=DirectorySasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        access_control = await directory_client.get_access_control()

        self.assertIsNotNone(access_control)

    @record
    def test_using_directory_sas_to_read_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_using_directory_sas_to_read())

    async def _test_using_directory_sas_to_create(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            self.dsc.credential.account_key,
            permission=DirectorySasPermissions(create=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        response = await directory_client.create_directory()
        self.assertIsNotNone(response)

    @record
    def test_using_directory_sas_to_create_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_using_directory_sas_to_create())


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
