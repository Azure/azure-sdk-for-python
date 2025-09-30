# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
import threading
import random
from azure.monitor.opentelemetry.exporter._constants import _ONE_SETTINGS_PYTHON_TARGETING

logger = logging.getLogger(__name__)

class _ConfigurationWorker:
    """Background worker thread for periodic configuration refresh from OneSettings.

    This class manages a daemon background thread that periodically fetches configuration
    updates from the OneSettings service. The worker automatically adjusts its refresh
    interval based on server responses and provides graceful shutdown capabilities.

    The worker operates independently once started and handles all configuration refresh
    operations in the background, including error handling and dynamic interval adjustment.

    Attributes:
        _default_refresh_interval (int): Default refresh interval (3600 seconds/1 hour)
        _lock (threading.Lock): Thread lock for worker state management
        _shutdown_event (threading.Event): Event for coordinating graceful shutdown
        _refresh_thread (threading.Thread): Background daemon thread for configuration refresh
        _refresh_interval (int): Current refresh interval in seconds
        _running (bool): Flag indicating if the worker is currently running
    """

    def __init__(self, configuration_manager, refresh_interval=None) -> None:
        """Initialize and start the configuration worker thread.

        Creates and starts a background daemon thread that will periodically refresh
        configuration from OneSettings. The thread starts immediately upon initialization
        with a random startup delay to prevent thundering herd issues.

        Args:
            configuration_manager: The ConfigurationManager instance to update
            refresh_interval (Optional[int]): Initial refresh interval in seconds.
                If None, defaults to 3600 seconds (1 hour).

        Note:
            The background thread is created as a daemon thread and includes a random
            0-15 second startup delay to stagger configuration requests across multiple
            SDK instances during startup or recovery from outages.
        """
        self._configuration_manager = configuration_manager
        self._default_refresh_interval = 3600  # Default to 60 minutes in seconds
        self._lock = threading.Lock()  # Single lock for all worker state

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
        """Gracefully shut down the configuration refresh worker thread.

        This method signals the background thread to stop and waits for it to
        complete its current operation before returning. The shutdown is coordinated
        using a threading.Event to ensure the thread can exit cleanly.

        The method is thread-safe and can be called multiple times. Subsequent calls
        after the first shutdown will have no effect.

        Note:
            This method blocks until the background thread has fully stopped.
            If the thread is in the middle of a configuration refresh, it will
            complete that operation before shutting down.
        """
        thread_to_join = None
        with self._lock:
            if not self._running:
                return

            self._running = False
            self._shutdown_event.set()
            if self._refresh_thread and self._refresh_thread.is_alive():
                thread_to_join = self._refresh_thread

        # Join outside the lock to prevent deadlock
        if thread_to_join:
            thread_to_join.join()

    def get_refresh_interval(self) -> int:
        """Get the current configuration refresh interval.

        Returns the current refresh interval that determines how often the worker
        fetches configuration updates from OneSettings. This value can change
        dynamically based on server responses.

        :return: Current refresh interval in seconds.
        :rtype: int

        Note:
            This method is thread-safe and can be called from any thread.
        """
        with self._lock:
            return self._refresh_interval

    def _get_configuration(self) -> None:
        """Main configuration refresh loop executed in the background thread.

        This method implements the core logic of the configuration worker:
        1. Applies random startup delay (0-15 seconds) to stagger requests
        2. Continuously loops until shutdown is requested
        3. Calls the configuration update function to fetch new settings
        4. Updates the refresh interval based on the server response
        5. Waits for the next refresh cycle or shutdown signal

        The initial random delay helps prevent thundering herd problems when many
        SDK instances start up simultaneously after service outages or deployments.

        Error Handling:
            - All exceptions are caught and logged as warnings
            - Errors do not stop the worker from continuing its refresh cycle
            - The worker maintains operation even if individual requests fail

        Shutdown Coordination:
            - Uses _shutdown_event.is_set() to check for shutdown requests
            - Uses _shutdown_event.wait() for interruptible sleep periods
            - Exits cleanly when shutdown is requested
        """
        # Add random startup delay (5-15 seconds) to stagger configuration requests
        # This prevents thundering herd when many SDKs start simultaneously
        startup_delay = random.uniform(5.0, 15.0)

        if self._shutdown_event.wait(startup_delay):
            # Shutdown requested during startup delay
            return

        while not self._shutdown_event.is_set():
            try:
                with self._lock:
                    self._refresh_interval = \
                    self._configuration_manager.get_configuration_and_refresh_interval(_ONE_SETTINGS_PYTHON_TARGETING)
                    # Capture interval while we have the lock
                    interval = self._refresh_interval
            except Exception as ex:  # pylint: disable=broad-exception-caught
                logger.warning("Configuration refresh failed: %s", ex)
                # Use current interval on error
                interval = self.get_refresh_interval()

            self._shutdown_event.wait(interval)
