# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import asyncio

from azure.core.exceptions import ResourceNotFoundError

from azure.core import MatchConditions
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.filedatalake.aio import DataLakeServiceClient
from azure.storage.filedatalake import PublicAccess
from testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
TEST_FILE_SYSTEM_PREFIX = 'filesystem'


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


class FileSystemTest(StorageTestCase):
    def setUp(self):
        super(FileSystemTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY,
                                         transport=AiohttpTestTransport())
        self.config = self.dsc._config
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dsc.__aenter__())
        self.test_file_systems = []

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                for file_system in self.test_file_systems:
                    loop.run_until_complete(self.dsc.delete_file_system(file_system))
                loop.run_until_complete(self.fsc.__aexit__())
            except:
                pass

        return super(FileSystemTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_file_system_reference(self, prefix=TEST_FILE_SYSTEM_PREFIX):
        file_system_name = self.get_resource_name(prefix)
        self.test_file_systems.append(file_system_name)
        return file_system_name

    async def _create_file_system(self, file_system_prefix=TEST_FILE_SYSTEM_PREFIX):
        return await self.dsc.create_file_system(self._get_file_system_reference(prefix=file_system_prefix))

    # --Helpers-----------------------------------------------------------------

    async def _test_create_file_system_async(self):
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = await file_system_client.create_file_system()

        # Assert
        self.assertTrue(created)

    @record
    def test_create_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_system_async())

    async def _test_create_file_system_with_metadata_async(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = await file_system_client.create_file_system(metadata=metadata)

        # Assert
        properties = await file_system_client.get_file_system_properties()
        self.assertTrue(created)
        self.assertDictEqual(properties.metadata, metadata)

    @record
    def test_create_file_system_with_metadata_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_system_with_metadata_async())

    async def _test_list_file_systems_async(self):
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = await self.dsc.create_file_system(file_system_name)

        # Act
        file_systems = []
        async for filesystem in self.dsc.list_file_systems():
            file_systems.append(filesystem)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertIsNotNone(file_systems[0].has_immutability_policy)
        self.assertIsNotNone(file_systems[0].has_legal_hold)

    @record
    def test_list_file_systems_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_file_systems_async())

    async def _test_delete_file_system_with_existing_file_system_async(self):
        # Arrange
        file_system = await self._create_file_system()

        # Act
        deleted = await file_system.delete_file_system()

        # Assert
        self.assertIsNone(deleted)

    @record
    def test_delete_file_system_with_existing_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_file_system_with_existing_file_system_async())

    async def _test_delete_none_existing_file_system_async(self):
        fake_file_system_client = self.dsc.get_file_system_client("fakeclient")

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await fake_file_system_client.delete_file_system(match_condition=MatchConditions.IfMissing)

    @record
    def test_delete_none_existing_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_none_existing_file_system_async())

    async def _test_list_file_systems_with_include_metadata_async(self):
        # Arrange
        file_system = await self._create_file_system()
        metadata = {'hello': 'world', 'number': '42'}
        await file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = []
        async for fs in self.dsc.list_file_systems(name_starts_with=file_system.file_system_name,
                                                   include_metadata=True):
            file_systems.append(fs)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertDictEqual(file_systems[0].metadata, metadata)

    @record
    def test_list_file_systems_with_include_metadata_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_file_systems_with_include_metadata_async())

    async def _test_list_file_systems_by_page_async(self):
        # Arrange
        for i in range(0, 6):
            await self._create_file_system(file_system_prefix="filesystem{}".format(i))

        # Act
        file_systems = []
        async for fs in await self.dsc.list_file_systems(
                results_per_page=3,
                name_starts_with="file",
                include_metadata=True).by_page().__anext__():
            file_systems.append(fs)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 3)

    @record
    def test_list_file_systems_by_page_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_file_systems_by_page_async())

    async def _test_list_file_systems_with_public_access_async(self):
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.get_file_system_client(file_system_name)
        await file_system.create_file_system(public_access="blob")
        metadata = {'hello': 'world', 'number': '42'}
        await file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = []
        async for fs in self.dsc.list_file_systems(name_starts_with=file_system.file_system_name,
                                                   include_metadata=True):
            file_systems.append(fs)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertDictEqual(file_systems[0].metadata, metadata)
        self.assertTrue(file_systems[0].public_access is PublicAccess.File)

    @record
    def test_list_file_systems_with_public_access_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_file_systems_with_public_access_async())

    async def _test_get_file_system_properties_async(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system = await self._create_file_system()
        await file_system.set_file_system_metadata(metadata)

        # Act
        props = await file_system.get_file_system_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        self.assertIsNotNone(props.has_immutability_policy)
        self.assertIsNotNone(props.has_legal_hold)

    @record
    def test_get_file_system_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_system_properties_async())

    async def _test_list_paths_async(self):
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))

        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        self.assertEqual(len(paths), 6)

    @record
    def test_list_paths_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_paths_async())

    async def _test_list_paths_which_are_all_files_async(self):
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_file("file{}".format(i))

        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        self.assertEqual(len(paths), 6)

    @record
    def test_list_paths_which_are_all_files_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_paths_which_are_all_files_async())

    async def _test_list_paths_with_max_per_page_async(self):
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))

        generator1 = file_system.get_paths(max_results=2, upn=True).by_page()
        paths1 = []
        async for path in await generator1.__anext__():
            paths1.append(path)

        generator2 = file_system.get_paths(max_results=4, upn=True) \
            .by_page(continuation_token=generator1.continuation_token)
        paths2 = []
        async for path in await generator2.__anext__():
            paths2.append(path)

        self.assertEqual(len(paths1), 2)
        self.assertEqual(len(paths2), 4)

    @record
    def test_list_paths_with_max_per_page_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_paths_with_max_per_page_async())

    async def _test_list_paths_under_specific_path_async(self):
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            dir = await file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = await dir.create_sub_directory("subdir")
            await subdir.create_sub_directory("subsub")

            # create a file under the current directory
            file_client = await subdir.create_file("file")
            await file_client.append_data(b"abced", 0, 5)
            await file_client.flush_data(5)

        generator1 = file_system.get_paths(path="dir10/subdir", max_results=2, upn=True).by_page()
        paths = []
        async for path in await generator1.__anext__():
            paths.append(path)

        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0].content_length, 5)

    @record
    def test_list_paths_under_specific_path_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_paths_under_specific_path_async())

    async def _test_list_paths_recursively_async(self):
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            dir = await file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = await dir.create_sub_directory("subdir")
            await subdir.create_sub_directory("subsub")

            # create a file under the current directory
            await subdir.create_file("file")

        paths = []
        async for path in file_system.get_paths(recursive=True, upn=True):
            paths.append(path)

        # there are 24 subpaths in total
        self.assertEqual(len(paths), 24)

    @record
    def test_list_paths_recursively_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_paths_recursively_async())

    async def _test_create_directory_from_file_system_client_async(self):
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_directory("dir1/dir2")

        paths = []
        async for path in file_system.get_paths(recursive=False, upn=True):
            paths.append(path)

        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].name, "dir1")

    @record
    def test_create_directory_from_file_system_client_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_from_file_system_client_async())

    async def _test_create_file_from_file_system_client_async(self):
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_file("dir1/dir2/file")

        paths = []
        async for path in file_system.get_paths(recursive=True, upn=True):
            paths.append(path)
        self.assertEqual(len(paths), 3)
        self.assertEqual(paths[0].name, "dir1")
        self.assertEqual(paths[2].is_directory, False)

    @record
    def test_create_file_from_file_system_client_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_from_file_system_client_async())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
