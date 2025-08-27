# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
import threading
from typing import Optional, Any

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
    is_statsbeat_enabled,
    set_statsbeat_shutdown,  # Add this import
)
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _get_stats_connection_string,
    _get_stats_long_export_interval,
    _get_stats_short_export_interval,
)
from azure.monitor.opentelemetry.exporter._utils import Singleton

logger = logging.getLogger(__name__)


class StatsbeatConfig:
    """Configuration class for Statsbeat metrics collection."""
    
    def __init__(self, 
                 endpoint: str,
                 instrumentation_key: str,
                 disable_offline_storage: bool = False,
                 credential: Optional[Any] = None,
                 distro_version: Optional[str] = None):
        self.endpoint = endpoint
        self.instrumentation_key = instrumentation_key
        self.connection_string = _get_stats_connection_string(endpoint)
        self.distro_version = distro_version
        # features
        self.disable_offline_storage = disable_offline_storage
        self.credential = credential

    @classmethod
    def from_exporter(cls, exporter) -> 'StatsbeatConfig':
        """Create configuration from an exporter instance."""
        return cls(
            endpoint=exporter._endpoint,
            instrumentation_key=exporter._instrumentation_key,
            disable_offline_storage=exporter._disable_offline_storage,
            credential=exporter._credential,
            distro_version=exporter._distro_version,
        )
    
    def __eq__(self, other) -> bool:
        """Compare two configurations for equality based on what can be changed via control plane."""
        if not isinstance(other, StatsbeatConfig):
            return False
        return (
            self.connection_string == other.connection_string and
            self.disable_offline_storage == other.disable_offline_storage
        )
    
    def __hash__(self) -> int:
        """Hash based on connection string and offline storage setting."""
        return hash((self.connection_string, self.disable_offline_storage))


class StatsbeatManager(metaclass=Singleton):
    """Thread-safe singleton manager for Statsbeat metrics collection with dynamic reconfiguration support."""

    def __init__(self):
        """Initialize instance attributes. Called only once due to Singleton metaclass."""
        # Instance-level attributes
        self._lock = threading.Lock()
        self._initialized: bool = False  # type: ignore
        self._metrics: Optional[_StatsbeatMetrics] = None  # type: ignore
        self._meter_provider: Optional[MeterProvider] = None  # type: ignore
        self._config: Optional[StatsbeatConfig] = None  # type: ignore
    
    def initialize(self, config: StatsbeatConfig) -> bool:
        """Initialize statsbeat collection with thread safety."""
        if not is_statsbeat_enabled():
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
        """Internal initialization method."""
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
            long_interval_threshold = (
                _get_stats_long_export_interval() // _get_stats_short_export_interval()
            )
            
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
    
    def _cleanup(self):
        """Clean up resources."""
        if self._meter_provider:
            try:
                self._meter_provider.shutdown()
            except Exception:  # pylint: disable=broad-except
                pass
        self._meter_provider = None
        self._metrics = None
        self._config = None
        self._initialized = False
    
    def shutdown(self) -> bool:
        """Shutdown statsbeat collection with thread safety."""
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
                self._cleanup()
            
            if shutdown_success:
                set_statsbeat_shutdown(True)  # Use the proper setter function
            
            return shutdown_success
    
    def reconfigure(self, new_config: StatsbeatConfig) -> bool:
        """Reconfigure statsbeat with new configuration."""
        if not is_statsbeat_enabled():
            return False
            
        with self._lock:
            if not self._initialized:
                # If not initialized, just initialize with new config
                return self._do_initialize(new_config)
            
            # If same config, no need to reconfigure
            if self._config and self._config == new_config:
                return True
                
            return self._reconfigure(new_config)
    
    def _reconfigure(self, new_config: StatsbeatConfig) -> bool:
        """Internal reconfiguration method."""
        # Shutdown current instance with timeout
        if self._meter_provider:
            try:
                # Force flush before shutdown to ensure data is sent
                self._meter_provider.force_flush(timeout_millis=5000)
                self._meter_provider.shutdown(timeout_millis=5000)
            except Exception:  # pylint: disable=broad-except
                pass
        
        # Reset state but keep initialized=True
        self._meter_provider = None
        self._metrics = None
        self._config = None
        
        # Initialize with new config
        success = self._do_initialize(new_config)
        
        if not success:
            # If reinitialization failed, mark as not initialized
            self._initialized = False
        
        return success


# Global convenience functions
def collect_statsbeat_metrics(exporter) -> None:
    """Collect statsbeat metrics from an exporter."""
    config = StatsbeatConfig.from_exporter(exporter)
    StatsbeatManager().initialize(config)


def shutdown_statsbeat_metrics() -> bool:
    """Shutdown statsbeat collection globally."""
    return StatsbeatManager().shutdown()
