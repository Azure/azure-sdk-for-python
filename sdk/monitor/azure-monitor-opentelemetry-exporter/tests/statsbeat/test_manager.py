# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import unittest
from unittest import mock
from unittest.mock import Mock, patch

from azure.monitor.opentelemetry.exporter.statsbeat._manager import StatsbeatConfig, StatsbeatManager
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL,
    _DEFAULT_EU_STATS_CONNECTION_STRING,
    _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
)

# cSpell:disable


# pylint: disable=too-many-public-methods
# pylint: disable=protected-access, line-too-long, unused-argument
class TestStatsbeatConfig(unittest.TestCase):
    def setUp(self):
        os.environ.pop(_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL, None)

    def test_init_basic(self):
        """Test basic initialization of StatsbeatConfig."""
        config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
        )

        self.assertEqual(config.endpoint, "https://westus-1.in.applicationinsights.azure.com/")
        self.assertEqual(config.region, "westus")
        self.assertEqual(config.instrumentation_key, "test-key")
        self.assertFalse(config.disable_offline_storage)
        self.assertIsNone(config.credential)
        self.assertIsNone(config.distro_version)
        self.assertIsNotNone(config.connection_string)

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            disable_offline_storage=True,
            credential=mock.Mock(),
            distro_version="1.0.0",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
        )

        self.assertEqual(config.endpoint, "https://westus-1.in.applicationinsights.azure.com/")
        self.assertEqual(config.region, "westus")
        self.assertEqual(config.instrumentation_key, "test-key")
        self.assertTrue(config.disable_offline_storage)
        self.assertIsNotNone(config.credential)
        self.assertEqual(config.distro_version, "1.0.0")
        self.assertEqual(
            config.connection_string,
            "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
        )

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._get_stats_connection_string")
    def test_init_invalid_connection_string_fallback(self, mock_get_stats_cs):
        """Test that invalid connection string falls back to default."""
        mock_get_stats_cs.return_value = "InstrumentationKey=fallback;IngestionEndpoint=https://fallback.com/"

        config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string="invalid-connection-string",
        )

        self.assertEqual(
            config.connection_string, "InstrumentationKey=fallback;IngestionEndpoint=https://fallback.com/"
        )
        mock_get_stats_cs.assert_called_once()

    def test_from_exporter_valid(self):
        """Test creating config from a valid exporter."""
        exporter = mock.Mock()
        exporter._endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        exporter._region = "westus"
        exporter._instrumentation_key = "test-key"
        exporter._disable_offline_storage = True
        exporter._credential = mock.Mock()
        exporter._distro_version = "1.0.0"

        config = StatsbeatConfig.from_exporter(exporter)

        self.assertIsNotNone(config)
        if config:
            self.assertEqual(config.endpoint, "https://westus-1.in.applicationinsights.azure.com/")
            self.assertEqual(config.region, "westus")
            self.assertEqual(config.instrumentation_key, "test-key")
            # config.disable_offline_storage mirrors the user's setting (used only for DISK_RETRY
            # reporting); statsbeat's own exporter never persists to disk regardless (see _do_initialize).
            self.assertTrue(config.disable_offline_storage)
            self.assertIsNotNone(config.credential)
            self.assertEqual(config.distro_version, "1.0.0")

    def test_from_exporter_missing_instrumentation_key(self):
        """Test creating config from exporter missing instrumentation key."""
        exporter = mock.Mock()
        exporter._endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        exporter._region = "westus"
        exporter._instrumentation_key = None

        config = StatsbeatConfig.from_exporter(exporter)
        self.assertIsNone(config)

    def test_from_exporter_missing_endpoint(self):
        """Test creating config from exporter missing endpoint."""
        exporter = mock.Mock()
        exporter._endpoint = None
        exporter._region = "westus"
        exporter._instrumentation_key = "test-key"

        config = StatsbeatConfig.from_exporter(exporter)
        self.assertIsNone(config)

    def test_from_exporter_missing_region(self):
        """Test creating config from exporter missing region."""
        exporter = mock.Mock()
        exporter._endpoint = "https://westus-1.in.applicationinsights.azure.com/"
        exporter._region = None
        exporter._instrumentation_key = "test-key"

        config = StatsbeatConfig.from_exporter(exporter)
        self.assertIsNone(config)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._get_connection_string_for_region_from_config")
    def test_from_config_valid(self, mock_get_cs_for_region):
        """Test creating config from base config and dictionary."""
        mock_get_cs_for_region.return_value = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/"

        base_config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            credential="test_credential",
            disable_offline_storage=True,
            distro_version="1.0.0",
        )

        # A conflicting value in the dict must be ignored: the customer's setting is preserved from
        # base_config, and statsbeat's own storage is never controlled by OneSettings.
        config_dict = {"disable_offline_storage": "false"}

        new_config = StatsbeatConfig.from_config(base_config, config_dict)

        self.assertIsNotNone(new_config)
        if new_config:
            self.assertEqual(new_config.endpoint, base_config.endpoint)
            self.assertEqual(new_config.region, base_config.region)
            self.assertEqual(new_config.instrumentation_key, base_config.instrumentation_key)
            self.assertTrue(new_config.disable_offline_storage)
            self.assertEqual(new_config.credential, "test_credential")
            self.assertEqual(new_config.distro_version, "1.0.0")
            self.assertEqual(
                new_config.connection_string,
                "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
            )

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._get_connection_string_for_region_from_config")
    def test_from_config_fallback_connection_string(self, mock_get_cs_for_region):
        """Test that from_config falls back to base config connection string when needed."""
        mock_get_cs_for_region.return_value = None

        base_config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string="InstrumentationKey=base;IngestionEndpoint=https://base.com/",
        )

        config_dict = {}

        new_config = StatsbeatConfig.from_config(base_config, config_dict)

        self.assertIsNotNone(new_config)
        if new_config:
            self.assertEqual(new_config.connection_string, base_config.connection_string)

    def test_from_config_missing_instrumentation_key(self):
        """Test from_config with missing instrumentation key."""
        base_config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/", region="westus", instrumentation_key=""
        )

        result = StatsbeatConfig.from_config(base_config, {})
        self.assertIsNone(result)

    def test_equality(self):
        """Test equality comparison between configs."""
        config1 = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/",
        )

        config2 = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/",
        )

        config3 = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            disable_offline_storage=True,
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/",
        )

        self.assertEqual(config1, config2)
        self.assertNotEqual(config1, config3)
        self.assertNotEqual(config1, "not a config")

    def test_hash(self):
        """Test hash function for configs."""
        config1 = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/",
        )

        config2 = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/",
        )

        config3 = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            disable_offline_storage=True,
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/",
        )

        self.assertEqual(hash(config1), hash(config2))
        self.assertNotEqual(hash(config1), hash(config3))


# pylint: disable=protected-access
class TestStatsbeatManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        os.environ[_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL] = "false"
        # Reset singleton state - only clear StatsbeatManager instances
        if StatsbeatManager in StatsbeatManager._instances:
            del StatsbeatManager._instances[StatsbeatManager]
        # Reset statsbeat state
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["SHUTDOWN"] = False
            _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
            _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 0

        # Create a fresh manager instance
        self.manager = StatsbeatManager()
        if hasattr(self.manager, "_initialized"):
            self.manager._initialized = False
        if hasattr(self.manager, "_config"):
            self.manager._config = None
        if hasattr(self.manager, "_metrics"):
            self.manager._metrics = None
        if hasattr(self.manager, "_meter_provider"):
            self.manager._meter_provider = None
        if hasattr(self.manager, "_warmup_timer"):
            self.manager._warmup_timer = None
        if hasattr(self.manager, "_exporter"):
            self.manager._exporter = None

    def tearDown(self):
        """Clean up after tests."""
        try:
            if hasattr(self, "manager"):
                self.manager.shutdown()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        os.environ.pop(_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL, None)
        # Reset singleton state - only clear StatsbeatManager instances
        if StatsbeatManager in StatsbeatManager._instances:
            del StatsbeatManager._instances[StatsbeatManager]

    def _create_valid_config(
        self,
        connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
        disable_offline_storage=False,
    ):
        """Helper to create a valid StatsbeatConfig."""
        return StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
            connection_string=connection_string,
            disable_offline_storage=True,
        )

    def test_singleton_behavior(self):
        """Test that StatsbeatManager follows singleton pattern."""
        manager1 = StatsbeatManager()
        manager2 = StatsbeatManager()
        self.assertIs(manager1, manager2)

    def test_validate_config_valid(self):
        """Test _validate_config with valid configuration."""
        config = self._create_valid_config()
        self.assertTrue(StatsbeatManager._validate_config(config))

    def test_validate_config_none(self):
        """Test _validate_config with None configuration."""
        self.assertFalse(StatsbeatManager._validate_config(None))  # type: ignore

    def test_validate_config_missing_instrumentation_key(self):
        """Test _validate_config with missing instrumentation key."""
        config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/", region="westus", instrumentation_key=""
        )
        self.assertFalse(StatsbeatManager._validate_config(config))

    def test_validate_config_missing_endpoint(self):
        """Test _validate_config with missing endpoint."""
        config = StatsbeatConfig(endpoint="", region="westus", instrumentation_key="test-key")
        self.assertFalse(StatsbeatManager._validate_config(config))

    def test_validate_config_missing_region(self):
        """Test _validate_config with missing region."""
        config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/", region="", instrumentation_key="test-key"
        )
        self.assertFalse(StatsbeatManager._validate_config(config))

    def test_validate_config_missing_connection_string(self):
        """Test _validate_config with missing connection string."""
        config = StatsbeatConfig(
            endpoint="https://westus-1.in.applicationinsights.azure.com/",
            region="westus",
            instrumentation_key="test-key",
        )
        config.connection_string = ""
        self.assertFalse(StatsbeatManager._validate_config(config))

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.is_statsbeat_enabled")
    def test_initialize_statsbeat_disabled(self, mock_is_enabled):
        """Test initialize when statsbeat is disabled."""
        mock_is_enabled.return_value = False
        config = self._create_valid_config()

        result = self.manager.initialize(config)

        self.assertFalse(result)
        self.assertFalse(self.manager._initialized)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._state.is_statsbeat_enabled")
    def test_initialize_invalid_config(self, mock_is_enabled):
        """Test initialize with invalid configuration."""
        mock_is_enabled.return_value = True

        result = self.manager.initialize(None)  # type: ignore

        self.assertFalse(result)
        self.assertFalse(self.manager._initialized)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetrics")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.threading.Timer")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._state.is_statsbeat_enabled")
    def test_initialize_success(
        self,
        mock_is_enabled,
        mock_timer_class,
        mock_statsbeat_metrics,
        mock_exporter_class,
        mock_reader_class,
        mock_meter_provider_class,
    ):
        """Test successful initialization."""
        mock_is_enabled.return_value = True

        # Mock the exporter
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter

        # Mock the reader
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader

        # Mock the meter provider
        mock_meter_provider = Mock()
        mock_meter_provider_class.return_value = mock_meter_provider

        # Mock the statsbeat metrics
        mock_metrics = Mock()
        mock_statsbeat_metrics.return_value = mock_metrics
        mock_timer_class.return_value = Mock()

        config = self._create_valid_config()

        result = self.manager.initialize(config)

        self.assertTrue(result)
        self.assertTrue(self.manager._initialized)
        self.assertEqual(self.manager._config, config)
        self.assertEqual(self.manager._meter_provider, mock_meter_provider)
        self.assertEqual(self.manager._metrics, mock_metrics)

        # Verify mocks were called correctly
        mock_exporter_class.assert_called_once()
        mock_reader_class.assert_called_once()
        mock_meter_provider_class.assert_called_once()
        mock_statsbeat_metrics.assert_called_once()
        mock_timer_class.assert_called_once()
        mock_timer_class.return_value.start.assert_called_once()
        mock_meter_provider.force_flush.assert_not_called()
        mock_metrics.init_non_initial_metrics.assert_called_once()

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.threading.Timer")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetrics")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._state.is_statsbeat_enabled")
    def test_initialize_with_delay_schedules_non_blocking_flush(
        self,
        mock_is_enabled,
        mock_statsbeat_metrics,
        mock_exporter_class,
        mock_reader_class,
        mock_meter_provider_class,
        mock_timer_class,
    ):
        """Test delayed initial statsbeat flush is scheduled asynchronously."""
        mock_is_enabled.return_value = True

        mock_exporter_class.return_value = Mock()
        mock_reader_class.return_value = Mock()
        mock_meter_provider = Mock()
        mock_meter_provider_class.return_value = mock_meter_provider
        mock_metrics = Mock()
        mock_statsbeat_metrics.return_value = mock_metrics

        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer

        result = self.manager.initialize(self._create_valid_config())

        self.assertTrue(result)
        mock_timer_class.assert_called_once()
        self.assertEqual(mock_timer_class.call_args[0][0], 15)
        mock_timer.start.assert_called_once()
        mock_meter_provider.force_flush.assert_not_called()

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._state.is_statsbeat_enabled")
    def test_initialize_failure_exception(
        self, mock_is_enabled, mock_exporter_class, mock_reader_class, mock_meter_provider_class
    ):
        """Test initialization failure due to exception."""
        mock_is_enabled.return_value = True
        mock_exporter_class.side_effect = ValueError("Test error")

        config = self._create_valid_config()

        result = self.manager.initialize(config)

        self.assertFalse(result)
        self.assertFalse(self.manager._initialized)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._state.is_statsbeat_enabled")
    def test_initialize_already_initialized_same_config(self, mock_is_enabled):
        """Test initialize when already initialized with same config."""
        mock_is_enabled.return_value = True
        config = self._create_valid_config()

        # Mock initialized state
        self.manager._initialized = True
        self.manager._config = config

        result = self.manager.initialize(config)

        self.assertTrue(result)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.is_statsbeat_enabled")
    def test_initialize_already_initialized_different_config_cs(self, mock_is_enabled):
        """Test initialize when already initialized with different config."""
        mock_is_enabled.return_value = True

        old_config = self._create_valid_config()
        new_config = StatsbeatConfig(
            endpoint="https://eastus-1.in.applicationinsights.azure.com/",
            region="eastus",
            instrumentation_key="different-key",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://eastus-0.in.applicationinsights.azure.com/",
        )

        # Mock initialized state
        self.manager._initialized = True
        self.manager._config = old_config

        with patch.object(self.manager, "_reconfigure") as mock_reconfigure:
            mock_reconfigure.return_value = True
            result = self.manager.initialize(new_config)

            self.assertTrue(result)
            mock_reconfigure.assert_called_once_with(new_config)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.is_statsbeat_enabled")
    def test_initialize_already_initialized_different_config_storage(self, mock_is_enabled):
        """Test initialize when already initialized with different config."""
        mock_is_enabled.return_value = True

        old_config = self._create_valid_config()
        new_config = StatsbeatConfig(
            endpoint="https://eastus-1.in.applicationinsights.azure.com/",
            region="eastus",
            instrumentation_key="different-key",
            disable_offline_storage=False,
        )

        # Mock initialized state
        self.manager._initialized = True
        self.manager._config = old_config

        with patch.object(self.manager, "_reconfigure") as mock_reconfigure:
            mock_reconfigure.return_value = True
            result = self.manager.initialize(new_config)

            self.assertTrue(result)
            mock_reconfigure.assert_called_once_with(new_config)

    def test_shutdown_not_initialized(self):
        """Test shutdown when not initialized."""
        result = self.manager.shutdown()
        self.assertFalse(result)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.set_statsbeat_shutdown")
    def test_shutdown_success(self, mock_set_shutdown):
        """Test successful shutdown."""
        # Mock initialized state
        self.manager._initialized = True
        mock_meter_provider = Mock()
        self.manager._meter_provider = mock_meter_provider

        result = self.manager.shutdown()

        self.assertTrue(result)
        self.assertFalse(self.manager._initialized)
        self.assertIsNone(self.manager._meter_provider)
        self.assertIsNone(self.manager._metrics)
        self.assertIsNone(self.manager._config)
        mock_meter_provider.shutdown.assert_called_once()
        mock_set_shutdown.assert_called_once_with(True)

        # Singleton is not cleared upon shutdown
        manager2 = StatsbeatManager()
        self.assertIs(self.manager, manager2)

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._state.set_statsbeat_shutdown")
    def test_shutdown_meter_provider_exception(self, mock_set_shutdown):
        """Test shutdown when meter provider raises exception."""
        # Mock initialized state
        self.manager._initialized = True
        mock_meter_provider = Mock()
        mock_meter_provider.shutdown.side_effect = Exception("Shutdown error")
        self.manager._meter_provider = mock_meter_provider

        result = self.manager.shutdown()

        self.assertFalse(result)
        self.assertFalse(self.manager._initialized)
        self.assertIsNone(self.manager._meter_provider)
        self.assertIsNone(self.manager._metrics)
        self.assertIsNone(self.manager._config)
        # Should be called once in try block, even though it failed
        mock_meter_provider.shutdown.assert_called_once()
        mock_set_shutdown.assert_not_called()

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.PeriodicExportingMetricReader")
    @patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetrics")
    def test_reconfigure_success(
        self, mock_statsbeat_metrics, mock_exporter_class, mock_reader_class, mock_meter_provider_class
    ):
        """Test successful reconfiguration."""
        # Mock initialized state with old config
        old_config = self._create_valid_config()
        self.manager._initialized = True
        self.manager._config = old_config
        mock_old_meter_provider = Mock()
        self.manager._meter_provider = mock_old_meter_provider

        # Mock new components
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_meter_provider = Mock()
        mock_meter_provider_class.return_value = mock_meter_provider
        mock_metrics = Mock()
        mock_statsbeat_metrics.return_value = mock_metrics

        new_config = StatsbeatConfig(
            endpoint="https://eastus-1.in.applicationinsights.azure.com/",
            region="eastus",
            instrumentation_key="new-key",
            connection_string="InstrumentationKey=new;IngestionEndpoint=https://new.com/",
        )

        result = self.manager._reconfigure(new_config)

        self.assertTrue(result)
        self.assertTrue(self.manager._initialized)
        self.assertEqual(self.manager._config, new_config)

        # Verify old meter provider was shutdown
        mock_old_meter_provider.force_flush.assert_called_once()
        mock_old_meter_provider.shutdown.assert_called_once()

    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.MeterProvider")
    def test_reconfigure_flush_failure(self, mock_meter_provider_class):
        """Test reconfiguration failure."""
        # Mock initialized state
        old_config = self._create_valid_config()
        self.manager._initialized = True
        self.manager._config = old_config
        mock_old_meter_provider = Mock()
        self.manager._meter_provider = mock_old_meter_provider

        mock_meter_provider_class.force_flush.side_effect = Exception("Reconfigure error")

        new_config = StatsbeatConfig(
            endpoint="https://eastus-1.in.applicationinsights.azure.com/",
            region="eastus",
            instrumentation_key="new-key",
            connection_string="InstrumentationKey=new;IngestionEndpoint=https://new.com/",
        )

        result = self.manager._reconfigure(new_config)

        # We still reinitialize the manager state even on flush/shutdown failure
        self.assertTrue(result)
        self.assertTrue(self.manager._initialized)

    # ========================================================================
    # UPDATE ENDPOINT (INGESTION REDIRECT) TESTS
    # ========================================================================

    def _setup_initialized_manager_for_update(self, connection_string=_DEFAULT_NON_EU_STATS_CONNECTION_STRING):
        """Put the manager in an initialized state with a mock exporter attached."""
        config = StatsbeatConfig(
            endpoint="https://dc.services.visualstudio.com",
            region="",
            instrumentation_key="test-key",
            connection_string=connection_string,
            disable_offline_storage=True,
        )
        exporter = Mock()
        exporter.client._config.host = "https://dc.services.visualstudio.com"
        exporter._update_connection_string.return_value = True
        self.manager._config = config
        self.manager._exporter = exporter
        self.manager._metrics = Mock()
        self.manager._meter_provider = Mock()
        self.manager._initialized = True
        return exporter

    def test_update_endpoint_empty_endpoint(self):
        self._setup_initialized_manager_for_update()
        self.assertFalse(self.manager.update_endpoint(""))

    def test_update_endpoint_not_initialized(self):
        self.manager._initialized = False
        self.manager._config = None
        self.assertFalse(self.manager.update_endpoint("https://westeurope-5.in.applicationinsights.azure.com/"))

    def test_update_endpoint_statsbeat_disabled(self):
        self._setup_initialized_manager_for_update()
        os.environ[_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL] = "true"
        try:
            self.assertFalse(self.manager.update_endpoint("https://westeurope-5.in.applicationinsights.azure.com/"))
        finally:
            os.environ[_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL] = "false"

    def test_update_endpoint_after_shutdown(self):
        self._setup_initialized_manager_for_update()
        with _STATSBEAT_STATE_LOCK:
            _STATSBEAT_STATE["SHUTDOWN"] = True
        try:
            self.assertFalse(self.manager.update_endpoint("https://westeurope-5.in.applicationinsights.azure.com/"))
        finally:
            with _STATSBEAT_STATE_LOCK:
                _STATSBEAT_STATE["SHUTDOWN"] = False

    def test_update_endpoint_unchanged_endpoint(self):
        self._setup_initialized_manager_for_update()
        self.assertFalse(self.manager.update_endpoint("https://dc.services.visualstudio.com"))

    def test_update_endpoint_row_to_eu_repoints_exporter(self):
        """A redirect into the EU boundary swaps the statsbeat destination in place."""
        exporter = self._setup_initialized_manager_for_update()
        meter_provider = self.manager._meter_provider
        metrics = self.manager._metrics

        result = self.manager.update_endpoint("https://westeurope-5.in.applicationinsights.azure.com/")

        self.assertTrue(result)
        self.assertEqual(self.manager._config.connection_string, _DEFAULT_EU_STATS_CONNECTION_STRING)
        self.assertEqual(self.manager._config.endpoint, "https://westeurope-5.in.applicationinsights.azure.com/")
        self.assertEqual(self.manager._config.region, "westeurope")
        exporter._update_connection_string.assert_called_once_with(_DEFAULT_EU_STATS_CONNECTION_STRING)
        # Metric infrastructure is preserved, only the host dimension is refreshed.
        self.assertIs(self.manager._meter_provider, meter_provider)
        self.assertIs(self.manager._metrics, metrics)
        metrics.update_endpoint_host.assert_called_once_with("https://westeurope-5.in.applicationinsights.azure.com/")

    def test_update_endpoint_same_boundary_keeps_exporter_route(self):
        """A redirect within the same data boundary refreshes host/config but not the destination."""
        exporter = self._setup_initialized_manager_for_update()

        result = self.manager.update_endpoint("https://eastus-8.in.applicationinsights.azure.com/")

        self.assertTrue(result)
        self.assertEqual(self.manager._config.connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)
        self.assertEqual(self.manager._config.endpoint, "https://eastus-8.in.applicationinsights.azure.com/")
        self.assertEqual(self.manager._config.region, "eastus")
        # Destination is unchanged - the exporter was never repointed.
        self.assertEqual(exporter.client._config.host, "https://dc.services.visualstudio.com")
        exporter._update_connection_string.assert_not_called()
        self.manager._metrics.update_endpoint_host.assert_called_once_with(
            "https://eastus-8.in.applicationinsights.azure.com/"
        )

    def test_update_endpoint_eu_to_row_repoints_exporter(self):
        exporter = self._setup_initialized_manager_for_update(
            connection_string=_DEFAULT_EU_STATS_CONNECTION_STRING,
        )

        result = self.manager.update_endpoint("https://westus-0.in.applicationinsights.azure.com/")

        self.assertTrue(result)
        self.assertEqual(self.manager._config.connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)
        exporter._update_connection_string.assert_called_once_with(_DEFAULT_NON_EU_STATS_CONNECTION_STRING)

    def test_update_endpoint_no_exporter_available(self):
        """Without a live exporter a boundary change cannot be applied, so nothing is mutated."""
        self._setup_initialized_manager_for_update()
        self.manager._exporter = None

        result = self.manager.update_endpoint("https://westeurope-5.in.applicationinsights.azure.com/")

        self.assertFalse(result)
        self.assertEqual(self.manager._config.connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)
        self.assertEqual(self.manager._config.endpoint, "https://dc.services.visualstudio.com")

    def test_update_endpoint_unparseable_connection_string_is_refused(self):
        """If the derived statsbeat connection string is unusable, the route is left untouched."""
        exporter = self._setup_initialized_manager_for_update()
        exporter._update_connection_string.return_value = False

        result = self.manager.update_endpoint("https://westeurope-5.in.applicationinsights.azure.com/")

        self.assertFalse(result)
        # Neither the exporter nor the stored config moved off the original ROW route.
        self.assertEqual(exporter.client._config.host, "https://dc.services.visualstudio.com")
        self.assertEqual(self.manager._config.connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)
        self.assertEqual(self.manager._config.endpoint, "https://dc.services.visualstudio.com")
        self.manager._metrics.update_endpoint_host.assert_not_called()

    def test_update_endpoint_swallows_exceptions(self):
        self._setup_initialized_manager_for_update()
        self.manager._metrics.update_endpoint_host.side_effect = Exception("boom")

        self.assertFalse(self.manager.update_endpoint("https://eastus-8.in.applicationinsights.azure.com/"))

    def test_get_current_config_not_initialized(self):
        result = self.manager.get_current_config()
        self.assertIsNone(result)

    def test_get_current_config_initialized(self):
        """Test get_current_config when initialized."""
        original_config = self._create_valid_config()
        self.manager._config = original_config

        result = self.manager.get_current_config()

        self.assertIsNotNone(result)
        if result:
            # Should be a copy, not the same object
            self.assertIsNot(result, original_config)
            self.assertEqual(result.endpoint, original_config.endpoint)
            self.assertEqual(result.region, original_config.region)
            self.assertEqual(result.instrumentation_key, original_config.instrumentation_key)

    def test_cleanup_with_shutdown(self):
        """Test internal cleanup method with meter provider shutdown."""
        # Mock initialized state
        self.manager._initialized = True
        mock_meter_provider = Mock()
        self.manager._meter_provider = mock_meter_provider
        mock_timer = Mock()
        self.manager._warmup_timer = mock_timer
        self.manager._metrics = Mock()
        config_mock = Mock()
        self.manager._config = config_mock

        self.manager._cleanup(shutdown_meter_provider=True)

        self.assertFalse(self.manager._initialized)
        self.assertIsNone(self.manager._meter_provider)
        self.assertIsNone(self.manager._metrics)
        self.assertIsNone(self.manager._warmup_timer)
        # Config is intact for potential re-initialization
        self.assertEqual(self.manager._config, config_mock)
        mock_timer.cancel.assert_called_once()
        mock_meter_provider.shutdown.assert_called_once()

    def test_cleanup_without_shutdown(self):
        """Test internal cleanup method without meter provider shutdown."""
        # Mock initialized state
        self.manager._initialized = True
        mock_meter_provider = Mock()
        self.manager._meter_provider = mock_meter_provider
        mock_timer = Mock()
        self.manager._warmup_timer = mock_timer
        self.manager._metrics = Mock()
        config_mock = Mock()
        self.manager._config = config_mock

        self.manager._cleanup(shutdown_meter_provider=False)

        self.assertFalse(self.manager._initialized)
        self.assertIsNone(self.manager._meter_provider)
        self.assertIsNone(self.manager._metrics)
        self.assertIsNone(self.manager._warmup_timer)
        # Config is intact for potential re-initialization
        self.assertEqual(self.manager._config, config_mock)
        mock_timer.cancel.assert_called_once()
        mock_meter_provider.shutdown.assert_not_called()

    def test_cleanup_meter_provider_exception(self):
        """Test cleanup when meter provider shutdown raises exception."""
        # Mock initialized state
        self.manager._initialized = True
        mock_meter_provider = Mock()
        mock_meter_provider.shutdown.side_effect = Exception("Cleanup error")
        self.manager._meter_provider = mock_meter_provider
        self.manager._metrics = Mock()
        config_mock = Mock()
        self.manager._config = config_mock

        # Should not raise exception
        self.manager._cleanup(shutdown_meter_provider=True)

        self.assertFalse(self.manager._initialized)
        self.assertIsNone(self.manager._meter_provider)
        self.assertIsNone(self.manager._metrics)
        # Config is intact for potential re-initialization
        self.assertEqual(self.manager._config, config_mock)
        mock_meter_provider.shutdown.assert_called_once()
