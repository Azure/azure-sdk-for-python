# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics.export import NumberDataPoint

from azure.core.exceptions import HttpResponseError
from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._state import _STATSBEAT_STATE, _STATSBEAT_STATE_LOCK
from azure.monitor.opentelemetry.exporter._constants import _STATSBEAT_METRIC_NAME_MAPPINGS
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient

from azure.monitor.opentelemetry.exporter._generated.models import (
    TelemetryErrorDetails,
    TelemetryItem,
    TrackResponse,
)


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


# pylint: disable=protected-access
class TestStatsbeatExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "false"

    def setUp(self):
        """Reset statsbeat state before each test."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 0
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["SHUTDOWN"] = False
            _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = False
            _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = False
        
        # Create exporter for each test to ensure clean state
        self._exporter = _StatsBeatExporter(disable_offline_storage=True)
        self._envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now())]

    def tearDown(self):
        """Clean up after each test."""
        # Reset any environment variables or state if needed
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        # Clean up environment variables
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_init(self, collect_mock):
        """Test that statsbeat exporter initializes correctly."""
        exporter = _StatsBeatExporter(disable_offline_storage=True)
        self.assertFalse(exporter._should_collect_stats())
        collect_mock.assert_not_called()

    def test_point_to_envelope(self):
        """Test converting data points to envelopes with proper metric name mapping."""
        resource = Resource.create(attributes={"asd": "test_resource"})
        point = NumberDataPoint(
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
            attributes={},
        )
        for ot_name, sb_name in _STATSBEAT_METRIC_NAME_MAPPINGS.items():
            envelope = self._exporter._point_to_envelope(point, ot_name, resource)
            self.assertEqual(envelope.data.base_data.metrics[0].name, sb_name)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.set_statsbeat_initial_success")
    def test_transmit_200_reach_ingestion(self, mock_set_success):
        """Test successful transmission that reaches ingestion."""
        # Reset the state properly
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = self._exporter._transmit(self._envelopes_to_export)
            
        mock_set_success.assert_called_once_with(True)
        self.assertEqual(result, ExportResult.SUCCESS)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.set_statsbeat_initial_success")
    def test_transmit_206_reach_ingestion(self, mock_set_success):
        """Test partial success transmission that reaches ingestion."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[TelemetryErrorDetails(index=0, status_code=500, message="should retry")],
            )
            result = self._exporter._transmit(self._envelopes_to_export)
            
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        mock_set_success.assert_called_once_with(True)

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.set_statsbeat_initial_success")
    def test_transmit_reach_ingestion_code(self, mock_set_success):
        """Test transmission that reaches ingestion but fails with retryable error."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._reached_ingestion_code") as m, \
             mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as p:
            m.return_value = True
            p.return_value = True
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                result = self._exporter._transmit(self._envelopes_to_export)
                
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
        mock_set_success.assert_called_once_with(True)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._state.increment_statsbeat_initial_failure_count")
    def test_transmit_not_reach_ingestion_code(self, mock_increment_failure):
        """Test transmission that doesn't reach ingestion."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 1
            
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._reached_ingestion_code") as m, \
             mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as p:
            m.return_value = False
            p.return_value = False
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                result = self._exporter._transmit(self._envelopes_to_export)
                
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertFalse(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        mock_increment_failure.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._state.increment_statsbeat_initial_failure_count")
    def test_transmit_not_reach_ingestion_exception(self, mock_increment_failure):
        """Test transmission that fails with exception but doesn't trigger shutdown."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 1
            
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics") as m:
            with mock.patch.object(AzureMonitorClient, "track", throw(Exception)):
                result = self._exporter._transmit(self._envelopes_to_export)
                
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertFalse(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        mock_increment_failure.assert_called_once()
        m.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._state.increment_statsbeat_initial_failure_count")
    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.increment_and_check_statsbeat_failure_count")
    def test_transmit_not_reach_ingestion_exception_shutdown(self, mock_check_failure, mock_increment_failure):
        """Test transmission that fails and triggers statsbeat shutdown."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 2
            
        # Mock the failure check to return True (threshold reached)
        mock_check_failure.return_value = True
        
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics") as m:
            with mock.patch.object(AzureMonitorClient, "track", throw(Exception)):
                result = self._exporter._transmit(self._envelopes_to_export)
                
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertFalse(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        mock_check_failure.assert_called_once()
        m.assert_called_once()


    def test_statsbeat_no_recursive_metrics_should_collect_stats(self):
        """Test that statsbeat exporter correctly identifies itself and doesn't collect stats on itself."""
        # Verify that the statsbeat exporter identifies itself correctly
        self.assertTrue(self._exporter._is_stats_exporter())
        
        # Verify that statsbeat exporter should not collect stats on itself
        self.assertFalse(self._exporter._should_collect_stats())

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._update_requests_map")
    def test_statsbeat_no_recursive_metrics_success_case(self, mock_update_requests):
        """Test that successful statsbeat transmission doesn't update request maps (no recursive tracking)."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch.object(AzureMonitorClient, "track") as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = self._exporter._transmit(self._envelopes_to_export)
            
        # Verify the transmission was successful
        self.assertEqual(result, ExportResult.SUCCESS)
        
        # Verify that no statsbeat metrics were collected about this transmission
        mock_update_requests.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._update_requests_map")
    def test_statsbeat_no_recursive_metrics_failure_case(self, mock_update_requests):
        """Test that failed statsbeat transmission doesn't update request maps (no recursive tracking)."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._reached_ingestion_code") as m, \
             mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as p:
            m.return_value = False
            p.return_value = False
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                result = self._exporter._transmit(self._envelopes_to_export)
                
        # Verify the transmission failed as expected
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        
        # Verify that no statsbeat metrics were collected about this transmission failure
        mock_update_requests.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._update_requests_map")
    def test_statsbeat_no_recursive_metrics_exception_case(self, mock_update_requests):
        """Test that statsbeat transmission exceptions don't update request maps (no recursive tracking)."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch.object(AzureMonitorClient, "track", throw(Exception("Test exception"))):
            result = self._exporter._transmit(self._envelopes_to_export)
                
        # Verify the transmission failed as expected
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        
        # Verify that no statsbeat metrics were collected about this transmission exception
        mock_update_requests.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._update_requests_map")
    def test_statsbeat_no_recursive_metrics_retry_case(self, mock_update_requests):
        """Test that retryable statsbeat failures don't update request maps (no recursive tracking)."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._reached_ingestion_code") as m, \
             mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as p:
            m.return_value = True
            p.return_value = True
            with mock.patch.object(AzureMonitorClient, "track", throw(HttpResponseError)):
                result = self._exporter._transmit(self._envelopes_to_export)
                
        # Verify the transmission is marked as retryable
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
        
        # Verify that no statsbeat retry metrics were collected about this transmission
        mock_update_requests.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._update_requests_map")
    def test_statsbeat_no_recursive_metrics_throttle_case(self, mock_update_requests):
        """Test that throttled statsbeat requests don't update request maps (no recursive tracking)."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_throttle_code") as throttle_mock:
            throttle_mock.return_value = True
            # Also need to mock _is_retryable_code to return False so we get to the throttle check
            with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as retryable_mock:
                retryable_mock.return_value = False
                with mock.patch.object(AzureMonitorClient, "track") as track_mock:
                    # Create an HttpResponseError with a throttle status code (402 or 439)
                    error = HttpResponseError("Quota exceeded")
                    error.status_code = 402  # Use actual throttle code instead of 429
                    track_mock.side_effect = error
                    result = self._exporter._transmit(self._envelopes_to_export)
                
        # Verify the transmission failed as expected
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        
        # Verify that no statsbeat throttle metrics were collected about this transmission
        mock_update_requests.assert_not_called()

    def test_statsbeat_exporter_attribute_detection(self):
        """Test that the attribute-based detection correctly identifies statsbeat exporter."""
        # Test that the base class method correctly identifies this as a statsbeat exporter
        # The _StatsBeatExporter should set is_stats_exporter=True in kwargs
        self.assertTrue(self._exporter._is_stats_exporter())
        
        # Verify the internal attribute is set correctly
        self.assertTrue(getattr(self._exporter, "_stats_exporter", False))
        
        # Create a regular (non-statsbeat) exporter to compare
        from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
        regular_exporter = AzureMonitorMetricExporter(disable_offline_storage=True)
        
        # Regular exporter should not be identified as statsbeat exporter
        self.assertFalse(regular_exporter._is_stats_exporter())
        
        # Verify the internal attribute is False for regular exporter
        self.assertFalse(getattr(regular_exporter, "_stats_exporter", False))
        
    def test_statsbeat_exporter_kwarg_propagation(self):
        """Test that is_stats_exporter kwarg is properly propagated to the underlying exporter."""
        # Create a new statsbeat exporter
        exporter = _StatsBeatExporter(disable_offline_storage=True)
        
        # Verify that the is_stats_exporter flag was properly set
        self.assertTrue(exporter._is_stats_exporter())
        
        # Verify that the underlying _exporter also has the flag set
        self.assertTrue(getattr(exporter._exporter, "_stats_exporter", False))
        
        # Test that creating a regular exporter without the flag works correctly
        from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
        regular_exporter = AzureMonitorMetricExporter(disable_offline_storage=True)
        self.assertFalse(regular_exporter._is_stats_exporter())
        
        # Test that explicitly setting is_stats_exporter=False works
        explicit_false_exporter = AzureMonitorMetricExporter(disable_offline_storage=True, is_stats_exporter=False)
        self.assertFalse(explicit_false_exporter._is_stats_exporter())
        
        # Test that explicitly setting is_stats_exporter=True works for regular exporter
        explicit_true_exporter = AzureMonitorMetricExporter(disable_offline_storage=True, is_stats_exporter=True)
        self.assertTrue(explicit_true_exporter._is_stats_exporter())

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._utils._update_requests_map")
    def test_statsbeat_no_duration_tracking(self, mock_update_requests):
        """Test that statsbeat transmission duration is not tracked to prevent recursion."""
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            
        # Mock a slow response to ensure duration would be > 0
        import time
        with mock.patch.object(AzureMonitorClient, "track") as post:
            def slow_track(*args, **kwargs):
                time.sleep(0.01)  # Small delay to create measurable duration
                return TrackResponse(items_received=1, items_accepted=1, errors=[])
            post.side_effect = slow_track
            
            result = self._exporter._transmit(self._envelopes_to_export)
            
        # Verify the transmission was successful
        self.assertEqual(result, ExportResult.SUCCESS)
        
        # Verify that no duration metrics were collected
        # Check that _update_requests_map was never called with duration-related parameters
        for call in mock_update_requests.call_args_list:
            self.assertNotIn("duration", str(call))
            self.assertNotIn("count", str(call))

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics")
    def test_statsbeat_initialization_no_self_collection(self, mock_collect):
        """Test that statsbeat exporter initialization doesn't trigger statsbeat collection on itself."""
        # Create a new statsbeat exporter
        exporter = _StatsBeatExporter(disable_offline_storage=True)
        
        # Verify that no statsbeat collection was triggered during initialization
        mock_collect.assert_not_called()
        
        # Verify that the exporter correctly identifies itself
        self.assertTrue(exporter._is_stats_exporter())
        self.assertFalse(exporter._should_collect_stats())

    def test_statsbeat_recursive_prevention_integration(self):
        """Integration test to verify complete recursive prevention."""
        # This test simulates the complete flow and ensures no recursive behavior
        
        # Store original request map state
        from azure.monitor.opentelemetry.exporter.statsbeat._state import _REQUESTS_MAP
        original_requests_map = dict(_REQUESTS_MAP)
        
        try:
            # Clear the requests map
            _REQUESTS_MAP.clear()
            
            with _STATSBEAT_STATE_LOCK:
                _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
                
            # Perform multiple operations that would normally generate statsbeat metrics
            with mock.patch.object(AzureMonitorClient, "track") as post:
                # Successful transmission
                post.return_value = TrackResponse(items_received=1, items_accepted=1, errors=[])
                result1 = self._exporter._transmit(self._envelopes_to_export)
                
                # Failed transmission
                post.side_effect = Exception("Test failure")
                result2 = self._exporter._transmit(self._envelopes_to_export)
                
                # Retry transmission  
                post.side_effect = HttpResponseError("Retryable error")
                with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code", return_value=True):
                    result3 = self._exporter._transmit(self._envelopes_to_export)
            
            # Verify that no metrics were added to the requests map
            self.assertEqual(len(_REQUESTS_MAP), 0, "Statsbeat exporter should not add any metrics to requests map")
            
            # Verify expected results
            self.assertEqual(result1, ExportResult.SUCCESS)
            self.assertEqual(result2, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(result3, ExportResult.FAILED_RETRYABLE)
            
        finally:
            # Restore original request map state
            _REQUESTS_MAP.clear()
            _REQUESTS_MAP.update(original_requests_map)
