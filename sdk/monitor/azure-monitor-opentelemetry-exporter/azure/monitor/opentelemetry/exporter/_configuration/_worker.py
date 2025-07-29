import logging
import threading
from azure.monitor.opentelemetry.exporter._configuration import _update_configuration_and_get_refresh_interval

logger = logging.getLogger(__name__)

class _ConfigurationWorker:
    """Worker that periodically refreshes configuration in a background thread.
    
    This class manages a daemon thread that periodically calls a configuration refresh function
    and updates the refresh interval dynamically based on configuration responses.
    """

    def __init__(self, refresh_interval=None) -> None:
        """Initialize the ConfigurationWorker."""
        self._default_refresh_interval = 3600.0  # Default to 60 minutes in seconds
        self._interval_lock = threading.Lock()
        self._state_lock = threading.Lock()
        
        self._shutdown_event = threading.Event()
        self._refresh_thread = threading.Thread(
            target=self._get_configuration,
            name="ConfigurationWorker",
            daemon=True
        )
        self._refresh_interval = refresh_interval or self._default_refresh_interval
        self._shutdown_event.clear()
        self._refresh_thread.start()
        self._running = True

    def shutdown(self) -> None:
        """Shut down the configuration refresh worker thread."""
        with self._state_lock:
            if not self._running:
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
