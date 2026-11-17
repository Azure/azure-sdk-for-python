# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import threading
import unittest
from unittest import mock
from unittest.mock import Mock, patch

from opentelemetry.metrics import Observation

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import HttpResponse
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._generated.exporter.models import TelemetryItem, TrackResponse
from azure.monitor.opentelemetry.exporter.export._base import BaseExporter, ExportResult
from azure.monitor.opentelemetry.exporter.statsbeat._manager import StatsbeatConfig, StatsbeatManager
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import get_statsbeat_configuration_callback
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP,
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL,
    _APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED,
    _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME,
    _DEFAULT_EU_STATS_CONNECTION_STRING,
    _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
    _REQ_SUCCESS_NAME,
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
        """A global ingestion endpoint can collect Statsbeat before a redirect."""
        exporter = mock.Mock()
        exporter._endpoint = "https://dc.services.visualstudio.com"
        exporter._region = None
        exporter._instrumentation_key = "test-key"

        config = StatsbeatConfig.from_exporter(exporter)
        self.assertIsNotNone(config)
        self.assertIsNone(config.region)
        self.assertEqual(config.connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)

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

    def test_from_config_unknown_region_uses_default_or_preserves_destination(self):
        custom = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://custom.example"
        with patch.dict(os.environ, {_APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME: ""}):
            for region in (None, ""):
                base_config = StatsbeatConfig(
                    endpoint="https://dc.services.visualstudio.com",
                    region=region,
                    instrumentation_key="test-key",
                    connection_string=_DEFAULT_EU_STATS_CONNECTION_STRING,
                )
                for settings, expected in (
                    ({"DEFAULT_STATS_CONNECTION_STRING": custom}, custom),
                    ({}, _DEFAULT_EU_STATS_CONNECTION_STRING),
                ):
                    with self.subTest(region=region, settings=settings):
                        config = StatsbeatConfig.from_config(base_config, settings)
                        self.assertIsNotNone(config)
                        self.assertEqual(config.connection_string, expected)
                        self.assertEqual(config.region, region)

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
        self.assertTrue(StatsbeatManager._validate_config(config))

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
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetricReader")
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
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetricReader")
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
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetricReader")
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
    @patch("azure.monitor.opentelemetry.exporter.statsbeat._manager._StatsbeatMetricReader")
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

    def test_get_current_config_not_initialized(self):
        """Test get_current_config when not initialized."""
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

    def _initialize_routing(self, disable_offline_storage=True):
        patches = (
            patch.dict(
                os.environ,
                {
                    _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME: "",
                    "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                },
            ),
            patch.dict(
                _STATSBEAT_STATE,
                {
                    "FEATURE_ATTRIBUTE_BITS": 0,
                    "CUSTOM_EVENTS_FEATURE_SET": False,
                    "LIVE_METRICS_FEATURE_SET": False,
                    "CUSTOMER_SDKSTATS_FEATURE_SET": False,
                    "BROWSER_SDK_LOADER_FEATURE_SET": False,
                },
            ),
            patch.dict(_REQUESTS_MAP, clear=True),
            patch("azure.monitor.opentelemetry.exporter.statsbeat._manager.threading.Timer"),
            patch(
                "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics."
                "_StatsbeatMetrics._get_azure_compute_metadata",
                return_value=False,
            ),
            patch(
                "azure.monitor.opentelemetry.exporter._generated.exporter.AzureMonitorClient.track",
                return_value=TrackResponse(items_received=1, items_accepted=1, errors=[]),
            ),
        )
        for patcher in patches:
            mocked = patcher.start()
            self.addCleanup(patcher.stop)
        config = StatsbeatConfig(
            endpoint="https://dc.services.visualstudio.com",
            region=None,
            instrumentation_key="4321abcd-5678-4efa-8abc-1234567890ab",
            disable_offline_storage=disable_offline_storage,
        )
        self.assertTrue(self.manager.initialize(config))
        return mocked

    def test_redirect_keeps_statsbeat_storage_disabled(self):
        self._initialize_routing(disable_offline_storage=False)
        self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
        self.assertFalse(self.manager.get_current_config().disable_offline_storage)
        self.assertTrue(self.manager._exporter._exporter._disable_offline_storage)
        self.assertIsNone(self.manager._exporter._exporter.storage)

    def test_unknown_region_accepts_settings_and_restarts_after_disable(self):
        track = self._initialize_routing()
        custom = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://custom.example"
        enabled = {
            "FEATURE_SDK_STATS": '{"default": "enabled"}',
            "DEFAULT_STATS_CONNECTION_STRING": custom,
        }
        with patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager",
            return_value=self.manager,
        ):
            get_statsbeat_configuration_callback(enabled)
            self.assertEqual(self.manager.get_current_config().connection_string, custom)
            get_statsbeat_configuration_callback({"FEATURE_SDK_STATS": '{"default": "disabled"}'})
            self.assertFalse(self.manager.is_initialized())
            get_statsbeat_configuration_callback(enabled)
        self.assertTrue(self.manager.is_initialized())
        self.assertIsNone(self.manager.get_current_config().region)
        self.assertEqual(self.manager.get_current_config().connection_string, custom)
        track.reset_mock()
        self.manager._meter_provider.force_flush()
        track.assert_called_once()

    def test_redirect_preserves_collection_and_routes_all_metrics_to_eu(self):
        track = self._initialize_routing()
        metrics = self.manager._metrics
        provider = self.manager._meter_provider
        reader = provider._metric_readers[0]
        exporter = self.manager._exporter
        timer = self.manager._warmup_timer
        interval_counts = dict(metrics._long_interval_count_map)
        _REQUESTS_MAP[_REQ_SUCCESS_NAME[1]] = 5
        original_config = self.manager.get_current_config()
        old_sender = exporter._exporter
        target = "https://germanynorth-1.in.applicationinsights.azure.com"

        with patch.object(old_sender, "shutdown", wraps=old_sender.shutdown) as shutdown, patch.object(
            old_sender.client, "close", wraps=old_sender.client.close
        ) as close:
            self.manager._update_endpoint(target)
            shutdown.assert_called_once()
            close.assert_called_once()
        self.assertIs(self.manager._metrics, metrics)
        self.assertIs(self.manager._meter_provider, provider)
        self.assertIs(provider._metric_readers[0], reader)
        self.assertIs(self.manager._warmup_timer, timer)
        self.assertIs(self.manager._exporter, exporter)
        self.assertEqual(metrics._long_interval_count_map, interval_counts)
        self.assertEqual(_REQUESTS_MAP[_REQ_SUCCESS_NAME[1]], 5)
        self.assertEqual(metrics._NETWORK_ATTRIBUTES, {"endpoint": "breeze", "host": "germanynorth-1"})
        config = self.manager.get_current_config()
        self.assertEqual(config.connection_string, _DEFAULT_EU_STATS_CONNECTION_STRING)
        self.assertEqual(config.endpoint, target)
        self.assertEqual(config.region, "germanynorth")

        # A subsequently constructed logs/traces exporter must not restore the global route.
        self.assertTrue(self.manager.initialize(original_config))
        self.assertEqual(self.manager.get_current_config().endpoint, target)
        provider.force_flush()
        envelopes = track.call_args.args[0]
        names = {envelope.data.base_data.metrics[0].name for envelope in envelopes}
        self.assertTrue({"Attach", "Feature", "Request_Success_Count"}.issubset(names))
        eu = ConnectionStringParser(_DEFAULT_EU_STATS_CONNECTION_STRING)
        self.assertTrue(all(envelope.instrumentation_key == eu.instrumentation_key for envelope in envelopes))
        self.assertEqual(exporter._exporter.client._config.host, eu.endpoint)

    def test_redirect_within_boundary_reuses_sender_and_cross_boundary_replaces_it(self):
        self._initialize_routing()
        self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
        eu_sender = self.manager._exporter._exporter
        self.manager._update_endpoint("https://northeurope-2.in.applicationinsights.azure.com")
        self.assertIs(self.manager._exporter._exporter, eu_sender)
        self.assertEqual(self.manager._metrics._NETWORK_ATTRIBUTES["host"], "northeurope-2")
        self.manager._update_endpoint("https://eastus-1.in.applicationinsights.azure.com")
        self.assertIsNot(self.manager._exporter._exporter, eu_sender)
        self.assertEqual(self.manager.get_current_config().connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)

    def test_redirect_respects_stats_connection_string_override(self):
        self._initialize_routing()
        custom = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://custom.example"
        config_manager = Mock()
        config_manager.get_settings.return_value = {
            "DEFAULT_STATS_CONNECTION_STRING": _DEFAULT_EU_STATS_CONNECTION_STRING
        }
        with patch.dict(
            os.environ,
            {
                _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME: custom,
                _APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED: "false",
            },
        ), patch(
            "azure.monitor.opentelemetry.exporter._configuration._state._configuration_manager",
            config_manager,
        ):
            self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
            sender = self.manager._exporter._exporter
            self.manager._update_endpoint("https://eastus-1.in.applicationinsights.azure.com")
        self.assertIs(self.manager._exporter._exporter, sender)
        self.assertEqual(self.manager.get_current_config().connection_string, custom)
        self.assertEqual(sender.client._config.host, "https://custom.example")
        self.assertEqual(self.manager._metrics._NETWORK_ATTRIBUTES["host"], "eastus-1")

    def test_redirect_uses_cached_settings_for_same_region_and_boundary_changes(self):
        self._initialize_routing()
        self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
        eu = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://eu.example"
        row = "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://row.example"
        settings = {
            "FEATURE_SDK_STATS": '{"default": "enabled"}',
            "SUPPORTED_DATA_BOUNDARIES": '["EU"]',
            "EU_REGIONS": '["westeurope", "northeurope"]',
            "EU_STATS_CONNECTION_STRING": eu,
            "DEFAULT_STATS_CONNECTION_STRING": row,
        }
        config_manager = Mock()
        config_manager.get_settings.return_value = settings
        with patch.dict(os.environ, {_APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED: "false"}), patch(
            "azure.monitor.opentelemetry.exporter._configuration._state._configuration_manager",
            config_manager,
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.get_statsbeat_manager",
            return_value=self.manager,
        ):
            get_statsbeat_configuration_callback(settings)
            sender = self.manager._exporter._exporter
            for target in ("westeurope-6", "northeurope-2"):
                with self.subTest(target=target):
                    self.manager._update_endpoint(f"https://{target}.in.applicationinsights.azure.com")
                    self.assertIs(self.manager._exporter._exporter, sender)
                    self.assertEqual(self.manager.get_current_config().connection_string, eu)
                    self.assertEqual(self.manager._metrics._NETWORK_ATTRIBUTES["host"], target)
            self.manager._update_endpoint("https://eastus-1.in.applicationinsights.azure.com")
            self.assertIsNot(self.manager._exporter._exporter, sender)
            self.assertEqual(self.manager.get_current_config().connection_string, row)
            config_manager.get_settings.return_value = {}
            self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
        self.assertEqual(self.manager.get_current_config().connection_string, _DEFAULT_EU_STATS_CONNECTION_STRING)

    def test_redirect_waits_for_observable_collection_during_flush(self):
        self._assert_redirect_waits_for_observable_collection(periodic=False)

    def test_redirect_waits_for_observable_collection_during_periodic_export(self):
        self._assert_redirect_waits_for_observable_collection(periodic=True)

    def _assert_redirect_waits_for_observable_collection(self, periodic):
        track = self._initialize_routing()
        self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
        provider = self.manager._meter_provider
        metrics = self.manager._metrics
        reader = provider._metric_readers[0]
        collecting = threading.Event()
        finish_collection = threading.Event()
        update_started = threading.Event()
        updated = threading.Event()
        errors = []

        def observe(options):
            attributes = dict(metrics._NETWORK_ATTRIBUTES)
            if not collecting.is_set():
                collecting.set()
                if not finish_collection.wait(5):
                    errors.append("Collection was not released")
            return [Observation(1, attributes)]

        meter = provider.get_meter("routing-test")
        meter.create_observable_gauge("route_before", callbacks=[observe])
        meter.create_observable_gauge(
            "route_after", callbacks=[lambda options: [Observation(1, dict(metrics._NETWORK_ATTRIBUTES))]]
        )

        def update():
            update_started.set()
            try:
                self.manager._update_endpoint("https://eastus-1.in.applicationinsights.azure.com")
            except Exception as exc:
                errors.append(exc)
            finally:
                updated.set()

        def collect():
            try:
                if periodic:
                    reader._ticker()
                else:
                    provider.force_flush()
            except Exception as exc:
                errors.append(exc)

        # Exercise the periodic path without waiting for the real 15-minute interval.
        with patch.object(reader, "_shutdown_event") as shutdown_event:
            shutdown_event.wait.side_effect = [False, True]
            collection_thread = threading.Thread(target=collect, daemon=True)
            update_thread = threading.Thread(target=update, daemon=True)
            collection_thread.start()
            try:
                self.assertTrue(collecting.wait(5))
                update_thread.start()
                self.assertTrue(update_started.wait(5))
                self.assertFalse(updated.wait(0.1))
            finally:
                finish_collection.set()
                collection_thread.join(10)
                if update_thread.ident:
                    update_thread.join(10)
        self.assertFalse(collection_thread.is_alive())
        self.assertFalse(update_thread.is_alive())
        self.assertEqual(errors, [])
        eu_key = ConnectionStringParser(_DEFAULT_EU_STATS_CONNECTION_STRING).instrumentation_key
        first_batch = track.call_args_list[0].args[0]
        self.assertTrue(all(envelope.instrumentation_key == eu_key for envelope in first_batch))
        self.assertEqual(
            {
                envelope.data.base_data.properties["host"]
                for envelope in first_batch
                if "host" in envelope.data.base_data.properties
            },
            {"westeurope-5"},
        )
        track.reset_mock()
        provider.force_flush()
        row_key = ConnectionStringParser(_DEFAULT_NON_EU_STATS_CONNECTION_STRING).instrumentation_key
        next_batch = track.call_args.args[0]
        self.assertTrue(all(envelope.instrumentation_key == row_key for envelope in next_batch))
        self.assertEqual(
            {
                envelope.data.base_data.properties["host"]
                for envelope in next_batch
                if "host" in envelope.data.base_data.properties
            },
            {"eastus-1"},
        )

    def test_redirect_does_not_initialize_or_revive_statsbeat(self):
        target = "https://westeurope-5.in.applicationinsights.azure.com"
        self.manager._update_endpoint(target)
        self.assertFalse(self.manager.is_initialized())
        self._initialize_routing()
        self.manager.shutdown()
        self.manager._update_endpoint(target)
        self.assertFalse(self.manager.is_initialized())
        self.assertIsNone(self.manager._exporter)

    def test_redirect_waits_for_inflight_export_and_storage_replay(self):
        self._initialize_routing()
        exporter = self.manager._exporter
        sender = exporter._exporter
        sender.storage = Mock()
        replay_started = threading.Event()
        finish_replay = threading.Event()
        update_started = threading.Event()
        updated = threading.Event()
        errors = []

        def replay(*args):
            replay_started.set()
            if not finish_replay.wait(5):
                raise AssertionError("Replay was not released")

        def update():
            update_started.set()
            try:
                self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
            except Exception as exc:
                errors.append(exc)
            finally:
                updated.set()

        with patch.object(sender, "_handle_transmit_from_storage", side_effect=replay), patch.object(
            sender, "shutdown", wraps=sender.shutdown
        ) as shutdown:
            export_thread = threading.Thread(target=self.manager._meter_provider.force_flush, daemon=True)
            update_thread = threading.Thread(target=update, daemon=True)
            export_thread.start()
            try:
                self.assertTrue(replay_started.wait(5))
                update_thread.start()
                self.assertTrue(update_started.wait(5))
                self.assertFalse(updated.wait(0.1))
                shutdown.assert_not_called()
            finally:
                finish_replay.set()
                export_thread.join(10)
                if update_thread.ident:
                    update_thread.join(10)
            self.assertFalse(export_thread.is_alive())
            self.assertFalse(update_thread.is_alive())
            self.assertEqual(errors, [])
            shutdown.assert_called_once()
            sender.storage.close.assert_called_once()
            self.assertIsNot(exporter._exporter, sender)

    def test_statsbeat_redirect_during_customer_route_update_does_not_deadlock(self):
        self._initialize_routing()
        sender = self.manager._exporter._exporter
        stats_started = threading.Event()
        update_started = threading.Event()
        results = []
        success = TrackResponse(items_received=1, items_accepted=1, errors=[])

        def redirect(endpoint):
            response = HttpResponse(None, None)
            response.status_code = 307
            response.headers = {"location": endpoint}
            return HttpResponseError(response=response)

        def stats_track(*args, **kwargs):
            if not stats_started.is_set():
                stats_started.set()
                self.assertTrue(update_started.wait(5))
                raise redirect("https://westus-2.in.applicationinsights.azure.com")
            return success

        update_endpoint = self.manager._update_endpoint

        def update(endpoint):
            update_started.set()
            update_endpoint(endpoint)

        with patch.object(BaseExporter, "_should_collect_stats", return_value=False), patch.object(
            BaseExporter, "_should_collect_customer_sdkstats", return_value=False
        ):
            customer = BaseExporter(
                connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
                disable_offline_storage=True,
            )
        with patch.object(sender.client, "track", side_effect=stats_track), patch.object(
            customer.client,
            "track",
            side_effect=[redirect("https://westeurope-5.in.applicationinsights.azure.com"), success],
        ), patch.object(customer, "_should_collect_stats", return_value=True), patch.object(
            customer, "_should_collect_customer_sdkstats", return_value=False
        ), patch.object(
            self.manager, "_update_endpoint", side_effect=update
        ), patch(
            "azure.monitor.opentelemetry.exporter.export._base.get_statsbeat_manager", return_value=self.manager
        ):
            stats_thread = threading.Thread(target=self.manager._meter_provider.force_flush, daemon=True)
            customer_thread = threading.Thread(
                target=lambda: results.append(customer._transmit([TelemetryItem(name="test")])), daemon=True
            )
            stats_thread.start()
            self.assertTrue(stats_started.wait(5))
            customer_thread.start()
            stats_thread.join(10)
            customer_thread.join(10)
            self.assertFalse(stats_thread.is_alive())
            self.assertFalse(customer_thread.is_alive())
        self.assertEqual(results, [ExportResult.SUCCESS])
        self.assertEqual(self.manager.get_current_config().connection_string, _DEFAULT_EU_STATS_CONNECTION_STRING)

    def test_redirect_replacement_failure_preserves_route(self):
        self._initialize_routing()
        config = self.manager.get_current_config()
        sender = self.manager._exporter._exporter
        host = self.manager._metrics._NETWORK_ATTRIBUTES["host"]
        with patch(
            "azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter",
            side_effect=ValueError("Invalid replacement"),
        ):
            with self.assertRaisesRegex(ValueError, "Invalid replacement"):
                self.manager._update_endpoint("https://westeurope-5.in.applicationinsights.azure.com")
        self.assertIs(self.manager._exporter._exporter, sender)
        self.assertEqual(self.manager.get_current_config(), config)
        self.assertEqual(self.manager._metrics._NETWORK_ATTRIBUTES["host"], host)

    def test_shutdown_during_reconfiguration_does_not_revive_collection(self):
        self._initialize_routing()
        config = self.manager.get_current_config()
        config.connection_string = _DEFAULT_EU_STATS_CONNECTION_STRING
        with patch.object(
            self.manager._meter_provider, "force_flush", side_effect=lambda **kwargs: self.manager.shutdown()
        ), patch.object(self.manager, "_do_initialize") as initialize:
            self.assertFalse(self.manager.initialize(config))
        initialize.assert_not_called()
        self.assertFalse(self.manager.is_initialized())

    def test_redirect_waits_for_configuration_update(self):
        self._initialize_routing()
        config = self.manager.get_current_config()
        config.connection_string = _DEFAULT_EU_STATS_CONNECTION_STRING
        flush_started = threading.Event()
        finish_flush = threading.Event()
        update_started = threading.Event()
        updated = threading.Event()
        results = []

        def flush(**kwargs):
            flush_started.set()
            self.assertTrue(finish_flush.wait(5))

        def update():
            update_started.set()
            self.manager._update_endpoint("https://eastus-1.in.applicationinsights.azure.com")
            updated.set()

        with patch.object(self.manager._meter_provider, "force_flush", side_effect=flush):
            configure_thread = threading.Thread(
                target=lambda: results.append(self.manager.initialize(config)), daemon=True
            )
            update_thread = threading.Thread(target=update, daemon=True)
            configure_thread.start()
            try:
                self.assertTrue(flush_started.wait(5))
                update_thread.start()
                self.assertTrue(update_started.wait(5))
                self.assertFalse(updated.wait(0.1))
            finally:
                finish_flush.set()
                configure_thread.join(10)
                if update_thread.ident:
                    update_thread.join(10)
            self.assertFalse(configure_thread.is_alive())
            self.assertFalse(update_thread.is_alive())
        self.assertEqual(results, [True])
        self.assertTrue(updated.is_set())
        current = self.manager.get_current_config()
        self.assertEqual(current.endpoint, "https://eastus-1.in.applicationinsights.azure.com")
        self.assertEqual(current.connection_string, _DEFAULT_NON_EU_STATS_CONNECTION_STRING)
