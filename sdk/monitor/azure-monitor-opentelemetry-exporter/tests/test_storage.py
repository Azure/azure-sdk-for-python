# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import shutil
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._storage import (
    LocalFileBlob,
    LocalFileStorage,
    _now,
    _seconds,
)
from azure.monitor.opentelemetry.exporter._constants import DropCode
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter.statsbeat._utils import _track_dropped_items

TEST_FOLDER = os.path.abspath(".test.storage")


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
            blob.put([1, 2, 3])

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

    def test_put_with_customer_statsbeat_success(self):
        """Test that LocalFileBlob.put() doesn't track dropped items when successful"""
        mock_statsbeat = mock.Mock()
        test_data = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
            {"name": "test_item2", "data": {"base_type": "ExceptionData"}},
        ]
        
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "success_blob"), mock_statsbeat)
        
        # Mock the file operations to succeed
        with mock.patch("builtins.open", mock.mock_open()):
            with mock.patch("os.rename"):
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    result = blob.put(test_data)
                    
                    # Should return the blob object on success
                    self.assertEqual(result, blob)
                    # Should not track any dropped items when successful
                    mock_track.assert_not_called()

    def test_put_with_customer_statsbeat_exception_tracking(self):
        """Test that LocalFileBlob.put() tracks dropped items when an exception occurs"""
        mock_statsbeat = mock.Mock()
        test_data = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
            {"name": "test_item2", "data": {"base_type": "ExceptionData"}},
        ]
        
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "exception_blob"), mock_statsbeat)
        
        # Create a test exception
        test_exception = PermissionError("Permission denied writing to file")
        
        # Mock file operations to raise an exception
        with mock.patch("builtins.open", side_effect=test_exception):
            with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                result = blob.put(test_data)
                
                # Should return None on failure
                self.assertIsNone(result)
                # Should track dropped items with the exception
                mock_track.assert_called_once_with(
                    mock_statsbeat,
                    test_data,
                    DropCode.CLIENT_EXCEPTION,
                    test_exception
                )

    def test_put_with_customer_statsbeat_os_rename_exception(self):
        """Test that LocalFileBlob.put() tracks dropped items when os.rename fails"""
        mock_statsbeat = mock.Mock()
        test_data = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]
        
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "rename_exception_blob"), mock_statsbeat)
        
        # Create a test exception for os.rename
        test_exception = OSError("Cross-device link")
        
        # Mock file write to succeed but os.rename to fail
        with mock.patch("builtins.open", mock.mock_open()):
            with mock.patch("os.rename", side_effect=test_exception):
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    result = blob.put(test_data)
                    
                    # Should return None on failure
                    self.assertIsNone(result)
                    # Should track dropped items with the rename exception
                    mock_track.assert_called_once_with(
                        mock_statsbeat,
                        test_data,
                        DropCode.CLIENT_EXCEPTION,
                        test_exception
                    )

    def test_put_without_customer_statsbeat_exception_no_tracking(self):
        """Test that LocalFileBlob.put() doesn't track when no customer_statsbeat_metrics provided"""
        test_data = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]
        
        # Create blob without customer statsbeat metrics
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "no_statsbeat_blob"))
        
        # Create a test exception
        test_exception = PermissionError("Permission denied writing to file")
        
        # Mock file operations to raise an exception
        with mock.patch("builtins.open", side_effect=test_exception):
            with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                result = blob.put(test_data)
                
                # Should return None on failure
                self.assertIsNone(result)
                # Should not track dropped items when no customer statsbeat available
                mock_track.assert_not_called()

    def test_put_customer_statsbeat_metrics_reference_preservation(self):
        """Test that the customer_statsbeat_metrics reference is preserved correctly"""
        mock_statsbeat = mock.Mock()
        test_data = [{"name": "test_item", "data": {"base_type": "RequestData"}}]
        
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "reference_blob"), mock_statsbeat)
        
        # Verify the reference is stored correctly
        self.assertEqual(blob.customer_statsbeat_metrics, mock_statsbeat)
        
        # Test that the same reference is passed to _track_dropped_items
        test_exception = IOError("File write error")
        
        with mock.patch("builtins.open", side_effect=test_exception):
            with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                result = blob.put(test_data)
                
                # Should return None on failure
                self.assertIsNone(result)
                # Verify the exact same reference is passed
                mock_track.assert_called_once()
                call_args = mock_track.call_args[0]
                self.assertIs(call_args[0], mock_statsbeat)  # Same object reference
                self.assertEqual(call_args[1], test_data)
                self.assertEqual(call_args[2], DropCode.CLIENT_EXCEPTION)
                self.assertEqual(call_args[3], test_exception)

    def test_put_with_different_exception_types_tracking(self):
        """Test LocalFileBlob.put() tracks different types of exceptions correctly"""
        mock_statsbeat = mock.Mock()
        test_data = [{"name": "test_item", "data": {"base_type": "RequestData"}}]
        
        exception_test_cases = [
            PermissionError("Permission denied"),
            OSError("Operation not permitted"),
            IOError("I/O operation failed"),
            Exception("Generic exception"),
            ValueError("Invalid value in data"),
        ]
        
        for i, test_exception in enumerate(exception_test_cases):
            with self.subTest(exception_type=type(test_exception).__name__):
                blob = LocalFileBlob(
                    os.path.join(TEST_FOLDER, f"exception_type_blob_{i}"), 
                    mock_statsbeat
                )
                
                # Mock file operations to raise the specific exception
                with mock.patch("builtins.open", side_effect=test_exception):
                    with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                        result = blob.put(test_data)
                        
                        # Should return None on failure
                        self.assertIsNone(result)
                        # Should track dropped items with the specific exception
                        mock_track.assert_called_once_with(
                            mock_statsbeat,
                            test_data,
                            DropCode.CLIENT_EXCEPTION,
                            test_exception
                        )

    def test_put_with_lease_period_and_exception_tracking(self):
        """Test that LocalFileBlob.put() tracks exceptions correctly even with lease_period"""
        mock_statsbeat = mock.Mock()
        test_data = [{"name": "test_item", "data": {"base_type": "RequestData"}}]
        
        blob = LocalFileBlob(os.path.join(TEST_FOLDER, "lease_exception_blob"), mock_statsbeat)
        
        test_exception = OSError("Disk full")
        
        # Mock file write to succeed initially, but os.rename to fail (which happens after lease processing)
        with mock.patch("builtins.open", mock.mock_open()):
            with mock.patch("os.rename", side_effect=test_exception):
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    # Test with lease_period
                    result = blob.put(test_data, lease_period=60)
                    
                    # Should return None on failure
                    self.assertIsNone(result)
                    # Should track dropped items even when lease_period is specified
                    mock_track.assert_called_once_with(
                        mock_statsbeat,
                        test_data,
                        DropCode.CLIENT_EXCEPTION,
                        test_exception
                    )


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
                self.assertIsNone(stor.put(test_input))

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

    def test_dropped_items_storage_disabled(self):
        mock_statsbeat = mock.Mock()

        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
            {"name": "test_item2", "data": {"base_type": "ExceptionData"}},
        ]

        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=False
        ):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "disabled_storage")) as stor:
                setattr(stor, '_customer_statsbeat_metrics', mock_statsbeat)

                result = stor.put(test_items)

                self.assertIsNone(result)

                self.assertEqual(mock_statsbeat.count_dropped_items.call_count, 2)

                expected_calls = [
                    mock.call(1, mock.ANY, DropCode.CLIENT_STORAGE_DISABLED),
                    mock.call(1, mock.ANY, DropCode.CLIENT_STORAGE_DISABLED),
                ]
                mock_statsbeat.count_dropped_items.assert_has_calls(expected_calls)

    def test_dropped_items_filesystem_readonly(self):
        mock_statsbeat = mock.Mock()

        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]

        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=True
        ):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_storage")) as stor:
                setattr(stor, '_customer_statsbeat_metrics', mock_statsbeat)
                stor.filesystem_is_readonly = True

                result = stor.put(test_items)

                self.assertIsNone(result)

                self.assertEqual(mock_statsbeat.count_dropped_items.call_count, 1)

                calls = mock_statsbeat.count_dropped_items.call_args_list
                drop_codes = [call[0][2] for call in calls]
                self.assertIn(DropCode.CLIENT_READONLY, drop_codes)

    def test_dropped_items_storage_full(self):
        mock_statsbeat = mock.Mock()

        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
            {"name": "test_item2", "data": {"base_type": "ExceptionData"}},
        ]

        with LocalFileStorage(os.path.join(TEST_FOLDER, "full_storage")) as stor:
            setattr(stor, '_customer_statsbeat_metrics', mock_statsbeat)

            with mock.patch.object(stor, "_check_storage_size", return_value=False):
                result = stor.put(test_items)

                self.assertIsNone(result)

                self.assertEqual(mock_statsbeat.count_dropped_items.call_count, 2)

                expected_calls = [
                    mock.call(1, mock.ANY, DropCode.CLIENT_PERSISTENCE_CAPACITY),
                    mock.call(1, mock.ANY, DropCode.CLIENT_PERSISTENCE_CAPACITY),
                ]
                mock_statsbeat.count_dropped_items.assert_has_calls(expected_calls)

    def test_dropped_items_storage_write_failure(self):
        mock_statsbeat = mock.Mock()

        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]

        with LocalFileStorage(os.path.join(TEST_FOLDER, "write_failure_storage")) as stor:
            setattr(stor, '_customer_statsbeat_metrics', mock_statsbeat)

            with mock.patch.object(LocalFileBlob, "put", return_value=None):
                result = stor.put(test_items)

                self.assertIsNone(result)

                # The customer statsbeat tracking should happen inside LocalFileBlob.put()
                # Since we mocked it to return None, the internal tracking wouldn't happen
                # So we verify the mocked put was called with the right parameters
                mock_statsbeat.count_dropped_items.assert_not_called()  # Because the mock prevented internal tracking

    def test_dropped_items_no_statsbeat_metrics(self):
        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]

        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=False
        ):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "no_statsbeat_storage")) as stor:
                self.assertIsNone(stor._customer_statsbeat_metrics)

                result = stor.put(test_items)

                self.assertIsNone(result)

    def test_dropped_items_telemetry_type_extraction(self):
        mock_statsbeat = mock.Mock()

        test_items = [
            {"name": "request_item", "data": {"base_type": "RequestData"}},
            {"name": "exception_item", "data": {"base_type": "ExceptionData"}},
            {"name": "dependency_item", "data": {"base_type": "RemoteDependencyData"}},
            {"name": "unknown_item", "data": {"base_type": "UnknownType"}},
        ]

        with LocalFileStorage(os.path.join(TEST_FOLDER, "telemetry_type_storage")) as stor:
            setattr(stor, '_customer_statsbeat_metrics', mock_statsbeat)

            with mock.patch.object(stor, "_check_storage_size", return_value=False):
                result = stor.put(test_items)

                self.assertIsNone(result)

                self.assertEqual(mock_statsbeat.count_dropped_items.call_count, 4)

                calls = mock_statsbeat.count_dropped_items.call_args_list
                for call in calls:
                    self.assertEqual(call[0][0], 1)
                    self.assertEqual(call[0][2], DropCode.CLIENT_PERSISTENCE_CAPACITY)
                    telemetry_type = call[0][1]
                    self.assertIsNotNone(telemetry_type)

    def test_successful_put_no_dropped_items(self):
        mock_statsbeat = mock.Mock()

        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]

        with LocalFileStorage(os.path.join(TEST_FOLDER, "successful_storage")) as stor:
            setattr(stor, '_customer_statsbeat_metrics', mock_statsbeat)

            mock_blob = mock.Mock()
            with mock.patch.object(LocalFileBlob, "put", return_value=mock_blob):
                result = stor.put(test_items)

                self.assertEqual(result, mock_blob)

                mock_statsbeat.count_dropped_items.assert_not_called()

    def test_exception_occurred_tracks_dropped_items(self):
        """Test that when exception_occurred is set, put() tracks dropped items in customer statsbeat."""
        mock_statsbeat = mock.Mock()
        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
            {"name": "test_item2", "data": {"base_type": "ExceptionData"}},
        ]
        
        # Mock the _check_and_set_folder_permissions to simulate an exception during initialization
        test_exception = PermissionError("Permission denied for storage folder")
        
        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=True
        ):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "exception_storage")) as stor:
                # Manually set the exception_occurred to simulate an exception that happened during initialization
                stor.exception_occurred = test_exception
                stor._customer_statsbeat_metrics = mock_statsbeat
                
                # Mock _track_dropped_items to capture the call
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    result = stor.put(test_items)
                    
                    # Verify that _track_dropped_items was called at least once with our exception
                    # Note: It might be called multiple times (once for exception_occurred, and potentially 
                    # once more if blob.put() also fails), so we check that our expected call is present
                    expected_call = mock.call(mock_statsbeat, test_items, DropCode.CLIENT_EXCEPTION, test_exception)
                    self.assertIn(expected_call, mock_track.call_args_list)
                    
                    # Verify that at least one call was made
                    self.assertGreaterEqual(mock_track.call_count, 1)

    def test_exception_occurred_specific_tracking_only(self):
        """Test the specific exception_occurred tracking logic by mocking blob.put to succeed."""
        mock_statsbeat = mock.Mock()
        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]
        
        test_exception = PermissionError("Permission denied for storage folder")
        
        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=True
        ):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "exception_specific_storage")) as stor:
                stor.exception_occurred = test_exception
                stor._customer_statsbeat_metrics = mock_statsbeat
                
                # Mock _track_dropped_items to capture the call
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    result = stor.put(test_items)
                    
                    # Should call _track_dropped_items exactly once for exception_occurred
                    mock_track.assert_called_once_with(
                        mock_statsbeat,
                        test_items,
                        DropCode.CLIENT_EXCEPTION,
                        test_exception
                    )
                    
                    # Should return None since exception_occurred causes early return
                    self.assertIsNone(result)
                    
                    # Verify that exception_occurred is reset to None after tracking
                    self.assertIsNone(stor.exception_occurred)

    def test_exception_occurred_no_customer_statsbeat(self):
        """Test that when exception_occurred is set but no customer statsbeat is available, no tracking occurs."""
        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]
        
        test_exception = OSError("Read-only filesystem")
        
        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=True
        ):
            with LocalFileStorage(os.path.join(TEST_FOLDER, "exception_no_statsbeat_storage")) as stor:
                # Set exception_occurred but no customer statsbeat metrics
                stor.exception_occurred = test_exception
                self.assertIsNone(stor._customer_statsbeat_metrics)
                
                # Mock _track_dropped_items to ensure it's not called
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    result = stor.put(test_items)
                    
                    # Should not call _track_dropped_items when no customer statsbeat is available
                    mock_track.assert_not_called()

    def test_exception_occurred_none_no_tracking(self):
        """Test that when exception_occurred is None, no exception tracking occurs."""
        mock_statsbeat = mock.Mock()
        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]
        
        with LocalFileStorage(os.path.join(TEST_FOLDER, "no_exception_storage")) as stor:
            stor._customer_statsbeat_metrics = mock_statsbeat
            # exception_occurred should be None by default
            self.assertIsNone(stor.exception_occurred)
            
            # Mock the blob.put to return a successful result
            mock_blob = mock.Mock()
            with mock.patch.object(LocalFileBlob, "put", return_value=mock_blob):
                with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                    result = stor.put(test_items)
                    
                    # Should not call _track_dropped_items for exception when exception_occurred is None
                    mock_track.assert_not_called()
                    self.assertEqual(result, mock_blob)

    def test_exception_occurred_with_different_exception_types(self):
        """Test exception tracking with different types of exceptions."""
        mock_statsbeat = mock.Mock()
        test_items = [{"name": "test_item", "data": {"base_type": "RequestData"}}]
        
        exception_test_cases = [
            PermissionError("Permission denied"),
            OSError("Operation not permitted"),
            Exception("Generic exception"),
            ValueError("Invalid value"),
        ]
        
        for i, test_exception in enumerate(exception_test_cases):
            with self.subTest(exception_type=type(test_exception).__name__):
                storage_path = os.path.join(TEST_FOLDER, f"exception_type_storage_{i}")
                
                with mock.patch.object(
                    LocalFileStorage, "_check_and_set_folder_permissions", return_value=True
                ):
                    with LocalFileStorage(storage_path) as stor:
                        stor.exception_occurred = test_exception
                        stor._customer_statsbeat_metrics = mock_statsbeat
                        
                        with mock.patch("azure.monitor.opentelemetry.exporter._storage._track_dropped_items") as mock_track:
                            result = stor.put(test_items)
                            
                            # Verify that _track_dropped_items was called with the specific exception
                            mock_track.assert_called_once_with(
                                mock_statsbeat,
                                test_items,
                                DropCode.CLIENT_EXCEPTION,
                                test_exception
                            )
                            
                            # Should return None since exception_occurred causes early return
                            self.assertIsNone(result)
                            
                            # Verify that exception_occurred is reset after tracking
                            self.assertIsNone(stor.exception_occurred)
                            mock_track.reset_mock()

    def test_check_and_set_folder_permissions_readonly_filesystem(self):
        """Test that OSError with errno.EROFS sets filesystem_is_readonly flag"""
        import errno
        
        readonly_error = OSError("Read-only file system")
        readonly_error.errno = errno.EROFS  # cspell:disable-line
        
        with mock.patch("os.makedirs", side_effect=readonly_error):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "readonly_test"))
                
                # Should not be enabled due to readonly filesystem
                self.assertFalse(stor._enabled)
                # Should set readonly flag
                self.assertTrue(stor.filesystem_is_readonly)
                # Should not set exception_occurred for readonly
                self.assertIsNone(stor.exception_occurred)

    def test_check_and_set_folder_permissions_permission_error(self):
        """Test that PermissionError (OSError subclass) sets exception_occurred"""
        permission_error = PermissionError("Permission denied")
        
        with mock.patch("os.makedirs", side_effect=permission_error):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "permission_test"))
                
                # Should not be enabled due to permission error
                self.assertFalse(stor._enabled)
                # Should not set readonly flag
                self.assertFalse(stor.filesystem_is_readonly)
                # Should set exception_occurred for permission error
                self.assertEqual(stor.exception_occurred, permission_error)

    def test_check_and_set_folder_permissions_other_os_error(self):
        """Test that other OSError types set exception_occurred"""
        import errno
        
        # Create a mock OSError with different errno (not EROFS)
        other_os_error = OSError("No space left on device")
        other_os_error.errno = errno.ENOSPC
        
        with mock.patch("os.makedirs", side_effect=other_os_error):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "other_os_error_test"))
                
                # Should not be enabled due to OS error
                self.assertFalse(stor._enabled)
                # Should not set readonly flag
                self.assertFalse(stor.filesystem_is_readonly)
                # Should set exception_occurred for other OS error
                self.assertEqual(stor.exception_occurred, other_os_error)

    def test_check_and_set_folder_permissions_general_exception(self):
        """Test that non-OSError exceptions set exception_occurred"""
        value_error = ValueError("Invalid path format")
        
        with mock.patch("os.makedirs", side_effect=value_error):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "general_exception_test"))
                
                # Should not be enabled due to general exception
                self.assertFalse(stor._enabled)
                # Should not set readonly flag
                self.assertFalse(stor.filesystem_is_readonly)
                # Should set exception_occurred for general exception
                self.assertEqual(stor.exception_occurred, value_error)

    def test_check_and_set_folder_permissions_os_error_without_errno(self):
        """Test that OSError without errno attribute sets exception_occurred"""
        # Create a regular OSError
        os_error_no_errno = OSError("Generic OS error")
        
        with mock.patch("os.makedirs", side_effect=os_error_no_errno):
            # Mock the getattr call in the storage module to return None for errno
            with mock.patch("azure.monitor.opentelemetry.exporter._storage.getattr") as mock_getattr:
                mock_getattr.return_value = None  # Simulate no errno attribute
                
                with mock.patch.object(
                    LocalFileStorage, "_maintenance_routine"
                ), mock.patch.object(LocalFileStorage, "__exit__"):
                    stor = LocalFileStorage(os.path.join(TEST_FOLDER, "no_errno_test"))
                    
                    # Should not be enabled due to OS error
                    self.assertFalse(stor._enabled)
                    # Should not set readonly flag (getattr returns None, not equal to EROFS)
                    self.assertFalse(stor.filesystem_is_readonly)
                    # Should set exception_occurred for OS error without errno
                    self.assertEqual(stor.exception_occurred, os_error_no_errno)
                    
                    # Verify getattr was called with the expected parameters
                    mock_getattr.assert_called_with(os_error_no_errno, 'errno', None)

    def test_check_and_set_folder_permissions_windows_icacls_failure(self):
        """Test Windows icacls failure handling"""
        with mock.patch("os.name", "nt"):  # Simulate Windows
            with mock.patch("os.makedirs"):  # Don't raise error in makedirs
                with mock.patch("subprocess.run") as mock_subprocess:
                    # Simulate icacls failure
                    mock_result = mock.Mock()
                    mock_result.returncode = 1  # Non-zero return code (failure)
                    mock_subprocess.return_value = mock_result
                    
                    with mock.patch.object(
                        LocalFileStorage, "_maintenance_routine"
                    ), mock.patch.object(LocalFileStorage, "__exit__"):
                        with mock.patch.object(LocalFileStorage, "_get_current_user", return_value="DOMAIN\\User"):
                            stor = LocalFileStorage(os.path.join(TEST_FOLDER, "windows_icacls_test"))
                            
                            # Should not be enabled due to icacls failure
                            self.assertFalse(stor._enabled)
                            # Should not set readonly flag (no exception thrown)
                            self.assertFalse(stor.filesystem_is_readonly)
                            # Should not set exception_occurred (no exception thrown)
                            self.assertIsNone(stor.exception_occurred)

    def test_check_and_set_folder_permissions_unix_chmod_success(self):
        """Test Unix chmod success path"""
        with mock.patch("os.name", "posix"):  # Simulate Unix
            with mock.patch("os.makedirs"):  # Don't raise error in makedirs
                with mock.patch("os.chmod"):  # Don't raise error in chmod
                    with mock.patch.object(
                        LocalFileStorage, "_maintenance_routine"
                    ), mock.patch.object(LocalFileStorage, "__exit__"):
                        stor = LocalFileStorage(os.path.join(TEST_FOLDER, "unix_success_test"))
                        
                        # Should be enabled due to successful chmod
                        self.assertTrue(stor._enabled)
                        # Should not set readonly flag
                        self.assertFalse(stor.filesystem_is_readonly)
                        # Should not set exception_occurred
                        self.assertIsNone(stor.exception_occurred)

    def test_exception_handling_categorization_integration(self):
        """Integration test to verify exception categorization works end-to-end"""
        import errno
        
        # Test data
        test_items = [
            {"name": "test_item1", "data": {"base_type": "RequestData"}},
        ]
        
        # Test 1: Readonly filesystem error
        readonly_error = OSError("Read-only file system")
        readonly_error.errno = errno.EROFS
        
        with mock.patch("os.makedirs", side_effect=readonly_error):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "integration_test"))
                
                # Should categorize as readonly and be disabled
                self.assertTrue(stor.filesystem_is_readonly)
                self.assertIsNone(stor.exception_occurred)
                self.assertFalse(stor._enabled)  # Storage should be disabled
                
                # Test put behavior - disabled storage should return CLIENT_STORAGE_DISABLED
                # But we can test that readonly flag was properly set during initialization
                with mock.patch.object(stor, '_customer_statsbeat_metrics') as mock_statsbeat:
                    result = stor.put(test_items)
                    
                    # Should return None and track storage disabled (since _enabled=False)
                    self.assertIsNone(result)
                    mock_statsbeat.count_dropped_items.assert_called_once()
                    args = mock_statsbeat.count_dropped_items.call_args[0]
                    self.assertEqual(args[2], DropCode.CLIENT_STORAGE_DISABLED)
        
        # Test 2: Permission error (should go to exception_occurred)
        permission_error = PermissionError("Permission denied")
        
        with mock.patch("os.makedirs", side_effect=permission_error):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "integration_test2"))
                
                # Should categorize as general exception and be disabled
                self.assertFalse(stor.filesystem_is_readonly)
                self.assertEqual(stor.exception_occurred, permission_error)
                self.assertFalse(stor._enabled)  # Storage should be disabled
                
        # Test 3: Successful initialization with enabled storage to test readonly handling in put()
        with mock.patch.object(
            LocalFileStorage, "_check_and_set_folder_permissions", return_value=True
        ):
            with mock.patch.object(
                LocalFileStorage, "_maintenance_routine"
            ), mock.patch.object(LocalFileStorage, "__exit__"):
                stor = LocalFileStorage(os.path.join(TEST_FOLDER, "integration_test3"))
                
                # Should be enabled and not have readonly/exception flags
                self.assertTrue(stor._enabled)
                self.assertFalse(stor.filesystem_is_readonly)
                self.assertIsNone(stor.exception_occurred)
                
                # Now test readonly handling in put() by manually setting the flag
                stor.filesystem_is_readonly = True
                
                with mock.patch.object(stor, '_customer_statsbeat_metrics') as mock_statsbeat:
                    result = stor.put(test_items)
                    
                    # Should return None and track readonly drop
                    self.assertIsNone(result)
                    mock_statsbeat.count_dropped_items.assert_called_once()
                    args = mock_statsbeat.count_dropped_items.call_args[0]
                    self.assertEqual(args[2], DropCode.CLIENT_READONLY)
