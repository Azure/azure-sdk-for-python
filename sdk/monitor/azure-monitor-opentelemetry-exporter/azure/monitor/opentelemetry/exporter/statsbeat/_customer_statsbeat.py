# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Customer Statsbeat implementation for Azure Monitor OpenTelemetry Exporter.

This module provides the implementation for collecting and reporting customer statsbeat
metrics that track the usage and performance of the Azure Monitor OpenTelemetry Exporter.
"""

from typing import List, Optional, Union
import logging
import os

from azure.monitor.opentelemetry.exporter._constants import _APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import AzureMonitorMetricExporter as AzureMonitorStatsbeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat_types import (
    CustomerStatsbeat,
    CustomerStatsbeatProperties,
    DropCode, 
    RetryCode,
    TelemetryType,
    CustomStatsbeatCounter,
    STATSBEAT_LANGUAGE
)

# Import VERSION from top-level package
try:
    from azure.monitor.opentelemetry.exporter import VERSION
except ImportError:
    # Fallback if import fails
    VERSION = "unknown"

# Import get_attach_type from _utils if available
try:
    from azure.monitor.opentelemetry.exporter._utils.metric_utils import get_attach_type
except ImportError:
    # Define locally if import fails
    def get_attach_type() -> str:
        """Return the attach type for use in statsbeat metrics.
        
        Determines the environment the SDK is attached to for reporting context.
        
        Returns:
            A string representing the attach type (e.g., "direct", "container", etc.)
        """
        return "direct"

logger = logging.getLogger(__name__)

class CustomerStatsbeatMetrics(_StatsbeatMetrics):
    """Customer-facing statsbeat metrics implementation.
    
    This class collects and reports metrics related to the SDK's interaction with the 
    Azure Monitor service. The metrics are sent to the customer's Breeze endpoint and
    can be used by the customer for monitoring their application performance.
    
    Three types of metrics are collected:
    - Successful telemetry items
    - Dropped telemetry items (with reasons)
    - Retried telemetry items (with reasons)
    """

    def _is_customer_statsbeat_enabled(self) -> bool:
        """Checks if customer statsbeat should be enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        env_var = os.environ.get(_APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW, "").lower()
        return env_var in ("true", "1", "yes")
    
    def __init__(self, options):
        """Initialize the customer statsbeat metrics.
        
        Args:
            options: Configuration options including instrumentation key and endpoint URL
        """
        # Initialize counter even when disabled to avoid AttributeError
        self._customer_statsbeat_counter = CustomerStatsbeat()
        
        # Store basic properties that will be used in all scenarios
        self._language = STATSBEAT_LANGUAGE
        self._version = VERSION
        self._attach = get_attach_type()
        
        # Check if customer statsbeat is enabled via environment variable
        # Default is disabled (opt-in feature)
        self._is_enabled = self._is_customer_statsbeat_enabled()
        if not self._is_enabled:
            logger.debug(
                "Customer statsbeat is disabled. "
                f"Enable it by setting {_APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW}=true"
            )
            return

        # Configure metric reader and meter provider
        self._stats_collection_interval = 900000  # 15 minutes
        
        exporter_config = {
            "connection_string": f"InstrumentationKey={options.instrumentation_key};"
                                 f"IngestionEndpoint={options.endpoint_url}"
        }
        self._customer_statsbeat_exporter = AzureMonitorStatsbeatExporter(**exporter_config)
        
        # Configure metric reader
        metric_reader_options = {
            "exporter": self._customer_statsbeat_exporter,
            "export_interval_millis": options.network_collection_interval or self._stats_collection_interval
        }
        self._customer_statsbeat_metric_reader = PeriodicExportingMetricReader(**metric_reader_options)
        
        self._customer_statsbeat_meter_provider = MeterProvider(
            metric_readers=[self._customer_statsbeat_metric_reader]
        )
        
        # Initialize base class with required parameters
        super().__init__(
            meter_provider=self._customer_statsbeat_meter_provider,
            instrumentation_key=options.instrumentation_key,
            endpoint=options.endpoint_url,
            disable_offline_storage=False,
            long_interval_threshold=15,  # Default to 15 minutes
            has_credential=False,
            distro_version=""
        )
        
        self._customer_statsbeat_meter = self._customer_statsbeat_meter_provider.get_meter(
            "Azure Monitor Customer Statsbeat"
        )
        
        # Create customer statsbeat properties for later use
        self._customer_properties = CustomerStatsbeatProperties(
            language=self._language,
            version=self._version,
            compute_type=self._attach
        )
        
        # Create observables for each type of metric using the enum values from CustomStatsbeatCounter
        self._success_gauge = self._customer_statsbeat_meter.create_observable_gauge(
            name=CustomStatsbeatCounter.ITEM_SUCCESS_COUNT.value,
            description="Tracks successful telemetry items sent to Azure Monitor",
            callbacks=[self._item_success_callback]
        )
        
        self._drop_gauge = self._customer_statsbeat_meter.create_observable_gauge(
            name=CustomStatsbeatCounter.ITEM_DROP_COUNT.value,
            description="Tracks telemetry items dropped by the SDK",
            callbacks=[self._item_drop_callback]
        )
        
        self._retry_gauge = self._customer_statsbeat_meter.create_observable_gauge(
            name=CustomStatsbeatCounter.ITEM_RETRY_COUNT.value,
            description="Tracks telemetry items that were retried",
            callbacks=[self._item_retry_callback]
        )
    
    def count_successful_items(self, count: int, telemetry_type: TelemetryType) -> None:
        """Count successful telemetry items.
        
        Args:
            count: Number of successful items
            telemetry_type: The type of telemetry (e.g., REQUEST, DEPENDENCY)
        """
        if not self._is_enabled or count <= 0:
            return
        
        try:
            counter = getattr(self, "_customer_statsbeat_counter", None)
            
            # Check if counter exists and has the required attribute
            if counter is None or not hasattr(counter, "total_item_success_count"):
                return
                
            # Check if there's an existing entry for this telemetry type
            existing_entry = None
            for entry in counter.total_item_success_count:
                if entry["telemetry_type"] == telemetry_type:
                    existing_entry = entry
                    break
            
            if existing_entry:
                existing_entry["count"] += count
            else:
                counter.total_item_success_count.append(
                    {"telemetry_type": telemetry_type, "count": count}
                )
        except (TypeError, KeyError) as exc:
            # Log specific exceptions that might occur during dictionary operations
            logger.warning("Failed to count successful items due to a type error: %s", str(exc))
        except Exception as exc:  # pylint: disable=broad-except
            # Still catch all other exceptions to prevent affecting the application            
            # This is acceptable in statsbeat since it should never crash the host app
            logger.warning("Failed to count successful items: %s", str(exc))
    
    def count_dropped_items(
        self, 
        count: int, 
        drop_code: Union[DropCode, str], 
        telemetry_type: Optional[TelemetryType] = None,
        exception_message: Optional[str] = None,
        drop_reason: Optional[str] = None
    ) -> None:
        """Count dropped telemetry items.
        
        Args:
            count: Number of dropped items
            drop_code: The reason/code for the drop (enum or string)
            telemetry_type: The type of telemetry (e.g., REQUEST, DEPENDENCY)
            exception_message: Optional exception message for logging
            drop_reason: Optional additional reason for the drop
        """
        if not self._is_enabled or count <= 0:
            return
        
        try:
            counter = getattr(self, "_customer_statsbeat_counter", None)
            
            # Check if counter exists and has the required attribute
            if counter is None or not hasattr(counter, "total_item_drop_count"):
                return
            
            # Check if there's an existing entry for this drop code and telemetry type
            existing_entry = None
            for entry in counter.total_item_drop_count:
                entry_drop_code = entry.get("drop_code")
                entry_telemetry_type = entry.get("telemetry_type")
                
                if (entry_drop_code == drop_code and entry_telemetry_type == telemetry_type):
                    if drop_code == DropCode.CLIENT_EXCEPTION or drop_code == "CLIENT_EXCEPTION":
                        # For exceptions, we need to match on both code and message
                        if entry.get("exception_message") == exception_message:
                            existing_entry = entry
                            break
                    else:
                        existing_entry = entry
                        break
            
            if existing_entry:
                existing_entry["count"] += count
            else:
                # Create a new entry
                new_entry = {
                    "drop_code": drop_code,
                    "count": count
                }
                
                if telemetry_type:
                    new_entry["telemetry_type"] = telemetry_type
                
                if ((drop_code == DropCode.CLIENT_EXCEPTION or 
                     drop_code == "CLIENT_EXCEPTION") and exception_message):
                    new_entry["exception_message"] = exception_message
                
                # Add drop.reason if provided
                if drop_reason:
                    new_entry["drop_reason"] = drop_reason
                
                counter.total_item_drop_count.append(new_entry)
        except (TypeError, KeyError, AttributeError) as exc:
            # Log specific exceptions that might occur during dictionary operations
            logger.warning("Failed to count dropped items due to a data error: %s", str(exc))
        except Exception as exc:  # pylint: disable=broad-except
            # Still catch all other exceptions to prevent affecting the application            
            # This is acceptable in statsbeat since it should never crash the host app
            logger.warning("Failed to count dropped items: %s", str(exc))
    
    def count_retry_items(
        self, 
        count: int, 
        retry_code: Union[RetryCode, str], 
        telemetry_type: Optional[TelemetryType] = None,
        exception_message: Optional[str] = None,
        retry_reason: Optional[str] = None
    ) -> None:
        """Count retried telemetry items.
        
        Args:
            count: Number of retried items
            retry_code: The reason/code for the retry
            telemetry_type: The type of telemetry (e.g., REQUEST, DEPENDENCY)
            exception_message: Optional exception message for logging
            retry_reason: Optional additional reason for the retry
        """
        if not self._is_enabled or count <= 0:
            return
        
        try:
            counter = getattr(self, "_customer_statsbeat_counter", None)
            
            # Check if counter exists and has the required attribute
            if counter is None or not hasattr(counter, "total_item_retry_count"):
                return
            
            # Check if there's an existing entry for this retry code and telemetry type
            existing_entry = None
            for entry in counter.total_item_retry_count:
                entry_retry_code = entry.get("retry_code")
                entry_telemetry_type = entry.get("telemetry_type")
                
                if (entry_retry_code == retry_code and entry_telemetry_type == telemetry_type):
                    if (retry_code == RetryCode.CLIENT_EXCEPTION or 
                        retry_code == "CLIENT_EXCEPTION" or 
                        retry_code == RetryCode.CLIENT_TIMEOUT):
                        # For exceptions and timeouts, we need to match on both code and message
                        if entry.get("exception_message") == exception_message:
                            existing_entry = entry
                            break
                    else:
                        existing_entry = entry
                        break
            
            if existing_entry:
                existing_entry["count"] += count
            else:
                # Create a new entry
                new_entry = {
                    "retry_code": retry_code,
                    "count": count
                }
                
                if telemetry_type:
                    new_entry["telemetry_type"] = telemetry_type
                
                if ((retry_code == RetryCode.CLIENT_EXCEPTION or 
                     retry_code == "CLIENT_EXCEPTION" or
                     retry_code == RetryCode.CLIENT_TIMEOUT) and exception_message):
                    new_entry["exception_message"] = exception_message
                
                # Add retry.reason if provided
                if retry_reason:
                    new_entry["retry_reason"] = retry_reason
                
                counter.total_item_retry_count.append(new_entry)
        except (TypeError, KeyError, AttributeError) as exc:
            # Log specific exceptions that might occur during dictionary operations
            logger.warning("Failed to count retry items due to a data error: %s", str(exc))
        except Exception as exc:  # pylint: disable=broad-except
            # Still catch all other exceptions to prevent affecting the application
            # This is acceptable in statsbeat since it should never crash the host app
            logger.warning("Failed to count retry items: %s", str(exc))
    
    def shutdown(self) -> None:
        """Shutdown the customer statsbeat metrics."""
        if not getattr(self, "_is_enabled", False):
            return
        
        try:
            # Shutdown the meter provider
            if hasattr(self, '_customer_statsbeat_meter_provider'):
                self._customer_statsbeat_meter_provider.shutdown()
        except AttributeError as exc:
            # Specific error when meter provider doesn't have shutdown
            logger.warning("Error during statsbeat shutdown - attribute error: %s", str(exc))
        except Exception as exc:  # pylint: disable=broad-except
            # Still catch all other exceptions to prevent affecting the application            
            # This is acceptable in statsbeat since it should never crash the host app
            logger.warning("Error during statsbeat shutdown: %s", str(exc))
    
    def _item_success_callback(self, options: CallbackOptions) -> List[Observation]:
        """Callback for reporting successful items.
        
        Args:
            options: Callback options
        
        Returns:
            List of observations
        """
        if not getattr(self, "_is_enabled", False):
            return []

        try:
            observations = []
            counter = getattr(self, "_customer_statsbeat_counter", None)
            
            # Check if counter exists and has the required attribute
            if counter is None or not hasattr(counter, "total_item_success_count"):
                return []
            
            # Create observations for each unique entry
            for entry in counter.total_item_success_count:
                if entry.get("count", 0) > 0:
                    attributes = {
                        "language": self._customer_properties.language,
                        "version": self._customer_properties.version,
                        "compute_type": self._customer_properties.compute_type,
                    }
                    
                    # Add telemetry_type if present
                    if "telemetry_type" in entry:
                        attributes["telemetry_type"] = entry["telemetry_type"]
                    
                    observation = Observation(entry["count"], attributes)
                    observations.append(observation)
                    
                    # Reset the count after reporting
                    entry["count"] = 0
            
            return observations
        except (KeyError, AttributeError) as exc:
            # Log specific exceptions that might occur with dictionary access
            logger.warning("Error in item success callback - data access error: %s", str(exc))
            return []
        except Exception as exc:  # pylint: disable=broad-except            
            # Still catch all other exceptions to prevent affecting the application
            logger.warning("Error in item success callback: %s", str(exc))
            return []
    
    def _item_drop_callback(self, options: CallbackOptions) -> List[Observation]:
        """Callback for reporting dropped items.
        
        Args:
            options: Callback options
        
        Returns:
            List of observations
        """
        if not getattr(self, "_is_enabled", False):
            return []
        
        try:
            observations = []
            counter = getattr(self, "_customer_statsbeat_counter", None)
            
            # Check if counter exists and has the required attribute
            if counter is None or not hasattr(counter, "total_item_drop_count"):
                return []
            
            # Create observations for each unique entry
            for entry in counter.total_item_drop_count:
                if entry.get("count", 0) > 0:
                    # Get drop code - could be either an enum or a string (e.g., a status code)
                    drop_code = entry.get("drop_code")
                    
                    attributes = {
                        "language": self._customer_properties.language,
                        "version": self._customer_properties.version,
                        "compute_type": self._customer_properties.compute_type,
                        # Ensure it's a string for non-enum values like status codes
                        "drop.code": str(drop_code)
                    }
                    
                    # Add telemetry_type if present
                    if "telemetry_type" in entry:
                        attributes["telemetry_type"] = entry["telemetry_type"]
                    
                    # Add exception message for CLIENT_EXCEPTION as drop.reason
                    if drop_code in (DropCode.CLIENT_EXCEPTION, "CLIENT_EXCEPTION"):
                        if entry.get("exception_message"):
                            attributes["drop.reason"] = entry["exception_message"]
                    
                    # Add drop.reason if present (new field per spec)
                    drop_reason = entry.get("drop_reason")
                    if drop_reason:
                        attributes["drop.reason"] = drop_reason
                    
                    observation = Observation(entry["count"], attributes)
                    observations.append(observation)
                    
                    # Reset the count after reporting
                    entry["count"] = 0
            
            return observations
        except (KeyError, AttributeError, TypeError) as exc:
            # Log specific exceptions that might occur with dictionary access
            logger.warning("Error in item drop callback - data access error: %s", str(exc))
            return []
        except Exception as exc:  # pylint: disable=broad-except            
            # Still catch all other exceptions to prevent affecting the application
            logger.warning("Error in item drop callback: %s", str(exc))
            return []
    
    def _item_retry_callback(self, options: CallbackOptions) -> List[Observation]:
        """Callback for reporting retried items.
        
        Args:
            options: Callback options
        
        Returns:
            List of observations
        """
        if not getattr(self, "_is_enabled", False):
            return []
        
        try:
            observations = []
            counter = getattr(self, "_customer_statsbeat_counter", None)
            
            # Check if counter exists and has the required attribute
            if counter is None or not hasattr(counter, "total_item_retry_count"):
                return []
            
            # Create observations for each unique entry
            for entry in counter.total_item_retry_count:
                if entry.get("count", 0) > 0:
                    # Get retry code - could be either an enum or a string (e.g., a status code)
                    retry_code = entry.get("retry_code")
                    
                    attributes = {
                        "language": self._customer_properties.language,
                        "version": self._customer_properties.version,
                        "compute_type": self._customer_properties.compute_type,
                        # Ensure it's a string for non-enum values like status codes
                        "retry.code": str(retry_code)
                    }
                    
                    # Add telemetry_type if present
                    if "telemetry_type" in entry:
                        attributes["telemetry_type"] = entry["telemetry_type"]
                    
                    # Add exception message for CLIENT_EXCEPTION or CLIENT_TIMEOUT as retry.reason
                    if retry_code in (RetryCode.CLIENT_EXCEPTION, "CLIENT_EXCEPTION", RetryCode.CLIENT_TIMEOUT):
                        if entry.get("exception_message"):
                            attributes["retry.reason"] = entry["exception_message"]
                    
                    # Add retry.reason if present (new field per spec)
                    retry_reason = entry.get("retry_reason")
                    if retry_reason:
                        attributes["retry.reason"] = retry_reason
                    
                    observation = Observation(entry["count"], attributes)
                    observations.append(observation)
                    
                    # Reset the count after reporting
                    entry["count"] = 0
            
            return observations
        except (KeyError, AttributeError, TypeError) as exc:
            # Log specific exceptions that might occur with dictionary access
            logger.warning("Error in item retry callback - data access error: %s", str(exc))
            return []
        except Exception as exc:  # pylint: disable=broad-except
            # Still catch all other exceptions to prevent affecting the application
            logger.warning("Error in item retry callback: %s", str(exc))
            return []
