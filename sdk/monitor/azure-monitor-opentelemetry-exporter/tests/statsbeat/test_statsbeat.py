# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._constants import (
    _DEFAULT_EU_STATS_CONNECTION_STRING,
    _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
)
from azure.monitor.opentelemetry.exporter.statsbeat import StatsbeatConfig, _statsbeat
from azure.monitor.opentelemetry.exporter.statsbeat._manager import StatsbeatManager
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatFeature
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL,
    _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME,
    _APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL_ENV_NAME,
    _APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME,
)

# cSpell:disable


# pylint: disable=protected-access, docstring-missing-param
class TestStatsbeat(unittest.TestCase):
    def setUp(self):
        os.environ[_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL] = "false"
        os.environ[_APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME] = "30"
        os.environ[_APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL_ENV_NAME] = "15"
        # Reset singleton state - only clear StatsbeatManager instances
        if StatsbeatManager in StatsbeatManager._instances:
            del StatsbeatManager._instances[StatsbeatManager]
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 0
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["SHUTDOWN"] = False
            _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = False
            _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = False
            _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"] = False

    def tearDown(self):
        """Clean up after tests."""
        StatsbeatManager().shutdown()
        os.environ.pop(_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL, None)
        os.environ.pop(_APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL_ENV_NAME, None)
        os.environ.pop(_APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME, None)
        # Reset singleton state - only clear StatsbeatManager instances
        if StatsbeatManager in StatsbeatManager._instances:
            del StatsbeatManager._instances[StatsbeatManager]

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetrics")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics(self, mock_exporter, mock_reader, mock_meter_provider, mock_statsbeat_metrics):
        """Test that collect_statsbeat_metrics properly initializes statsbeat collection."""
        # Arrange
        exporter = mock.Mock()
        exporter._endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        exporter._instrumentation_key = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        # Set up mock returns
        mock_exporter_instance = mock.Mock()
        mock_exporter.return_value = mock_exporter_instance

        mock_reader_instance = mock.Mock()
        mock_reader.return_value = mock_reader_instance

        mock_meter_provider_instance = mock.Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        flush_mock = mock.Mock()
        mock_meter_provider_instance.force_flush = flush_mock

        mock_statsbeat_metrics_instance = mock.Mock()
        mock_statsbeat_metrics.return_value = mock_statsbeat_metrics_instance

        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - verify manager is initialized
        self.assertTrue(manager._initialized)
        self.assertEqual(manager._metrics, mock_statsbeat_metrics_instance)
        self.assertEqual(manager._meter_provider, mock_meter_provider_instance)
        self.assertIsInstance(manager._config, StatsbeatConfig)

        # Verify configuration was created correctly from exporter
        config = manager._config
        self.assertEqual(config.endpoint, exporter._endpoint)
        self.assertEqual(config.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(config.disable_offline_storage, exporter._disable_offline_storage)
        self.assertEqual(config.credential, exporter._credential)
        self.assertEqual(config.distro_version, exporter._distro_version)

        # Verify statsbeat metrics creation
        mock_statsbeat_metrics.assert_called_once_with(
            mock_meter_provider_instance,
            exporter._instrumentation_key,
            exporter._endpoint,
            exporter._disable_offline_storage,
            2,
            False,
            exporter._distro_version,
        )

        # Verify initialization methods were called
        flush_mock.assert_called_once()
        mock_statsbeat_metrics_instance.init_non_initial_metrics.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_configuration_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_registers_configuration_callback(  # pylint: disable=name-too-long
        self,
        mock_exporter,
        mock_reader,
        mock_meter_provider,
        mock_get_manager,
        mock_get_configuration_manager,  # pylint: disable=docstring-missing-param
    ):
        """Test that collect_statsbeat_metrics registers a configuration callback when initialized successfully."""
        # Arrange
        exporter = mock.Mock()
        exporter._endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        exporter._instrumentation_key = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3334"
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        # Set up mock returns
        mock_exporter_instance = mock.Mock()
        mock_exporter.return_value = mock_exporter_instance

        mock_reader_instance = mock.Mock()
        mock_reader.return_value = mock_reader_instance

        mock_meter_provider_instance = mock.Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        flush_mock = mock.Mock()
        mock_meter_provider_instance.force_flush = flush_mock

        manager = mock.Mock()
        manager.initialize.return_value = True
        mock_get_manager.return_value = manager

        mock_config_manager_instance = mock.Mock()
        mock_get_configuration_manager.return_value = mock_config_manager_instance

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - verify manager is initialized
        self.assertTrue(manager._initialized)

        # Verify that the configuration manager callback was registered
        mock_config_manager_instance.register_callback.assert_called_once()

        # Verify the callback function passed is the expected one
        registered_callback = mock_config_manager_instance.register_callback.call_args[0][0]
        self.assertEqual(registered_callback, _statsbeat.get_statsbeat_configuration_callback)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.evaluate_feature")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.StatsbeatConfig")
    def test_get_statsbeat_configuration_callback_successful_update(  # pylint: disable=name-too-long
        self,
        mock_statsbeat_config_cls,
        mock_get_manager,
        mock_evaluate_feature,  # pylint: disable=docstring-missing-param
    ):
        """Test that configuration callback successfully updates configuration when statsbeat is initialized."""
        # Arrange
        mock_manager_instance = mock.Mock()
        mock_get_manager.return_value = mock_manager_instance

        # Create mock current config
        current_config = mock.Mock()
        mock_manager_instance.get_current_config.return_value = current_config

        # Create mock updated config
        updated_config = mock.Mock()
        mock_statsbeat_config_cls.from_config.return_value = updated_config

        # mock evaluate_feature to return True (indicating SDK stats should be enabled)
        mock_evaluate_feature.return_value = True

        settings = {"disable_offline_storage": "true"}

        # Act
        _statsbeat.get_statsbeat_configuration_callback(settings)

        # Assert
        mock_evaluate_feature.assert_called_once()
        mock_get_manager.assert_called_once()
        mock_manager_instance.get_current_config.assert_called_once()
        mock_statsbeat_config_cls.from_config.assert_called_once_with(current_config, settings)
        mock_manager_instance.initialize.assert_called_once_with(updated_config)
        mock_manager_instance.shutdown.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.evaluate_feature")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.StatsbeatConfig")
    def test_get_statsbeat_configuration_callback_disable_sdkstats(  # pylint: disable=name-too-long
        self, mock_statsbeat_config_cls, mock_get_manager, mock_evaluate_feature
    ):
        """Test that configuration callback successfully updates configuration when statsbeat is initialized."""
        # Arrange
        mock_manager_instance = mock.Mock()
        mock_get_manager.return_value = mock_manager_instance

        # Create mock current config
        current_config = mock.Mock()
        mock_manager_instance.get_current_config.return_value = current_config

        # Create mock updated config
        updated_config = mock.Mock()
        mock_statsbeat_config_cls.from_config.return_value = updated_config

        # mock evaluate_feature to return False (indicating SDK stats should be disabled)
        mock_evaluate_feature.return_value = False

        settings = {"disable_offline_storage": "true"}

        # Act
        _statsbeat.get_statsbeat_configuration_callback(settings)

        # Assert
        mock_evaluate_feature.assert_called_once()
        mock_get_manager.assert_called_once()
        mock_manager_instance.get_current_config.assert_not_called()
        mock_statsbeat_config_cls.from_config.assert_not_called()
        mock_manager_instance.initialize.assert_not_called()
        mock_manager_instance.shutdown.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.evaluate_feature")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.StatsbeatConfig")
    def test_get_statsbeat_configuration_callback_not_initialized(  # pylint: disable=name-too-long
        self, mock_statsbeat_config_cls, mock_get_manager, mock_evaluate_feature
    ):
        """Test that configuration callback handles case when statsbeat is not initialized."""
        # Arrange
        mock_manager_instance = mock.Mock()
        mock_get_manager.return_value = mock_manager_instance
        mock_manager_instance.get_current_config.return_value = None
        # mock evaluate_feature to return True (indicating SDK stats should be enabled)
        mock_evaluate_feature.return_value = True

        settings = {"disable_offline_storage": "true"}

        # Act
        _statsbeat.get_statsbeat_configuration_callback(settings)

        # Assert
        mock_get_manager.assert_called_once()
        mock_manager_instance.get_current_config.assert_called_once()
        mock_statsbeat_config_cls.from_config.assert_not_called()
        mock_manager_instance.initialize.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.evaluate_feature")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.StatsbeatConfig")
    def test_get_statsbeat_configuration_callback_no_updated_config(  # pylint: disable=name-too-long
        self, mock_statsbeat_config_cls, mock_get_manager, mock_evaluate_feature
    ):
        """Test that configuration callback handles case when StatsbeatConfig.from_config returns None."""
        # Arrange
        mock_manager_instance = mock.Mock()
        mock_get_manager.return_value = mock_manager_instance

        # Create mock current config
        current_config = mock.Mock()
        mock_manager_instance.get_current_config.return_value = current_config

        # mock evaluate_feature to return True (indicating SDK stats should be enabled)
        mock_evaluate_feature.return_value = True

        # Mock from_config to return False (indicating no valid update)
        mock_statsbeat_config_cls.from_config.return_value = False

        settings = {"disable_offline_storage": "invalid_value"}

        # Act
        _statsbeat.get_statsbeat_configuration_callback(settings)

        # Assert
        mock_statsbeat_config_cls.from_config.assert_called_once_with(current_config, settings)
        mock_get_manager.assert_called_once()
        mock_manager_instance.initialize.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter._configuration._ConfigurationManager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetrics")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_no_callback_when_init_fails(  # pylint: disable=name-too-long
        self,
        mock_exporter,
        mock_reader,
        mock_meter_provider,
        mock_statsbeat_metrics,
        mock_config_manager_cls,  # pylint: disable=unused-argument
    ):
        """Test that configuration callback is not registered when initialization fails."""
        # Arrange
        exporter = mock.Mock()
        exporter._endpoint = ""  # Invalid endpoint to cause initialization failure
        exporter._instrumentation_key = ""  # Invalid key
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        mock_config_manager_instance = mock.Mock()
        mock_config_manager_cls.return_value = mock_config_manager_instance

        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - verify manager is still not initialized
        self.assertFalse(manager._initialized)

        # Verify that the configuration manager callback was NOT registered
        mock_config_manager_instance.register_callback.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetrics")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_exists(
        self, mock_exporter, mock_reader, mock_meter_provider, mock_statsbeat_metrics, mock_get_manager
    ):
        """Test that collect_statsbeat_metrics reuses existing configuration when called multiple times with same config."""  # pylint: disable=line-too-long
        # Arrange
        exporter = mock.Mock()
        exporter._endpoint = "test endpoint"
        exporter._instrumentation_key = "test ikey"
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        # Set up mock returns
        mock_exporter_instance = mock.Mock()
        mock_exporter.return_value = mock_exporter_instance

        mock_reader_instance = mock.Mock()
        mock_reader.return_value = mock_reader_instance

        mock_meter_provider_instance = mock.Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        flush_mock = mock.Mock()
        mock_meter_provider_instance.force_flush = flush_mock

        mock_statsbeat_metrics_instance = mock.Mock()
        mock_statsbeat_metrics.return_value = mock_statsbeat_metrics_instance

        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        # Act - Initialize first time
        _statsbeat.collect_statsbeat_metrics(exporter)
        first_metrics = manager._metrics
        self.assertTrue(manager._initialized)
        self.assertEqual(first_metrics, mock_statsbeat_metrics_instance)

        # Verify first initialization called the mocks
        self.assertEqual(mock_statsbeat_metrics.call_count, 1)
        self.assertEqual(mock_meter_provider.call_count, 1)

        # Act - Initialize second time with same config
        _statsbeat.collect_statsbeat_metrics(exporter)
        second_metrics = manager._metrics

        # Assert - should reuse existing config since it's the same
        self.assertTrue(manager._initialized)
        self.assertIsNotNone(second_metrics)
        self.assertEqual(first_metrics, second_metrics)

        # Verify mocks were NOT called again since config is the same
        self.assertEqual(mock_statsbeat_metrics.call_count, 1)  # Still only called once
        self.assertEqual(mock_meter_provider.call_count, 1)  # Still only called once

        # Verify only one call to flush (from first initialization)
        flush_mock.assert_called_once()
        mock_statsbeat_metrics_instance.init_non_initial_metrics.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_non_eu(self, mock_exporter, mock_reader, mock_meter_provider, mock_get_manager):
        """Test collect_statsbeat_metrics with non-EU endpoint uses correct connection string."""
        # Arrange
        exporter = mock.Mock()
        exporter._instrumentation_key = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3333"
        exporter._endpoint = "https://westus-0.in.applicationinsights.azure.com/"
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        # Set up mock returns
        mock_exporter_instance = mock.Mock()
        mock_exporter.return_value = mock_exporter_instance

        mock_reader_instance = mock.Mock()
        mock_reader.return_value = mock_reader_instance

        mock_meter_provider_instance = mock.Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        flush_mock = mock.Mock()
        mock_meter_provider_instance.force_flush = flush_mock

        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        with mock.patch.dict(
            os.environ,
            {
                _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME: "",
            },
        ):
            # Act
            _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert
        self.assertTrue(manager._initialized)
        self.assertIsNotNone(manager._metrics)

        # Verify that AzureMonitorMetricExporter was called with the correct connection string
        mock_exporter.assert_called_once()
        call_args = mock_exporter.call_args
        # The connection string should be the non-EU default since the endpoint is non-EU
        expected_connection_string = call_args[1]["connection_string"]
        self.assertIn(_DEFAULT_NON_EU_STATS_CONNECTION_STRING.split(";", maxsplit=1)[0], expected_connection_string)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_eu(self, mock_exporter, mock_reader, mock_meter_provider, mock_get_manager):
        """Test collect_statsbeat_metrics with EU endpoint uses correct connection string."""
        # Arrange
        exporter = mock.Mock()
        exporter._instrumentation_key = "1aa11111-bbbb-1ccc-8ddd-eeeeffff3333"
        exporter._endpoint = "https://northeurope-0.in.applicationinsights.azure.com/"
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        # Set up mock returns
        mock_exporter_instance = mock.Mock()
        mock_exporter.return_value = mock_exporter_instance

        mock_reader_instance = mock.Mock()
        mock_reader.return_value = mock_reader_instance

        mock_meter_provider_instance = mock.Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        flush_mock = mock.Mock()
        mock_meter_provider_instance.force_flush = flush_mock

        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        with mock.patch.dict(
            os.environ,
            {
                _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME: "",
            },
        ):
            # Act
            _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert
        self.assertTrue(manager._initialized)
        self.assertIsNotNone(manager._metrics)

        # Verify that AzureMonitorMetricExporter was called with the correct connection string
        mock_exporter.assert_called_once()
        call_args = mock_exporter.call_args
        # The connection string should be the EU default since the endpoint is EU
        expected_connection_string = call_args[1]["connection_string"]
        self.assertIn(_DEFAULT_EU_STATS_CONNECTION_STRING.split(";", maxsplit=1)[0], expected_connection_string)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_aad(
        self, mock_exporter, mock_reader, mock_meter_provider, mock_get_manager
    ):  # pylint: disable=unused-argument
        """Test collect_statsbeat_metrics with AAD credentials."""
        # Arrange
        exporter = mock.Mock()
        TEST_ENDPOINT = "test endpoint"
        TEST_IKEY = "test ikey"
        TEST_CREDENTIAL = "test credential"
        exporter._endpoint = TEST_ENDPOINT
        exporter._instrumentation_key = TEST_IKEY
        exporter._disable_offline_storage = False
        exporter._credential = TEST_CREDENTIAL
        exporter._distro_version = ""
        mp_mock = mock.Mock()
        mock_meter_provider.return_value = mp_mock
        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - Verify _StatsbeatMetrics was called with correct parameters
        self.assertIsNotNone(manager._metrics)
        self.assertEqual(manager._metrics._ikey, TEST_IKEY)
        self.assertTrue(manager._metrics._feature >= _StatsbeatFeature.AAD)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_no_aad(
        self, mock_exporter, mock_reader, mock_meter_provider, mock_get_manager
    ):  # pylint: disable=line-too-long, unused-argument
        """Test collect_statsbeat_metrics without AAD credentials."""
        # Arrange
        exporter = mock.Mock()
        TEST_ENDPOINT = "test endpoint"
        TEST_IKEY = "test ikey"
        TEST_CREDENTIAL = None
        exporter._endpoint = TEST_ENDPOINT
        exporter._instrumentation_key = TEST_IKEY
        exporter._disable_offline_storage = False
        exporter._credential = TEST_CREDENTIAL
        exporter._distro_version = ""
        mp_mock = mock.Mock()
        mock_meter_provider.return_value = mp_mock
        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - Verify _StatsbeatMetrics was called with correct parameters
        self.assertIsNotNone(manager._metrics)
        self.assertEqual(manager._metrics._ikey, TEST_IKEY)
        self.assertTrue(manager._metrics._feature < _StatsbeatFeature.AAD)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_distro_version(  # pylint: disable=name-too-long
        self, mock_exporter, mock_reader, mock_meter_provider, mock_get_manager  # pylint: disable=unused-argument
    ):
        """Test collect_statsbeat_metrics with distribution version."""
        # Arrange
        exporter = mock.Mock()
        TEST_ENDPOINT = "test endpoint"
        TEST_IKEY = "test ikey"
        TEST_CREDENTIAL = None
        exporter._endpoint = TEST_ENDPOINT
        exporter._instrumentation_key = TEST_IKEY
        exporter._disable_offline_storage = False
        exporter._credential = TEST_CREDENTIAL
        exporter._distro_version = "1.0.0"
        mp_mock = mock.Mock()
        mock_meter_provider.return_value = mp_mock
        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - Verify _StatsbeatMetrics was called with correct parameters
        self.assertIsNotNone(manager._metrics)
        self.assertEqual(manager._metrics._ikey, TEST_IKEY)
        self.assertTrue(manager._metrics._feature > _StatsbeatFeature.DISTRO)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    def test_collect_statsbeat_metrics_local_storage(  # pylint: disable=name-too-long
        self, mock_exporter, mock_reader, mock_meter_provider, mock_get_manager  # pylint: disable=unused-argument
    ):
        """Test collect_statsbeat_metrics with local storage."""
        # Arrange
        exporter = mock.Mock()
        TEST_ENDPOINT = "test endpoint"
        TEST_IKEY = "test ikey"
        TEST_CREDENTIAL = None
        exporter._endpoint = TEST_ENDPOINT
        exporter._instrumentation_key = TEST_IKEY
        exporter._disable_offline_storage = False
        exporter._credential = TEST_CREDENTIAL
        exporter._distro_version = ""
        mp_mock = mock.Mock()
        mock_meter_provider.return_value = mp_mock
        manager = StatsbeatManager()
        self.assertFalse(manager._initialized)
        mock_get_manager.return_value = manager

        # Act
        _statsbeat.collect_statsbeat_metrics(exporter)

        # Assert - Verify _StatsbeatMetrics was called with correct parameters
        self.assertIsNotNone(manager._metrics)
        self.assertEqual(manager._metrics._ikey, TEST_IKEY)
        self.assertTrue(manager._metrics._feature >= _StatsbeatFeature.DISK_RETRY)

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics._StatsbeatMetrics")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @mock.patch("azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter")
    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    def test_shutdown_statsbeat_metrics(
        self, mock_get_manager, mock_exporter, mock_reader, mock_meter_provider, mock_statsbeat_metrics
    ):
        """Test shutdown_statsbeat_metrics after initialization."""
        # Arrange - First initialize statsbeat
        exporter = mock.Mock()
        exporter._endpoint = "test endpoint"
        exporter._region = "testregion"  # Add missing region
        exporter._instrumentation_key = "test ikey"
        exporter._disable_offline_storage = False
        exporter._credential = None
        exporter._distro_version = ""

        # Set up mock returns
        mock_exporter_instance = mock.Mock()
        mock_exporter.return_value = mock_exporter_instance

        mock_reader_instance = mock.Mock()
        mock_reader.return_value = mock_reader_instance

        mock_meter_provider_instance = mock.Mock()
        mock_meter_provider.return_value = mock_meter_provider_instance
        flush_mock = mock.Mock()
        shutdown_mock = mock.Mock(return_value=True)
        mock_meter_provider_instance.force_flush = flush_mock
        mock_meter_provider_instance.shutdown = shutdown_mock

        mock_statsbeat_metrics_instance = mock.Mock()
        mock_statsbeat_metrics.return_value = mock_statsbeat_metrics_instance

        # Create a real manager instance for initialization
        manager = StatsbeatManager()

        # Mock get_statsbeat_manager to return our initialized manager
        mock_get_manager.return_value = manager

        # Act - Initialize first
        _statsbeat.collect_statsbeat_metrics(exporter)
        self.assertTrue(manager.is_initialized())
        self.assertFalse(_STATSBEAT_STATE["SHUTDOWN"])

        # Act - Test shutdown
        result = _statsbeat.shutdown_statsbeat_metrics()

        # Assert
        self.assertTrue(result)
        self.assertFalse(manager.is_initialized())
        self.assertTrue(_STATSBEAT_STATE["SHUTDOWN"])
        assert mock_get_manager.call_count == 2

    @mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager")
    def test_shutdown_statsbeat_metrics_not_initialized(self, mock_get_manager):  # pylint: disable=name-too-long
        """Test shutdown when statsbeat is not initialized."""
        # Arrange
        manager = StatsbeatManager()
        self.assertFalse(manager.is_initialized())

        # Mock get_statsbeat_manager to return our uninitialized manager
        mock_get_manager.return_value = manager

        # Act - Test shutdown when not initialized
        result = _statsbeat.shutdown_statsbeat_metrics()

        # Assert
        self.assertFalse(result)  # Should return False when not initialized
        self.assertFalse(manager.is_initialized())
        mock_get_manager.assert_called_once()


# cSpell:enable
