import logging
import threading
from azure.monitor.opentelemetry.exporter._configuration import _update_configuration_and_get_refresh_interval

logger = logging.getLogger(__name__)

class _ConfigurationWorker:
    """Worker that periodically refreshes configuration in a background thread.
    
    This class manages a daemon thread that periodically calls a configuration refresh function
    and updates the refresh interval dynamically based on configuration responses.
    This class is implemented as a singleton to ensure only one configuration refresh process
    exists across the application. Multiple requests to start configuration workers with
    the same refresh_callback will reuse the existing worker instance.    
    """

    _instance = None
    _instance_lock = threading.Lock()
    _refresh_interval = 1800.0  # Default to 30 minutes in seconds
    _interval_lock = threading.Lock()
    _refresh_thread = None
    _shutdown_event = None
    _initialized = False
    _running = False
    _state_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(_ConfigurationWorker, cls).__new__(cls)
            return cls._instance

    def __init__(self,) -> None:
        """Initialize the ConfigurationWorker. Will not reinitialize if already created."""
        with self._state_lock:
            if not self._initialized:
                self._shutdown_event = threading.Event()
                self._refresh_thread = threading.Thread(
                    target=self._get_configuration,
                    name="ConfigurationWorker",
                    daemon=True
                )
                self._shutdown_event.clear()
                self._refresh_thread.start()
                self._running = True
                self._initialized = True

    def shutdown(self) -> None:
        """Shut down the configuration refresh worker thread."""
        with self._state_lock:
            if not self._initialized or not self._running:
                return

            self._running = False
            if self._shutdown_event:
                self._shutdown_event.set()
            if self._refresh_thread and self._refresh_thread.is_alive():
                self._refresh_thread.join()

    def get_refresh_interval(self) -> float:
        """Get the current refresh interval.

        :return: Current refresh interval in seconds.
        """
        with self._interval_lock:
            return self._refresh_interval

    def _get_configuration(self) -> None:
        """Update configuration loop that runs in the background thread.

        This method will be called periodically to refresh the configuration.

        """
        if self._shutdown_event:
            while not self._shutdown_event.is_set():
                try:
                    # Perform the refresh operation
                    with self._interval_lock:
                        self._refresh_interval = _update_configuration_and_get_refresh_interval()  
                except Exception as ex:
                    logger.warning("Configuration refresh failed: %s", ex)
                
                # Wait until next refresh or shutdown
                self._shutdown_event.wait(self.get_refresh_interval())