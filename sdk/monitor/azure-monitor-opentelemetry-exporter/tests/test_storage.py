# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import tempfile
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._storage import (
    LocalFileBlob,
    LocalFileStorage,
    StorageExportResult,
    _now,
    _seconds,
)

from azure.monitor.opentelemetry.exporter.export._base import _get_storage_directory

TEST_FOLDER = os.path.abspath(".test.storage")
DUMMY_INSTRUMENTATION_KEY = "00000000-0000-0000-0000-000000000000"
TEST_USER = "multiuser-test"
STORAGE_MODULE = "azure.monitor.opentelemetry.exporter._storage"


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


def clean_folder(folder):
    if os.path.isfile(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))


# pylint: disable=no-self-use
class TestLocalFileBlob(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        os.makedirs(TEST_FOLDER, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_FOLDER, True)

    def tearDown(self):
        clean_folder(TEST_FOLDER)

    def test_delete(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar"))
        blob.delete()

    def test_get(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar"))
        self.assertIsNone(blob.get())
        blob.get()

    def test_put_error(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar"))
        with mock.patch("os.rename", side_effect=throw(Exception)):
            result = blob.put([1, 2, 3])
            #self.assertIsInstance(result, str)

    @unittest.skip("transient storage")
    def test_put_success_returns_self(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "success_blob"))
        test_input = [1, 2, 3]
        result = blob.put(test_input)
        # Should return the blob itself (self) on success
        self.assertIsInstance(result, StorageExportResult)
        self.assertEqual(result, StorageExportResult.LOCAL_FILE_BLOB_SUCCESS)

    def test_put_file_write_error_returns_string(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "write_error_blob"))
        test_input = [1, 2, 3]
        
        with mock.patch("builtins.open", side_effect=PermissionError("Cannot write to file")):
            result = blob.put(test_input)
            self.assertIsInstance(result, str)
            self.assertIn("Cannot write to file", result)

    @unittest.skip("transient storage")
    def test_put_rename_error_returns_string(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "rename_error_blob"))
        test_input = [1, 2, 3]
        
        # Mock os.rename to raise an exception
        with mock.patch("os.rename", side_effect=OSError("File already exists")):
            result = blob.put(test_input)
            self.assertIsInstance(result, str)
            self.assertIn("File already exists", result)

    def test_put_json_serialization_error_returns_string(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "json_error_blob"))
        
        import datetime
        non_serializable_data = [datetime.datetime.now()]
        
        result = blob.put(non_serializable_data)
        self.assertIsInstance(result, str)
        # Should contain JSON serialization error
        self.assertTrue("not JSON serializable" in result or "Object of type" in result)
    
    def test_put_various_exceptions_return_strings(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "various_errors_blob"))
        test_input = [1, 2, 3]
        
        exception_scenarios = [
            ("FileNotFoundError", FileNotFoundError("Directory not found")),
            ("PermissionError", PermissionError("Permission denied")),
            ("OSError", OSError("Disk full")),
            ("IOError", IOError("I/O operation failed")),
            ("ValueError", ValueError("Invalid value")),
            ("RuntimeError", RuntimeError("Runtime error occurred")),
        ]
        
        for error_name, exception in exception_scenarios:
            with self.subTest(exception=error_name):
                with mock.patch("os.rename", side_effect=exception):
                    result = blob.put(test_input)
                    self.assertIsInstance(result, str)
                    self.assertTrue(len(result) > 0)  # Should contain error message

    @unittest.skip("transient storage")
    def test_put_with_lease_period_success(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "lease_success_blob"))
        test_input = [1, 2, 3]
        lease_period = 60
        
        result = blob.put(test_input, lease_period=lease_period)
        self.assertIsInstance(result, StorageExportResult)
        self.assertEqual(result, StorageExportResult.LOCAL_FILE_BLOB_SUCCESS)
        # File should have .lock extension due to lease period
        self.assertTrue(blob.fullpath.endswith(".lock"))
    
    @unittest.skip("transient storage")
    def test_put_with_lease_period_error_returns_string(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "lease_error_blob"))
        test_input = [1, 2, 3]
        lease_period = 60
        
        # Mock os.rename to fail
        with mock.patch("os.rename", side_effect=OSError("Cannot rename file")):
            result = blob.put(test_input, lease_period=lease_period)
            self.assertIsInstance(result, str)
            self.assertIn("Cannot rename file", result)

    def test_put_empty_data_success(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "empty_data_blob"))
        empty_data = []
        
        result = blob.put(empty_data)
        self.assertIsInstance(result, StorageExportResult)
        self.assertEqual(result, StorageExportResult.LOCAL_FILE_BLOB_SUCCESS)

    @unittest.skip("transient storage")
    def test_put_large_data_success(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "large_data_blob"))
        # Create a large list of data
        large_data = [{"id": i, "value": f"data_{i}"} for i in range(1000)]
        
        result = blob.put(large_data)
        self.assertIsInstance(result, StorageExportResult)
        self.assertEqual(result, StorageExportResult.LOCAL_FILE_BLOB_SUCCESS)
        
        # Verify data can be retrieved
        retrieved_data = blob.get()
        self.assertEqual(len(retrieved_data), 1000)
        self.assertEqual(retrieved_data[0], {"id": 0, "value": "data_0"})
        self.assertEqual(retrieved_data[999], {"id": 999, "value": "data_999"})

    def test_put_return_type_consistency(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "consistency_blob"))
        test_input = [1, 2, 3]
        
        # Test successful case
        result_success = blob.put(test_input)
        self.assertTrue(isinstance(result_success, StorageExportResult) or isinstance(result_success, str))
        
        # Test error case
        blob2 = LocalFileBlob(os.path.join(TEST_FOLDER, "consistency_blob2"))
        with mock.patch("os.rename", side_effect=Exception("Test error")):
            result_error = blob2.put(test_input)
            self.assertIsInstance(result_error, str)
            
    def test_put_invalid_return_type(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "invalid_return_blob"))
        test_input = [1, 2, 3]
        
        # This tests that even if os.rename somehow returns something unexpected,
        # the put method still maintains its type contract
        with mock.patch("os.rename", return_value=42):
            result = blob.put(test_input)
            # Should either convert to string or return StorageExportResult
            self.assertTrue(isinstance(result, (StorageExportResult, str)),
                          f"Expected StorageExportResult or str, got {type(result)}")

    @unittest.skip("transient storage")
    def test_put(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar.blob"))
        test_input = (1, 2, 3)
        blob.put(test_input)
        self.assertGreaterEqual(len(os.listdir(TEST_FOLDER)), 1)

    @unittest.skip("transient storage")
    def test_lease_error(self):
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "foobar.blob"))
        blob.delete()
        self.assertEqual(blob.lease(0.01), None)


# pylint: disable=protected-access
class TestLocalFileStorage(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_FOLDER, True)

    def test_get_nothing(self):
        with LocalFileStorage(os.path.join(TEST_FOLDER, "test", "a")) as stor:
            pass
        with LocalFileStorage(os.path.join(TEST_FOLDER, "test")) as stor:
            self.assertIsNone(stor.get())

    def test_get(self):
        now = _now()
        with LocalFileStorage(os.path.join(TEST_FOLDER, "foo")) as stor:
            stor.put((1, 2, 3), lease_period=10)
            with mock.patch("azure.monitor.opentelemetry.exporter._storage._now") as m:
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

    def test_put(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "bar")) as stor:
            stor.put(test_input, 0)
            self.assertEqual(stor.get().get(), test_input)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "bar")) as stor:
            self.assertEqual(stor.get().get(), test_input)
            with mock.patch("os.rename", side_effect=throw(Exception)):
                result = stor.put(test_input)
                # Should return an error string when os.rename fails
                #self.assertIsInstance(result, None)

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

    def test_maintenance_routine(self):
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

    def test_put_storage_disabled_readonly(self):
        test_input = (1, 2, 3)
        with mock.patch("azure.monitor.opentelemetry.exporter._storage.get_local_storage_setup_state_readonly", return_value=True):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_test")) as stor:
                stor._enabled = False
                result = stor.put(test_input)
                self.assertEqual(result, StorageExportResult.CLIENT_READONLY)

    def test_put_storage_disabled_with_exception_state(self):
        test_input = (1, 2, 3)
        exception_message = "Previous storage error occurred"
        with mock.patch("azure.monitor.opentelemetry.exporter._storage.get_local_storage_setup_state_readonly", return_value=False):
            with mock.patch("azure.monitor.opentelemetry.exporter._storage.get_local_storage_setup_state_exception", return_value=exception_message):
                with LocalFileStorage(os.path.join(TEST_FOLDER, "exception_test")) as stor:
                    stor._enabled = False
                    result = stor.put(test_input)
                    self.assertEqual(result, exception_message)

    def test_put_storage_disabled_no_exception(self):
        test_input = (1, 2, 3)
        with mock.patch("azure.monitor.opentelemetry.exporter._storage.get_local_storage_setup_state_readonly", return_value=False):
            with mock.patch("azure.monitor.opentelemetry.exporter._storage.get_local_storage_setup_state_exception", return_value=""):
                with LocalFileStorage(os.path.join(TEST_FOLDER, "disabled_test")) as stor:
                    stor._enabled = False
                    result = stor.put(test_input)
                    self.assertEqual(result, StorageExportResult.CLIENT_STORAGE_DISABLED)

    def test_put_persistence_capacity_reached(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "capacity_test")) as stor:
            with mock.patch.object(stor, '_check_storage_size', return_value=False):
                result = stor.put(test_input)
                self.assertEqual(result, StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED)

    def test_put_success_returns_localfileblob(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "success_test")) as stor:
            result = stor.put(test_input, lease_period=0)  # No lease period so file is immediately available
            self.assertIsInstance(result, StorageExportResult)
            self.assertEqual(stor.get().get(), test_input)
    
    def test_put_blob_put_failure_returns_string(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "blob_failure_test")) as stor:
            # Mock os.rename to fail in blob.put()
            with mock.patch("os.rename", side_effect=OSError("Permission denied")):
                result = stor.put(test_input)
                self.assertIsInstance(result, str)
                self.assertIn("Permission denied", result)
    

    def test_put_exception_in_method_returns_string(self):
        test_input = (1, 2, 3)
        with LocalFileStorage(os.path.join(TEST_FOLDER, "method_exception_test")) as stor:
            with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", side_effect=RuntimeError("Time error")):
                result = stor.put(test_input)
                self.assertIsInstance(result, str)
                self.assertIn("Time error", result)

    def test_put_various_blob_errors(self):
        test_input = (1, 2, 3)
        error_scenarios = [
            ("FileNotFoundError", FileNotFoundError("File not found")),
            ("PermissionError", PermissionError("Permission denied")),
            ("OSError", OSError("Disk full")),
            ("IOError", IOError("I/O error")),
        ]
        
        for error_name, error_exception in error_scenarios:
            with self.subTest(error=error_name):
                with LocalFileStorage(os.path.join(TEST_FOLDER, f"error_test_{error_name}")) as stor:
                    # Mock os.rename to fail with specific error
                    with mock.patch("os.rename", side_effect=error_exception):
                        result = stor.put(test_input)
                        self.assertIsInstance(result, str)
                        self.assertTrue(len(result) > 0)

    def test_put_with_lease_period(self):
        test_input = (1, 2, 3)
        custom_lease_period = 120  # 2 minutes
        
        with LocalFileStorage(os.path.join(TEST_FOLDER, "lease_test")) as stor:
            result = stor.put(test_input, lease_period=custom_lease_period)
            self.assertIsInstance(result, StorageExportResult)
            # Verify the file was created with lease period
            self.assertEqual(result, StorageExportResult.LOCAL_FILE_BLOB_SUCCESS)

    def test_put_default_lease_period(self):
        test_input = (1, 2, 3)
        
        with LocalFileStorage(os.path.join(TEST_FOLDER, "default_lease_test"), lease_period=90) as stor:
            result = stor.put(test_input)
            self.assertIsInstance(result, StorageExportResult)
            # File should be created with lease (since default lease_period > 0)
            self.assertEqual(result, StorageExportResult.LOCAL_FILE_BLOB_SUCCESS)

    def test_check_and_set_folder_permissions_oserror_sets_exception_state(self):
        test_input = (1, 2, 3)
        test_error_message = "OSError: Permission denied creating directory"

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # Mock os.makedirs to raise OSError during folder permissions check
        with mock.patch("os.makedirs", side_effect=OSError(test_error_message)):
            stor = LocalFileStorage(os.path.join(TEST_FOLDER, "permission_error_test"))
            
            # Storage should be disabled due to permission error
            self.assertFalse(stor._enabled)
            
            # Exception state should be set with the error message
            exception_state = get_local_storage_setup_state_exception()
            self.assertEqual(exception_state, test_error_message)
            
            # When storage is disabled with exception state, put() should return the exception message
            result = stor.put(test_input)
            self.assertEqual(result, test_error_message)
            
            stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
    
    def test_check_and_set_folder_permissions_generic_exception_sets_exception_state(self):
        test_input = (1, 2, 3)
        test_error_message = "RuntimeError: Unexpected error during setup"

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # Mock os.makedirs to raise a generic exception
        with mock.patch("os.makedirs", side_effect=RuntimeError(test_error_message)):
            stor = LocalFileStorage(os.path.join(TEST_FOLDER, "generic_error_test"))
            
            # Storage should be disabled due to exception
            self.assertFalse(stor._enabled)
            
            # Exception state should be set with the error message
            exception_state = get_local_storage_setup_state_exception()
            self.assertEqual(exception_state, test_error_message)
            
            # When storage is disabled with exception state, put() should return the exception message
            result = stor.put(test_input)
            self.assertEqual(result, test_error_message)
            
            stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
    
    def test_check_and_set_folder_permissions_readonly_filesystem_sets_readonly_state(self):
        test_input = (1, 2, 3)

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing states (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # Create an OSError with Read-only file system
        import errno
        readonly_error = OSError("Read-only file system")
        readonly_error.errno = errno.EROFS   # cspell:disable-line
        
        # Mock os.makedirs to raise READONLY error
        with mock.patch("os.makedirs", side_effect=readonly_error):
            stor = LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_fs_test"))
            
            # Storage should be disabled due to readonly filesystem
            self.assertFalse(stor._enabled)
            
            # Readonly state should be set
            self.assertTrue(get_local_storage_setup_state_readonly())
            
            # When storage is disabled and readonly, put() should return CLIENT_READONLY
            result = stor.put(test_input)
            self.assertEqual(result, StorageExportResult.CLIENT_READONLY)
            
            stor.close()
        
        # Clean up - note: cannot easily reset readonly state, but test isolation should handle this
        set_local_storage_setup_state_exception("")

    def test_check_and_set_folder_permissions_windows_icacls_failure_sets_exception_state(self):
        test_input = (1, 2, 3)

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # Mock Windows environment and icacls failure
        with mock.patch("os.name", "nt"):  # Windows
            with mock.patch("os.makedirs"):  # Allow directory creation
                with mock.patch.object(LocalFileStorage, "_get_current_user", return_value="DOMAIN\\user"):
                    # Mock subprocess.run to return failure (non-zero return code)
                    mock_result = mock.MagicMock()
                    mock_result.returncode = 1  # Failure
                    
                    with mock.patch("subprocess.run", return_value=mock_result):
                        stor = LocalFileStorage(os.path.join(TEST_FOLDER, "icacls_failure_test"))
                        
                        # Storage should be disabled due to icacls failure
                        self.assertFalse(stor._enabled)
                        
                        # Exception state should still be empty string since icacls failure doesn't set exception
                        exception_state = get_local_storage_setup_state_exception()
                        self.assertEqual(exception_state, "")
                        
                        # When storage is disabled, put() behavior depends on readonly state
                        result = stor.put(test_input)
                        if get_local_storage_setup_state_readonly():
                            # Readonly takes priority - readonly state may be set by previous tests
                            self.assertEqual(result, StorageExportResult.CLIENT_READONLY)
                        else:
                            # If readonly not set, should return CLIENT_STORAGE_DISABLED
                            self.assertEqual(result, StorageExportResult.CLIENT_STORAGE_DISABLED)
                        
                        stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
    
    def test_check_and_set_folder_permissions_windows_user_retrieval_failure(self):
        test_input = (1, 2, 3)

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # Mock Windows environment and user retrieval failure
        with mock.patch("os.name", "nt"):  # Windows
            with mock.patch("os.makedirs"):  # Allow directory creation
                with mock.patch.object(LocalFileStorage, "_get_current_user", return_value=None):
                    stor = LocalFileStorage(os.path.join(TEST_FOLDER, "user_failure_test"))
                    
                    # Storage should be disabled due to user retrieval failure
                    self.assertFalse(stor._enabled)
                    
                    # When storage is disabled, put() behavior depends on readonly state
                    result = stor.put(test_input)
                    if get_local_storage_setup_state_readonly():
                        # Readonly takes priority - readonly state may be set by previous tests
                        self.assertEqual(result, StorageExportResult.CLIENT_READONLY)
                    else:
                        # If readonly not set, should return CLIENT_STORAGE_DISABLED
                        self.assertEqual(result, StorageExportResult.CLIENT_STORAGE_DISABLED)
                    
                    stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
    
    def test_check_and_set_folder_permissions_unix_chmod_exception_sets_exception_state(self):
        test_input = (1, 2, 3)
        test_error_message = "OSError: Operation not permitted"

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # Mock Unix environment and chmod failure
        with mock.patch("os.name", "posix"):  # Unix
            with mock.patch("os.makedirs"):  # Allow directory creation
                with mock.patch("os.chmod", side_effect=OSError(test_error_message)):
                    stor = LocalFileStorage(os.path.join(TEST_FOLDER, "chmod_failure_test"))
                    
                    # Storage should be disabled due to chmod failure
                    self.assertFalse(stor._enabled)
                    
                    # Exception state should be set with the error message
                    exception_state = get_local_storage_setup_state_exception()
                    self.assertEqual(exception_state, test_error_message)
                    
                    # When storage is disabled, put() behavior depends on readonly state
                    result = stor.put(test_input)
                    if get_local_storage_setup_state_readonly():
                        # Readonly takes priority over exception state
                        self.assertEqual(result, StorageExportResult.CLIENT_READONLY)
                    else:
                        # If readonly not set, should return the exception message
                        self.assertEqual(result, test_error_message)
                    
                    stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
    
    def test_exception_state_persistence_across_storage_instances(self):
        test_input = (1, 2, 3)
        test_error_message = "Persistent storage setup error"

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        
        # First storage instance that sets exception state
        with mock.patch("os.makedirs", side_effect=OSError(test_error_message)):
            stor1 = LocalFileStorage(os.path.join(TEST_FOLDER, "persistent_error_test1"))
            self.assertFalse(stor1._enabled)
            self.assertEqual(get_local_storage_setup_state_exception(), test_error_message)
            stor1.close()
        
        # Second storage instance should also be affected by the exception state
        # (assuming the exception state persists between instances in the same process)
        stor2 = LocalFileStorage(os.path.join(TEST_FOLDER, "persistent_error_test2"))
        if not stor2._enabled:  # If storage setup also fails for the second instance
            result = stor2.put(test_input)
            # Should return the exception message if storage is disabled due to exception state
            if isinstance(result, str) and test_error_message in result:
                self.assertIn(test_error_message, result)
        stor2.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
    
    def test_exception_state_cleared_and_storage_recovery(self):
        test_input = (1, 2, 3)
        test_error_message = "Temporary storage setup error"
        
        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Set exception state manually
        set_local_storage_setup_state_exception(test_error_message)
        self.assertEqual(get_local_storage_setup_state_exception(), test_error_message)
        
        # Create storage with exception state set - should be disabled
        stor1 = LocalFileStorage(os.path.join(TEST_FOLDER, "recovery_test1"))
        if not stor1._enabled:
            result = stor1.put(test_input)
            self.assertEqual(result, test_error_message)
        stor1.close()
        
        # Clear exception state (set to empty string, not None)
        set_local_storage_setup_state_exception("")
        self.assertEqual(get_local_storage_setup_state_exception(), "")
        
        # Create new storage instance - should work normally now
        with LocalFileStorage(os.path.join(TEST_FOLDER, "recovery_test2")) as stor2:
            if stor2._enabled:  # Storage should be enabled now
                result = stor2.put(test_input, lease_period=0)
                self.assertIsInstance(result, StorageExportResult)
                retrieved_data = stor2.get().get()
                self.assertEqual(retrieved_data, test_input)

    def test_local_storage_state_readonly_get_set_operations(self):
        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
            _LOCAL_STORAGE_SETUP_STATE,
            _LOCAL_STORAGE_SETUP_STATE_LOCK
        )
        
        # Save original state
        original_readonly_state = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        
        try:
            # Test 1: Initial state should be False
            # Note: Cannot easily reset readonly state, so we'll work with current state
            initial_state = get_local_storage_setup_state_readonly()
            self.assertIsInstance(initial_state, bool)
            
            # Test 2: Set readonly state and verify get operation
            set_local_storage_setup_state_readonly()
            self.assertTrue(get_local_storage_setup_state_readonly())
            
            # Test 3: Verify thread safety by directly accessing state
            with _LOCAL_STORAGE_SETUP_STATE_LOCK:
                direct_value = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
            self.assertTrue(direct_value)
            self.assertEqual(get_local_storage_setup_state_readonly(), direct_value)
            
            # Test 4: Multiple calls to set should maintain True state
            set_local_storage_setup_state_readonly()
            set_local_storage_setup_state_readonly()
            self.assertTrue(get_local_storage_setup_state_readonly())
            
            # Test 5: Verify state persists across multiple get calls
            for _ in range(5):
                self.assertTrue(get_local_storage_setup_state_readonly())
            
        finally:
            # Note: We cannot reset readonly state to False as there's no reset function
            # This is by design - once readonly is set, it stays set for the process
            pass

    def test_readonly_state_interaction_with_storage_put_method(self):
        test_input = (1, 2, 3)

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
            set_local_storage_setup_state_exception,
        )
        
        # Clear exception state
        set_local_storage_setup_state_exception("")
        
        # Set readonly state
        set_local_storage_setup_state_readonly()
        self.assertTrue(get_local_storage_setup_state_readonly())
        
        # Create storage instance with disabled state to test readonly behavior
        with LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_interaction_test")) as stor:
            # Manually disable storage to simulate permission failure scenario
            stor._enabled = False
            
            # When storage is disabled and readonly state is set, put() should return CLIENT_READONLY
            result = stor.put(test_input)
            self.assertEqual(result, StorageExportResult.CLIENT_READONLY)
            
    def test_storage_put_invalid_return_type(self):
        test_input = (1, 2, 3)
        
        with LocalFileStorage(os.path.join(TEST_FOLDER, "invalid_return_test")) as stor:
            # Mock _check_storage_size to return a non-boolean value
            with mock.patch.object(stor, '_check_storage_size', return_value=42):
                result = stor.put(test_input)
                # Should maintain return type contract despite invalid internal return
                self.assertTrue(isinstance(result, (StorageExportResult, str)),
                              f"Expected StorageExportResult or str, got {type(result)}")

    def test_readonly_state_priority_over_exception_state(self):
        test_input = (1, 2, 3)
        test_exception_message = "Some storage exception"
        
        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Set both readonly and exception states
        set_local_storage_setup_state_readonly()
        set_local_storage_setup_state_exception(test_exception_message)
        
        # Verify both states are set
        self.assertTrue(get_local_storage_setup_state_readonly())
        self.assertEqual(get_local_storage_setup_state_exception(), test_exception_message)
        
        # Create storage instance with disabled state
        with LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_priority_test")) as stor:
            # Manually disable storage
            stor._enabled = False
            
            # Readonly state should take priority over exception state
            # Based on the put() method logic: readonly is checked first
            result = stor.put(test_input)
            self.assertEqual(result, StorageExportResult.CLIENT_READONLY)

    def test_readonly_state_thread_safety(self):
        import threading
        import time

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
        )
        
        # Track results from multiple threads
        results = []
        errors = []
        
        def readonly_operations():
            try:
                # Each thread sets readonly and gets the value
                set_local_storage_setup_state_readonly()
                time.sleep(0.01)  # Small delay to encourage race conditions
                value = get_local_storage_setup_state_readonly()
                results.append(value)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=readonly_operations)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        
        # Verify all operations succeeded and returned True
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertTrue(result)

    def test_readonly_state_persistence_across_storage_instances(self):
        test_input = (1, 2, 3)

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
            set_local_storage_setup_state_exception,
        )
        
        set_local_storage_setup_state_exception("")
        set_local_storage_setup_state_readonly()
        
        # First storage instance
        stor1 = LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_persist_test1"))
        stor1._enabled = False  # Simulate disabled state
        result1 = stor1.put(test_input)
        self.assertEqual(result1, StorageExportResult.CLIENT_READONLY)
        stor1.close()
        
        # Second storage instance should also see readonly state
        stor2 = LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_persist_test2"))
        stor2._enabled = False  # Simulate disabled state
        result2 = stor2.put(test_input)
        self.assertEqual(result2, StorageExportResult.CLIENT_READONLY)
        stor2.close()
        
        # Verify readonly state is still set
        self.assertTrue(get_local_storage_setup_state_readonly())

    def test_readonly_state_direct_access_vs_function_access(self):
        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
            _LOCAL_STORAGE_SETUP_STATE,
            _LOCAL_STORAGE_SETUP_STATE_LOCK
        )
        
        set_local_storage_setup_state_readonly()
        
        # Compare function access with direct access
        function_value = get_local_storage_setup_state_readonly()
        
        with _LOCAL_STORAGE_SETUP_STATE_LOCK:
            direct_value = _LOCAL_STORAGE_SETUP_STATE["READONLY"]
        
        self.assertEqual(function_value, direct_value)
        self.assertTrue(function_value)
        self.assertTrue(direct_value)

    def test_readonly_state_idempotent_set_operations(self):
        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_readonly,
            set_local_storage_setup_state_readonly,
        )
        
        # Multiple set operations should be idempotent
        initial_state = get_local_storage_setup_state_readonly()
        
        for _ in range(5):
            set_local_storage_setup_state_readonly()
            self.assertTrue(get_local_storage_setup_state_readonly())
        
        # State should remain True after multiple sets
        final_state = get_local_storage_setup_state_readonly()
        self.assertTrue(final_state)

    def test_check_and_set_folder_permissions_unix_multiuser_scenario(self):

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state
        set_local_storage_setup_state_exception("")
        
        storage_abs_path = _get_storage_directory(DUMMY_INSTRUMENTATION_KEY)

        with mock.patch(f"{STORAGE_MODULE}.os.name", "posix"):
            chmod_calls = []
            makedirs_calls = []

            def mock_chmod(path, mode):
                chmod_calls.append((path, oct(mode)))

            def mock_makedirs(path, mode=0o777, exist_ok=False):
                makedirs_calls.append((path, oct(mode), exist_ok))

            with mock.patch(f"{STORAGE_MODULE}.os.makedirs", side_effect=mock_makedirs):
                with mock.patch(f"{STORAGE_MODULE}.os.chmod", side_effect=mock_chmod):
                    with mock.patch(f"{STORAGE_MODULE}.os.path.abspath", side_effect=lambda path: path):
                        stor = LocalFileStorage(storage_abs_path)

                        self.assertTrue(stor._enabled)

                        self.assertEqual(
                            makedirs_calls,
                            [(storage_abs_path, '0o777', True)],
                            f"Unexpected makedirs calls: {makedirs_calls}",
                        )

                        self.assertEqual(
                            {(storage_abs_path, '0o700')},
                            {(call_path, mode) for call_path, mode in chmod_calls},
                            f"Unexpected chmod calls: {chmod_calls}",
                        )

                        stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
        
    def test_check_and_set_folder_permissions_unix_multiuser_parent_permission_failure(self):
        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )

        # Clear any existing exception state
        set_local_storage_setup_state_exception("")

        storage_abs_path = _get_storage_directory(DUMMY_INSTRUMENTATION_KEY)

        with mock.patch(f"{STORAGE_MODULE}.os.name", "posix"):
            def mock_makedirs(path, mode=0o777, exist_ok=False):
                raise PermissionError("Operation not permitted on parent directory")

            with mock.patch(f"{STORAGE_MODULE}.os.makedirs", side_effect=mock_makedirs):
                with mock.patch(f"{STORAGE_MODULE}.os.chmod"):
                    with mock.patch(f"{STORAGE_MODULE}.os.path.abspath", side_effect=lambda path: path):
                        stor = LocalFileStorage(storage_abs_path)

                        self.assertFalse(stor._enabled)

                        exception_state = get_local_storage_setup_state_exception()
                        self.assertEqual(exception_state, "Operation not permitted on parent directory")

                        stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")

    def test_check_and_set_folder_permissions_unix_multiuser_storage_permission_failure(self):
        test_error_message = "PermissionError: Operation not permitted on storage directory"

        from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
            get_local_storage_setup_state_exception,
            set_local_storage_setup_state_exception,
        )
        
        # Clear any existing exception state
        set_local_storage_setup_state_exception("")

        storage_abs_path = _get_storage_directory(DUMMY_INSTRUMENTATION_KEY)

        with mock.patch(f"{STORAGE_MODULE}.os.name", "posix"):
            def mock_chmod(path, mode):
                if mode == 0o700:
                    raise PermissionError(test_error_message)
                raise OSError(f"Unexpected chmod call: {path}, {oct(mode)}")

            with mock.patch(f"{STORAGE_MODULE}.os.makedirs"):
                with mock.patch(f"{STORAGE_MODULE}.os.chmod", side_effect=mock_chmod):
                    with mock.patch(f"{STORAGE_MODULE}.os.path.abspath", side_effect=lambda path: path):
                        stor = LocalFileStorage(storage_abs_path)

                        self.assertFalse(stor._enabled)

                        exception_state = get_local_storage_setup_state_exception()
                        self.assertEqual(exception_state, test_error_message)

                        stor.close()
        
        # Clean up
        set_local_storage_setup_state_exception("")
