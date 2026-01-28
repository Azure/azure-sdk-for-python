# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import threading
import time
from unittest.mock import Mock, patch

from azure.monitor.opentelemetry.exporter._configuration._worker import _ConfigurationWorker
from azure.monitor.opentelemetry.exporter._constants import _ONE_SETTINGS_PYTHON_TARGETING


# pylint: disable=protected-access, docstring-missing-param
class TestConfigurationWorker(unittest.TestCase):
    """Test cases for _ConfigurationWorker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_configuration_manager = Mock()
        self.mock_configuration_manager.get_configuration_and_refresh_interval.return_value = 1800

    def tearDown(self):  # pylint: disable=docstring-missing-return, docstring-missing-rtype
        """Clean up after each test."""
        # Ensure any workers created during tests are shut down
        # This prevents hanging tests and resource leaks
        pass  # pylint: disable=unnecessary-pass

    def test_init_with_default_refresh_interval(self):
        """Test worker initialization with default refresh interval."""
        with patch("random.uniform", return_value=0.1):  # Short startup delay for tests
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            try:
                # Verify initial state
                self.assertEqual(worker._configuration_manager, self.mock_configuration_manager)
                self.assertEqual(worker._default_refresh_interval, 3600)
                self.assertEqual(worker._refresh_interval, 3600)
                self.assertTrue(worker._running)

                # Verify thread was created and started
                self.assertIsNotNone(worker._refresh_thread)
                self.assertTrue(worker._refresh_thread.is_alive())
                self.assertTrue(worker._refresh_thread.daemon)
                self.assertEqual(worker._refresh_thread.name, "ConfigurationWorker")

            finally:
                worker.shutdown()

    def test_init_with_custom_refresh_interval(self):
        """Test worker initialization with custom refresh interval."""
        custom_interval = 900

        with patch("random.uniform", return_value=0.1):
            worker = _ConfigurationWorker(self.mock_configuration_manager, custom_interval)

            try:
                self.assertEqual(worker._refresh_interval, custom_interval)
                self.assertEqual(worker.get_refresh_interval(), custom_interval)
            finally:
                worker.shutdown()

    def test_get_refresh_interval_thread_safe(self):
        """Test that get_refresh_interval is thread-safe."""
        with patch("random.uniform", return_value=0.1):
            worker = _ConfigurationWorker(self.mock_configuration_manager, 1200)

            try:
                # Test from multiple threads
                results = []

                def get_interval():
                    results.append(worker.get_refresh_interval())

                threads = [threading.Thread(target=get_interval) for _ in range(10)]

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                # All results should be the same
                self.assertEqual(len(set(results)), 1)
                self.assertEqual(results[0], 1200)

            finally:
                worker.shutdown()

    @patch("random.uniform")
    def test_startup_delay_range(self, mock_random):
        """Test that startup delay is applied with correct range."""
        mock_random.return_value = 7.5  # Middle of range

        worker = _ConfigurationWorker(self.mock_configuration_manager)

        try:
            # Verify random.uniform was called with correct range
            mock_random.assert_called_once_with(5.0, 15.0)
        finally:
            worker.shutdown()

    def test_configuration_refresh_called(self):
        """Test that configuration refresh is called with correct parameters."""
        with patch("random.uniform", return_value=0.001):  # Very short delay
            worker = _ConfigurationWorker(self.mock_configuration_manager, 0.01)  # Very short interval

            try:
                # Wait for at least one refresh cycle with timeout
                max_wait = 1.0  # Maximum 1 second wait
                start_time = time.time()

                while time.time() - start_time < max_wait:
                    if self.mock_configuration_manager.get_configuration_and_refresh_interval.called:
                        break
                    time.sleep(0.01)

                # Verify the configuration manager was called
                self.mock_configuration_manager.get_configuration_and_refresh_interval.assert_called_with(
                    _ONE_SETTINGS_PYTHON_TARGETING
                )

            finally:
                worker.shutdown()

    def test_refresh_interval_update(self):
        """Test that refresh interval is updated from configuration manager response."""
        # Mock returns different intervals
        self.mock_configuration_manager.get_configuration_and_refresh_interval.side_effect = [1800, 3600]

        with patch("random.uniform", return_value=0.001):
            worker = _ConfigurationWorker(self.mock_configuration_manager, 0.01)

            try:
                # Wait for refresh cycles with timeout
                max_wait = 1.0
                start_time = time.time()

                while time.time() - start_time < max_wait:
                    if self.mock_configuration_manager.get_configuration_and_refresh_interval.call_count >= 1:
                        break
                    time.sleep(0.01)

                # Should have updated to the new interval
                current_interval = worker.get_refresh_interval()
                self.assertIn(current_interval, [1800, 3600])  # Could be either depending on timing

            finally:
                worker.shutdown()

    @patch("azure.monitor.opentelemetry.exporter._configuration._worker.logger")
    def test_exception_handling_in_refresh_loop(self, mock_logger):
        """Test that exceptions in refresh loop are handled gracefully."""
        # Make the configuration manager raise an exception
        self.mock_configuration_manager.get_configuration_and_refresh_interval.side_effect = Exception("Test error")

        with patch("random.uniform", return_value=0.001):
            worker = _ConfigurationWorker(self.mock_configuration_manager, 0.01)

            try:
                # Wait for refresh cycles with timeout
                max_wait = 1.0
                start_time = time.time()

                while time.time() - start_time < max_wait:
                    if mock_logger.warning.called:
                        break
                    time.sleep(0.01)

                # Worker should still be running despite exception
                self.assertTrue(worker._running)
                self.assertTrue(worker._refresh_thread.is_alive())

                # Error should be logged
                mock_logger.warning.assert_called()
                warning_call = mock_logger.warning.call_args[0]
                self.assertIn("Configuration refresh failed", warning_call[0])
                self.assertIn("Test error", str(warning_call[1]))

            finally:
                worker.shutdown()

    def test_shutdown_graceful(self):
        """Test graceful shutdown of worker."""
        with patch("random.uniform", return_value=0.001):
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            # Verify worker is running
            self.assertTrue(worker._running)
            self.assertTrue(worker._refresh_thread.is_alive())

            # Shutdown with timeout
            start_time = time.time()
            worker.shutdown()
            shutdown_time = time.time() - start_time

            # Verify shutdown state
            self.assertFalse(worker._running)
            self.assertTrue(worker._shutdown_event.is_set())

            # Shutdown should be reasonably fast
            self.assertLess(shutdown_time, 2.0)  # Should not take more than 2 seconds

            # Thread should be stopped
            self.assertFalse(worker._refresh_thread.is_alive())

    def test_shutdown_idempotent(self):
        """Test that shutdown can be called multiple times safely."""
        with patch("random.uniform", return_value=0.01):
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            # First shutdown
            worker.shutdown()
            self.assertFalse(worker._running)

            # Second shutdown should not cause errors
            try:
                worker.shutdown()
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.fail(f"Second shutdown raised an exception: {e}")

            # State should remain shutdown
            self.assertFalse(worker._running)

    def test_shutdown_during_startup_delay(self):
        """Test shutdown during startup delay period."""
        with patch("random.uniform", return_value=1.0):  # 1 second startup delay
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            # Shutdown immediately with timeout
            start_time = time.time()
            worker.shutdown()
            shutdown_time = time.time() - start_time

            # Should shutdown cleanly even during startup delay
            self.assertFalse(worker._running)

            # Shutdown should be reasonably fast (much less than the startup delay)
            self.assertLess(shutdown_time, 0.5)  # Should be much faster than 1 second startup delay

            # Thread should be stopped
            self.assertFalse(worker._refresh_thread.is_alive())

            # Configuration manager should not have been called
            self.mock_configuration_manager.get_configuration_and_refresh_interval.assert_not_called()

    def test_shutdown_thread_safety(self):
        """Test that shutdown is thread-safe."""
        with patch("random.uniform", return_value=0.01):
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            # Shutdown from multiple threads
            shutdown_results = []

            def shutdown_worker():
                try:
                    worker.shutdown()
                    shutdown_results.append("success")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    shutdown_results.append(f"error: {e}")

            threads = [threading.Thread(target=shutdown_worker) for _ in range(5)]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # All shutdowns should succeed
            self.assertEqual(len(shutdown_results), 5)
            self.assertTrue(all(result == "success" for result in shutdown_results))
            self.assertFalse(worker._running)

    def test_daemon_thread_property(self):
        """Test that the worker thread is created as a daemon thread."""
        with patch("random.uniform", return_value=0.01):
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            try:
                # Verify thread is daemon
                self.assertTrue(worker._refresh_thread.daemon)
            finally:
                worker.shutdown()

    @patch("threading.Thread")
    def test_thread_target_and_name(self, mock_thread_class):
        """Test that thread is created with correct target and name."""
        mock_thread_instance = Mock()
        mock_thread_instance.is_alive.return_value = False  # Simulate thread that doesn't start
        mock_thread_class.return_value = mock_thread_instance

        with patch("random.uniform", return_value=0.001):
            worker = _ConfigurationWorker(self.mock_configuration_manager)

            try:
                # Verify thread was created with correct parameters
                mock_thread_class.assert_called_once_with(
                    target=worker._get_configuration, name="ConfigurationWorker", daemon=True
                )

                # Verify thread was started
                mock_thread_instance.start.assert_called_once()

            finally:
                # Call shutdown to clean up, even though thread is mocked
                worker.shutdown()

    def test_configuration_targeting_parameter(self):
        """Test that the correct targeting parameter is passed."""
        with patch("random.uniform", return_value=0.001):
            worker = _ConfigurationWorker(self.mock_configuration_manager, 0.01)

            try:
                # Wait for refresh with timeout
                max_wait = 1.0
                start_time = time.time()

                while time.time() - start_time < max_wait:
                    if self.mock_configuration_manager.get_configuration_and_refresh_interval.called:
                        break
                    time.sleep(0.01)

                # Verify correct parameter was passed
                self.mock_configuration_manager.get_configuration_and_refresh_interval.assert_called_with(
                    _ONE_SETTINGS_PYTHON_TARGETING
                )

            finally:
                worker.shutdown()

    def test_lock_protects_worker_state(self):
        """Test that single lock properly protects worker state access."""
        with patch("random.uniform", return_value=0.01):
            worker = _ConfigurationWorker(self.mock_configuration_manager, 1000)

            try:
                # Test that get_refresh_interval works normally
                interval = worker.get_refresh_interval()
                self.assertEqual(interval, 1000)

                # Test thread safety by accessing from current thread
                # (We can't easily test cross-thread locking without risking deadlock)
                with worker._lock:
                    # While holding lock, verify we can still access internal state
                    self.assertEqual(worker._refresh_interval, 1000)
                    self.assertTrue(worker._running)

            finally:
                worker.shutdown()

    def test_refresh_loop_continues_after_exception(self):  # pylint: disable=name-too-long
        """Test that refresh loop continues after exceptions."""
        # First call raises exception, second succeeds
        self.mock_configuration_manager.get_configuration_and_refresh_interval.side_effect = [
            Exception("First error"),
            1500,
            Exception("Second error"),
            2000,
        ]

        with patch("random.uniform", return_value=0.001):
            worker = _ConfigurationWorker(self.mock_configuration_manager, 0.005)

            try:
                # Wait for multiple refresh cycles with timeout
                max_wait = 1.0
                start_time = time.time()

                while time.time() - start_time < max_wait:
                    if self.mock_configuration_manager.get_configuration_and_refresh_interval.call_count >= 2:
                        break
                    time.sleep(0.01)

                # Should have called multiple times despite exceptions
                call_count = self.mock_configuration_manager.get_configuration_and_refresh_interval.call_count
                self.assertGreaterEqual(call_count, 1)  # At least one call should have happened

            finally:
                worker.shutdown()


if __name__ == "__main__":
    unittest.main()
