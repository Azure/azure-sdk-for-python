"""
Unit tests for red_team._utils.retry_utils module.
"""

import asyncio
import logging

import httpcore
import httpx
import pytest
from unittest.mock import MagicMock, patch

from azure.ai.evaluation.red_team._utils.retry_utils import (
    RetryManager,
    create_standard_retry_manager,
    create_retry_decorator,
)


# ---------------------------------------------------------------------------
# RetryManager.__init__
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestRetryManagerInit:
    """Test RetryManager initialisation and default config values."""

    def test_default_values(self):
        """Verify class-level defaults propagate when no args given."""
        manager = RetryManager()

        assert manager.max_attempts == 5
        assert manager.min_wait == 2
        assert manager.max_wait == 30
        assert manager.multiplier == 1.5
        assert isinstance(manager.logger, logging.Logger)

    def test_custom_values(self):
        """Verify custom values override defaults."""
        logger = logging.getLogger("custom")
        manager = RetryManager(
            logger=logger,
            max_attempts=10,
            min_wait=5,
            max_wait=60,
            multiplier=3.0,
        )

        assert manager.logger is logger
        assert manager.max_attempts == 10
        assert manager.min_wait == 5
        assert manager.max_wait == 60
        assert manager.multiplier == 3.0

    def test_none_logger_falls_back(self):
        """Passing None should create a module-level logger."""
        manager = RetryManager(logger=None)
        assert manager.logger is not None
        assert isinstance(manager.logger, logging.Logger)


# ---------------------------------------------------------------------------
# RetryManager.should_retry_exception – retryable network exceptions
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestShouldRetryException:
    """Test should_retry_exception with various exception types."""

    def setup_method(self):
        self.manager = RetryManager()

    # -- retryable exceptions ------------------------------------------------

    def test_httpx_connect_timeout(self):
        assert self.manager.should_retry_exception(httpx.ConnectTimeout("timeout"))

    def test_httpx_read_timeout(self):
        assert self.manager.should_retry_exception(httpx.ReadTimeout("timeout"))

    def test_httpx_connect_error(self):
        assert self.manager.should_retry_exception(httpx.ConnectError("conn err"))

    def test_httpx_http_error(self):
        assert self.manager.should_retry_exception(httpx.HTTPError("http err"))

    def test_httpx_timeout_exception(self):
        assert self.manager.should_retry_exception(httpx.TimeoutException("timeout"))

    def test_httpcore_read_timeout(self):
        assert self.manager.should_retry_exception(httpcore.ReadTimeout("timeout"))

    def test_asyncio_timeout_error(self):
        assert self.manager.should_retry_exception(asyncio.TimeoutError())

    def test_connection_error(self):
        assert self.manager.should_retry_exception(ConnectionError("refused"))

    def test_connection_refused_error(self):
        assert self.manager.should_retry_exception(ConnectionRefusedError("refused"))

    def test_connection_reset_error(self):
        assert self.manager.should_retry_exception(ConnectionResetError("reset"))

    def test_timeout_error(self):
        assert self.manager.should_retry_exception(TimeoutError("timed out"))

    def test_os_error(self):
        assert self.manager.should_retry_exception(OSError("os err"))

    def test_io_error(self):
        assert self.manager.should_retry_exception(IOError("io err"))

    # -- HTTPStatusError special cases ---------------------------------------

    def _make_status_error(self, status_code: int, body: str = "error") -> httpx.HTTPStatusError:
        """Helper to create an HTTPStatusError with a given status code."""
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(status_code, request=request, text=body)
        return httpx.HTTPStatusError(
            message=body,
            request=request,
            response=response,
        )

    def test_http_status_error_is_network_exception_retryable(self):
        """HTTPStatusError is in NETWORK_EXCEPTIONS so isinstance check returns True."""
        exc = self._make_status_error(400)
        # The first isinstance check on NETWORK_EXCEPTIONS returns True for any HTTPStatusError,
        # so should_retry_exception returns True before reaching the special-case block.
        assert self.manager.should_retry_exception(exc) is True

    def test_http_status_error_500(self):
        """500 status should be retryable (also covered by isinstance)."""
        exc = self._make_status_error(500)
        assert self.manager.should_retry_exception(exc) is True

    def test_http_status_error_429(self):
        """429 (rate-limited) is an HTTPStatusError – retryable via isinstance."""
        exc = self._make_status_error(429)
        assert self.manager.should_retry_exception(exc) is True

    def test_http_status_error_model_error(self):
        """model_error in message should be retryable."""
        exc = self._make_status_error(422, body="model_error: bad output")
        assert self.manager.should_retry_exception(exc) is True

    # -- non-retryable exceptions --------------------------------------------

    def test_value_error_not_retryable(self):
        assert self.manager.should_retry_exception(ValueError("bad")) is False

    def test_runtime_error_not_retryable(self):
        assert self.manager.should_retry_exception(RuntimeError("oops")) is False

    def test_key_error_not_retryable(self):
        assert self.manager.should_retry_exception(KeyError("key")) is False

    def test_type_error_not_retryable(self):
        assert self.manager.should_retry_exception(TypeError("type")) is False


# ---------------------------------------------------------------------------
# RetryManager.should_retry_exception – Azure exceptions
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestShouldRetryAzureExceptions:
    """Test that Azure SDK exceptions are retryable when available."""

    def test_service_request_error_retryable(self):
        from azure.core.exceptions import ServiceRequestError

        manager = RetryManager()
        assert manager.should_retry_exception(ServiceRequestError("svc req err"))

    def test_service_response_error_retryable(self):
        from azure.core.exceptions import ServiceResponseError

        manager = RetryManager()
        assert manager.should_retry_exception(ServiceResponseError("svc resp err"))


# ---------------------------------------------------------------------------
# RetryManager.log_retry_attempt
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestLogRetryAttempt:
    """Test log_retry_attempt logging."""

    def test_logs_warning_on_exception(self):
        mock_logger = MagicMock()
        manager = RetryManager(logger=mock_logger)

        retry_state = MagicMock()
        retry_state.attempt_number = 2
        retry_state.outcome.exception.return_value = ConnectionError("conn refused")
        retry_state.next_action.sleep = 4.0

        manager.log_retry_attempt(retry_state)

        mock_logger.warning.assert_called_once()
        msg = mock_logger.warning.call_args[0][0]
        assert "2/5" in msg
        assert "ConnectionError" in msg
        assert "conn refused" in msg
        assert "4.0" in msg

    def test_no_log_when_no_exception(self):
        mock_logger = MagicMock()
        manager = RetryManager(logger=mock_logger)

        retry_state = MagicMock()
        retry_state.outcome.exception.return_value = None

        manager.log_retry_attempt(retry_state)

        mock_logger.warning.assert_not_called()


# ---------------------------------------------------------------------------
# RetryManager.log_retry_error
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestLogRetryError:
    """Test log_retry_error logging and return value."""

    def test_logs_error_and_returns_exception(self):
        mock_logger = MagicMock()
        manager = RetryManager(logger=mock_logger)

        exc = TimeoutError("deadline exceeded")
        retry_state = MagicMock()
        retry_state.attempt_number = 5
        retry_state.outcome.exception.return_value = exc

        result = manager.log_retry_error(retry_state)

        mock_logger.error.assert_called_once()
        msg = mock_logger.error.call_args[0][0]
        assert "5 attempts" in msg
        assert "TimeoutError" in msg
        assert "deadline exceeded" in msg
        assert result is exc


# ---------------------------------------------------------------------------
# RetryManager.create_retry_decorator
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestCreateRetryDecorator:
    """Test create_retry_decorator returns a usable tenacity decorator."""

    def test_returns_callable(self):
        manager = RetryManager()
        decorator = manager.create_retry_decorator()
        assert callable(decorator)

    def test_returns_callable_with_context(self):
        manager = RetryManager()
        decorator = manager.create_retry_decorator(context="MyContext")
        assert callable(decorator)

    def test_decorator_wraps_function(self):
        """Verify the decorator can wrap a function (produces a tenacity wrapper)."""
        manager = RetryManager(max_attempts=1)
        decorator = manager.create_retry_decorator()

        @decorator
        def dummy():
            return 42

        # The wrapped function should still be callable
        assert dummy() == 42

    def test_decorator_context_in_log(self):
        """Verify context prefix appears in retry log messages."""
        mock_logger = MagicMock()
        manager = RetryManager(logger=mock_logger, max_attempts=2, min_wait=0, max_wait=0)
        decorator = manager.create_retry_decorator(context="TestCtx")

        call_count = 0

        @decorator
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("fail")
            return "ok"

        result = flaky()
        assert result == "ok"
        # The warning log should contain the context prefix
        mock_logger.warning.assert_called_once()
        msg = mock_logger.warning.call_args[0][0]
        assert "[TestCtx]" in msg

    def test_decorator_no_context_prefix(self):
        """Verify no context prefix when context is empty."""
        mock_logger = MagicMock()
        manager = RetryManager(logger=mock_logger, max_attempts=2, min_wait=0, max_wait=0)
        decorator = manager.create_retry_decorator(context="")

        call_count = 0

        @decorator
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("fail")
            return "ok"

        result = flaky()
        assert result == "ok"
        msg = mock_logger.warning.call_args[0][0]
        assert not msg.startswith("[")

    def test_decorator_logs_final_error(self):
        """Verify final error is logged when all retries exhausted."""
        mock_logger = MagicMock()
        manager = RetryManager(logger=mock_logger, max_attempts=2, min_wait=0, max_wait=0)
        decorator = manager.create_retry_decorator(context="FinalErr")

        @decorator
        def always_fail():
            raise ConnectionError("permanent failure")

        # retry_error_callback returns the exception as the function result
        result = always_fail()
        assert isinstance(result, ConnectionError)
        assert "permanent failure" in str(result)

        mock_logger.error.assert_called_once()
        msg = mock_logger.error.call_args[0][0]
        assert "[FinalErr]" in msg
        assert "All retries failed" in msg


# ---------------------------------------------------------------------------
# RetryManager.get_retry_config
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestGetRetryConfig:
    """Test get_retry_config returns a valid configuration dict."""

    def test_returns_dict_with_network_retry_key(self):
        manager = RetryManager()
        config = manager.get_retry_config()

        assert isinstance(config, dict)
        assert "network_retry" in config

    def test_network_retry_has_required_keys(self):
        manager = RetryManager()
        config = manager.get_retry_config()
        network = config["network_retry"]

        assert "retry" in network
        assert "stop" in network
        assert "wait" in network
        assert "retry_error_callback" in network
        assert "before_sleep" in network

    def test_callbacks_reference_manager_methods(self):
        manager = RetryManager()
        config = manager.get_retry_config()
        network = config["network_retry"]

        # Bound methods create new objects each access, so compare via __func__
        assert network["retry_error_callback"].__func__ is RetryManager.log_retry_error
        assert network["before_sleep"].__func__ is RetryManager.log_retry_attempt


# ---------------------------------------------------------------------------
# Module-level factory: create_standard_retry_manager
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestCreateStandardRetryManager:
    """Test create_standard_retry_manager factory function."""

    def test_returns_retry_manager(self):
        manager = create_standard_retry_manager()
        assert isinstance(manager, RetryManager)

    def test_uses_defaults(self):
        manager = create_standard_retry_manager()
        assert manager.max_attempts == RetryManager.DEFAULT_MAX_ATTEMPTS
        assert manager.min_wait == RetryManager.DEFAULT_MIN_WAIT
        assert manager.max_wait == RetryManager.DEFAULT_MAX_WAIT
        assert manager.multiplier == RetryManager.DEFAULT_MULTIPLIER

    def test_custom_logger(self):
        logger = logging.getLogger("factory_test")
        manager = create_standard_retry_manager(logger=logger)
        assert manager.logger is logger

    def test_none_logger(self):
        manager = create_standard_retry_manager(logger=None)
        assert isinstance(manager.logger, logging.Logger)


# ---------------------------------------------------------------------------
# Module-level convenience: create_retry_decorator
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestModuleLevelCreateRetryDecorator:
    """Test module-level create_retry_decorator convenience function."""

    def test_returns_callable(self):
        decorator = create_retry_decorator()
        assert callable(decorator)

    def test_custom_parameters(self):
        logger = logging.getLogger("mod_dec_test")
        decorator = create_retry_decorator(
            logger=logger,
            context="CustomCtx",
            max_attempts=3,
            min_wait=1,
            max_wait=10,
        )
        assert callable(decorator)

    def test_wraps_function_successfully(self):
        decorator = create_retry_decorator(max_attempts=1)

        @decorator
        def simple():
            return "hello"

        assert simple() == "hello"

    def test_retries_on_network_error(self):
        decorator = create_retry_decorator(max_attempts=3, min_wait=0, max_wait=0)

        call_count = 0

        @decorator
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("transient")
            return "recovered"

        assert flaky_func() == "recovered"
        assert call_count == 3

    def test_does_not_retry_non_retryable(self):
        decorator = create_retry_decorator(max_attempts=3, min_wait=0, max_wait=0)

        @decorator
        def bad():
            raise ValueError("not retryable")

        with pytest.raises(ValueError, match="not retryable"):
            bad()


# ---------------------------------------------------------------------------
# AZURE_EXCEPTIONS import handling
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestAzureExceptionsImport:
    """Test that AZURE_EXCEPTIONS is populated when azure.core is available."""

    def test_azure_exceptions_tuple_populated(self):
        """When azure.core is importable, AZURE_EXCEPTIONS should contain the two classes."""
        from azure.ai.evaluation.red_team._utils.retry_utils import AZURE_EXCEPTIONS
        from azure.core.exceptions import ServiceRequestError, ServiceResponseError

        assert ServiceRequestError in AZURE_EXCEPTIONS
        assert ServiceResponseError in AZURE_EXCEPTIONS

    def test_network_exceptions_includes_azure(self):
        """NETWORK_EXCEPTIONS should include AZURE_EXCEPTIONS members."""
        from azure.core.exceptions import ServiceRequestError, ServiceResponseError

        assert ServiceRequestError in RetryManager.NETWORK_EXCEPTIONS
        assert ServiceResponseError in RetryManager.NETWORK_EXCEPTIONS

    def test_azure_import_error_fallback(self):
        """When azure.core is NOT importable, AZURE_EXCEPTIONS should be empty tuple.

        We simulate by importing the module-level constant after patching.
        """
        import importlib
        import azure.ai.evaluation.red_team._utils.retry_utils as mod

        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def mock_import(name, *args, **kwargs):
            if name == "azure.core.exceptions":
                raise ImportError("mocked")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            importlib.reload(mod)
            assert mod.AZURE_EXCEPTIONS == ()

        # Reload again to restore original state
        importlib.reload(mod)
