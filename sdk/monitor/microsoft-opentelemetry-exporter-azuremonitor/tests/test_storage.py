# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import unittest
from unittest import mock

from microsoft.opentelemetry.exporter.azuremonitor.storage import (
    LocalFileBlob,
    LocalFileStorage,
    _now,
    _seconds,
)

TEST_FOLDER = os.path.abspath(".test")

def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=no-self-use
class TestLocalFileBlob(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        os.makedirs(TEST_FOLDER, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_FOLDER, True)

    def test_delete(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar"))
        blob.delete()
        blob.delete()

    def test_get(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar"))
        self.assertIsNone(blob.get())
        blob.get()

    def test_put_error(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar"))
        with mock.patch("os.rename", side_effect=throw(Exception)):
            blob.put([1, 2, 3])

    def test_put_without_lease(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar.blob"))
        test_input = (1, 2, 3)
        blob.delete()
        blob.put(test_input)
        self.assertEqual(blob.get(), test_input)

    def test_put_with_lease(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar.blob"))
        test_input = (1, 2, 3)
        blob.delete()
        blob.put(test_input, lease_period=0.01)
        blob.lease(0.01)
        self.assertEqual(blob.get(), test_input)

    def test_lease_error(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar.blob"))
        blob.delete()
        self.assertEqual(blob.lease(0.01), None)


# pylint: disable=protected-access
class TestLocalFileStorage(unittest.TestCase):
    def test_get_nothing(self):
        with LocalFileStorage(os.path.join(TEST_FOLDER, "test", "a")) as stor:
            pass
        with LocalFileStorage(os.path.join(TEST_FOLDER, "test")) as stor:
            self.assertIsNone(stor.get())

    def test_get(self):
        now = _now()
        with LocalFileStorage(os.path.join(TEST_FOLDER, "foo")) as stor:
            stor.put((1, 2, 3), lease_period=10)
            with mock.patch("microsoft.opentelemetry.exporter.azuremonitor.storage._now") as m:
                m.return_value = now - _seconds(30 * 24 * 60 * 60)
                stor.put((1, 2, 3))
                stor.put((1, 2, 3), lease_period=10)
                with mock.patch("os.rename"):
                    stor.put((1, 2, 3))
            with mock.patch("os.rename"):
                stor.put((1, 2, 3))
            with mock.patch("os.remove", side_effect=throw(Exception)):
                with mock.patch("os.rename", side_effect=throw(Exception)):
                    self.assertIsNone(stor.get())
            self.assertIsNone(stor.get())

    # def test_put(self):
    #     test_input = (1, 2, 3)
    #     with LocalFileStorage(os.path.join(TEST_FOLDER, "bar")) as stor:
    #         stor.put(test_input)
    #         self.assertEqual(stor.get().get(), test_input)
    #     with LocalFileStorage(os.path.join(TEST_FOLDER, "bar")) as stor:
    #         self.assertEqual(stor.get().get(), test_input)
    #         with mock.patch("os.rename", side_effect=throw(Exception)):
    #             self.assertIsNone(stor.put(test_input))

    def test_put_max_size(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "asd")) as stor:
            size_mock = mock.Mock()
            size_mock.return_value = False
            stor._check_storage_size = size_mock
            stor.put(test_input)
            self.assertEqual(stor.get(), None)

    def test_check_storage_size_full(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "asd2"), 1) as stor:
            stor.put(test_input)
            self.assertFalse(stor._check_storage_size())

    def test_check_storage_size_not_full(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "asd3"), 1000) as stor:
            stor.put(test_input)
            self.assertTrue(stor._check_storage_size())

    def test_check_storage_size_no_files(self):
        with LocalFileStorage(os.path.join(TEST_FOLDER, "asd3"), 1000) as stor:
            self.assertTrue(stor._check_storage_size())

    def test_check_storage_size_links(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "asd4"), 1000) as stor:
            stor.put(test_input)
            with mock.patch("os.path.islink") as os_mock:
                os_mock.return_value = True
            self.assertTrue(stor._check_storage_size())

    def test_check_storage_size_error(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "asd5"), 1) as stor:
            with mock.patch("os.path.getsize", side_effect=throw(OSError)):
                stor.put(test_input)
                with mock.patch("os.path.islink") as os_mock:
                    os_mock.return_value = True
                self.assertTrue(stor._check_storage_size())

    def test_maintanence_routine(self):
        with mock.patch("os.makedirs") as m:
            with LocalFileStorage(os.path.join(TEST_FOLDER, "baz")) as stor:
                m.return_value = None
        with mock.patch("os.makedirs", side_effect=throw(Exception)):
            stor = LocalFileStorage(os.path.join(TEST_FOLDER, "baz"))
            stor.close()
        with mock.patch("os.listdir", side_effect=throw(Exception)):
            stor = LocalFileStorage(os.path.join(TEST_FOLDER, "baz"))
            stor.close()
        with LocalFileStorage(os.path.join(TEST_FOLDER, "baz")) as stor:
            with mock.patch("os.listdir", side_effect=throw(Exception)):
                stor._maintenance_routine()
            with mock.patch("os.path.isdir", side_effect=throw(Exception)):
                stor._maintenance_routine()
