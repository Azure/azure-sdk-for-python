# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
import threading
from typing import Optional, Any, Dict

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    is_statsbeat_enabled,
    set_statsbeat_shutdown,  # Add this import
)
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _get_stats_connection_string,
    _get_stats_long_export_interval,
    _get_stats_short_export_interval,
    _get_connection_string_for_region_from_config,
)
from azure.monitor.opentelemetry.exporter._utils import Singleton

logger = logging.getLogger(__name__)


class StatsbeatConfig:
    """Configuration class for Statsbeat metrics collection."""

    def __init__(self,
                 endpoint: str,
                 region: str,
                 instrumentation_key: str,
                 disable_offline_storage: bool = False,
                 credential: Optional[Any] = None,
                 distro_version: Optional[str] = None,
                 connection_string: Optional[str] = None) -> None:
        # Customer specific information
        self.endpoint = endpoint
        self.region = region
        self.instrumentation_key = instrumentation_key

        # features
        self.disable_offline_storage = disable_offline_storage
        self.credential = credential
        self.distro_version = distro_version
        self.connection_string: str = ""

        # Use provided connection_string or generate from endpoint
        if connection_string:
            try:
                # Validate connection string
                ConnectionStringParser(connection_string)
                self.connection_string = connection_string
            except Exception:  # pylint: disable=broad-except
                logger.error("Invalid connection string obtained from config. Reverting to default.")
                self.connection_string = _get_stats_connection_string(endpoint)
        else:
            self.connection_string = _get_stats_connection_string(endpoint)

    @classmethod
    def from_exporter(cls, exporter: Any) -> Optional['StatsbeatConfig']:
        # Create configuration from an exporter instance
        # Validate required fields from exporter
        if not hasattr(exporter, '_instrumentation_key') or not exporter._instrumentation_key:  # pylint: disable=protected-access
            logger.warning("Exporter is missing a valid instrumentation key.")
            return None
        if not hasattr(exporter, '_endpoint') or not exporter._endpoint:  # pylint: disable=protected-access
            logger.warning("Exporter is missing a valid endpoint.")
            return None
        if not hasattr(exporter, '_region') or not exporter._region:  # pylint: disable=protected-access
            logger.warning("Exporter is missing a valid region.")
            return None

        return cls(
            endpoint=exporter._endpoint,  # pylint: disable=protected-access
            region=exporter._region,  # pylint: disable=protected-access
            instrumentation_key=exporter._instrumentation_key,  # pylint: disable=protected-access
            disable_offline_storage=exporter._disable_offline_storage,  # pylint: disable=protected-access
            credential=exporter._credential,  # pylint: disable=protected-access
            distro_version=exporter._distro_version,  # pylint: disable=protected-access
        )

    @classmethod
    def from_config(cls, base_config: 'StatsbeatConfig', config_dict: Dict[str, str]) -> Optional['StatsbeatConfig']:
        """Update configuration from a dictionary. Used in conjunction with OneSettings control plane.

        Creates a new StatsbeatConfig instance with the same base configuration but updated
        `connection_string` and `disable_offline_storage` from the provided dictionary.

        :param base_config: Base configuration to update
        :type base_config: StatsbeatConfig
        :param config_dict: Dictionary containing configuration values
        :type config_dict: Dict[str, str]
        :return: Updated StatsbeatConfig instance
        :rtype: StatsbeatConfig
        """
        # Validate required fields
        if not base_config.instrumentation_key:
            logger.warning("Base configuration is missing a valid instrumentation key.")
            return None
        if not base_config.region:
            logger.warning("Base configuration is missing a valid region.")
            return None
        if not base_config.endpoint:
            logger.warning("Base configuration is missing a valid endpoint.")
            return None

        connection_string = _get_connection_string_for_region_from_config(base_config.region, config_dict)
        if connection_string is None:
            # If something went wrong in fetching connection string, fall back to the original
            connection_string = base_config.connection_string

        # TODO: Add support for disable_offline_storage from config_dict once supported in control plane
        disable_offline_storage = config_dict.get("disable_offline_storage")
        disable_offline_storage_config = isinstance(disable_offline_storage, str) \
            and disable_offline_storage.lower() == "true"

        return cls(
            endpoint=base_config.endpoint,
            region=base_config.region,
            instrumentation_key=base_config.instrumentation_key,
            disable_offline_storage=disable_offline_storage_config, # TODO: Use config value once supported
            credential=base_config.credential,
            distro_version=base_config.distro_version,
            connection_string=connection_string
        )

    def __eq__(self, other: object) -> bool:
        # Compare two configurations for equality based on what can be changed via control plane.
        if not isinstance(other, StatsbeatConfig):
            return False
        return (
            str(self.connection_string) == str(other.connection_string) and
            self.disable_offline_storage == other.disable_offline_storage
        )

    def __hash__(self) -> int:
        # Hash based on connection string and offline storage setting.
        return hash((str(self.connection_string), self.disable_offline_storage))


class StatsbeatManager(metaclass=Singleton):
    """Thread-safe singleton manager for Statsbeat metrics collection with dynamic reconfiguration support."""

    def __init__(self) -> None:
        # Initialize instance attributes. Called only once due to Singleton metaclass.
        self._lock = threading.Lock()
        self._initialized: bool = False  # type: ignore
        self._metrics: Optional[_StatsbeatMetrics] = None  # type: ignore
        self._meter_provider: Optional[MeterProvider] = None  # type: ignore

        # Set during first initialization, preserved in shutdown for potential re-initialization
        self._config: Optional[StatsbeatConfig] = None  # type: ignore

    @staticmethod
    def _validate_config(config: Optional[StatsbeatConfig]) -> bool:
        """Validate that a configuration has all required fields.

        :param config: Configuration to validate
        :type config: StatsbeatConfig
        :return: True if config is valid, False otherwise
        :rtype: bool
        """
        if config is None:
            return False
        if not config.instrumentation_key:
            return False
        if not config.endpoint:
            return False
        if not config.region:
            return False
        if not config.connection_string:
            return False
        return True

    def initialize(self, config: StatsbeatConfig) -> bool:  # pyright: ignore
        # Initialize statsbeat collection with thread safety.
        if not is_statsbeat_enabled():
            return False

        # Validate config before proceeding
        if not self._validate_config(config):
            return False

        with self._lock:
            if self._initialized:
                # If already initialized with the same config, return True
                if self._config and self._config == config:
                    return True
                # If config is different, reconfigure
                return self._reconfigure(config)

            return self._do_initialize(config)

    def _do_initialize(self, config: StatsbeatConfig) -> bool:
        # Internal initialization method.
        try:
            # Create statsbeat exporter
            # Use delayed import to avoid circular import
            from azure.monitor.opentelemetry.exporter.export.metrics._exporter import AzureMonitorMetricExporter

            statsbeat_exporter = AzureMonitorMetricExporter(
                connection_string=config.connection_string,
                disable_offline_storage=config.disable_offline_storage,
                is_sdkstats=True,
            )

            # Create metric reader
            reader = PeriodicExportingMetricReader(
                statsbeat_exporter,
                export_interval_millis=_get_stats_short_export_interval() * 1000, # 15m by default
            )

            # Create meter provider
            self._meter_provider = MeterProvider(
                metric_readers=[reader],
                resource=Resource.get_empty(),
            )

            # long_interval_threshold represents how many collects for short interval
            # should have passed before a long interval collect
            short_interval = _get_stats_short_export_interval()
            long_interval = _get_stats_long_export_interval()

            long_interval_threshold = long_interval // short_interval

            # Create statsbeat metrics
            self._metrics = _StatsbeatMetrics(
                self._meter_provider,
                config.instrumentation_key,
                config.endpoint,
                config.disable_offline_storage,
                long_interval_threshold,
                config.credential is not None,
                config.distro_version,
            )

            # Force initial flush and initialize non-initial metrics
            self._meter_provider.force_flush()
            self._metrics.init_non_initial_metrics()

            self._config = config
            self._initialized = True
            return True

        except Exception as e:  # pylint: disable=broad-except
            # Log the error for debugging
            logger.warning("Failed to initialize statsbeat: %s", e)
            # Clean up on failure
            self._cleanup()
            return False

    def _cleanup(self, shutdown_meter_provider: bool = True) -> None:
        # Clean up resources with optional meter provider shutdown
        if shutdown_meter_provider and self._meter_provider:
            try:
                self._meter_provider.shutdown()
            except Exception:  # pylint: disable=broad-except
                pass
        # We leave config intact for potential re-initialization
        self._meter_provider = None
        self._metrics = None
        self._initialized = False

    def shutdown(self) -> bool:
        # Shutdown statsbeat collection with thread safety.
        with self._lock:
            if not self._initialized:
                return False

            shutdown_success = False
            try:
                if self._meter_provider is not None:
                    self._meter_provider.shutdown()
                    shutdown_success = True
            except Exception:  # pylint: disable=broad-except
                pass
            finally:
                self._cleanup(shutdown_meter_provider=False)

            if shutdown_success:
                set_statsbeat_shutdown(True)  # Use the proper setter function

            return shutdown_success

    def _reconfigure(self, new_config: StatsbeatConfig) -> bool:
        # Internal reconfiguration method.
        # Shutdown current instance with timeout
        if self._meter_provider:
            try:
                # Force flush before shutdown to ensure data is sent
                self._meter_provider.force_flush(timeout_millis=5000)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to flush meter provider during reconfiguration: %s", e)

            try:
                self._meter_provider.shutdown(timeout_millis=5000)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to shutdown meter provider during reconfiguration: %s", e)

        # Reset state but keep initialized=True
        self._meter_provider = None
        self._metrics = None

        # Initialize with new config
        success: bool = self._do_initialize(new_config)

        if not success:
            # If reinitialization failed, mark as not initialized
            logger.error("Failed to reinitialize statsbeat with new configuration.")
            self._initialized = False
        else:
            logger.info("Statsbeat successfully reconfigured with new settings.")

        return success

    def get_current_config(self) -> Optional[StatsbeatConfig]:
        """Get a copy of the current statsbeat configuration.

        :return: Copy of current StatsbeatConfig instance if initialized, None otherwise
        :rtype: Optional[StatsbeatConfig]
        """
        with self._lock:
            if self._config is None:
                return None
            # Return a copy to prevent external modification
            return StatsbeatConfig(
                endpoint=self._config.endpoint,
                region=self._config.region,
                instrumentation_key=self._config.instrumentation_key,
                disable_offline_storage=self._config.disable_offline_storage,
                credential=self._config.credential,
                distro_version=self._config.distro_version,
                connection_string=self._config.connection_string
            )

    def is_initialized(self) -> bool:
        """Check if the StatsbeatManager is currently initialized.

        :return: True if initialized, False otherwise
        :rtype: bool
        """
        with self._lock:
            return self._initialized
