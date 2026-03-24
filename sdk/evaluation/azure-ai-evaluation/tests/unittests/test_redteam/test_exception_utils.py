"""
Unit tests for red_team._utils.exception_utils module.
"""

import asyncio
import logging
import pytest
from unittest.mock import MagicMock, patch

import httpx
import httpcore

from azure.ai.evaluation.red_team._utils.exception_utils import (
    ErrorCategory,
    ErrorSeverity,
    RedTeamError,
    ExceptionHandler,
    create_exception_handler,
    exception_context,
)


# ---------------------------------------------------------------------------
# ErrorCategory enum
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestErrorCategory:
    """Test ErrorCategory enum values."""

    def test_all_categories_exist(self):
        categories = {
            "NETWORK": "network",
            "AUTHENTICATION": "authentication",
            "CONFIGURATION": "configuration",
            "DATA_PROCESSING": "data_processing",
            "ORCHESTRATOR": "orchestrator",
            "EVALUATION": "evaluation",
            "FILE_IO": "file_io",
            "TIMEOUT": "timeout",
            "UNKNOWN": "unknown",
        }
        for attr, value in categories.items():
            assert getattr(ErrorCategory, attr).value == value

    def test_category_count(self):
        assert len(ErrorCategory) == 9


# ---------------------------------------------------------------------------
# ErrorSeverity enum
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestErrorSeverity:
    """Test ErrorSeverity enum values."""

    def test_all_severities_exist(self):
        severities = {
            "LOW": "low",
            "MEDIUM": "medium",
            "HIGH": "high",
            "FATAL": "fatal",
        }
        for attr, value in severities.items():
            assert getattr(ErrorSeverity, attr).value == value

    def test_severity_count(self):
        assert len(ErrorSeverity) == 4


# ---------------------------------------------------------------------------
# RedTeamError exception class
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestRedTeamError:
    """Test RedTeamError exception class."""

    def test_defaults(self):
        err = RedTeamError("boom")
        assert str(err) == "boom"
        assert err.message == "boom"
        assert err.category == ErrorCategory.UNKNOWN
        assert err.severity == ErrorSeverity.MEDIUM
        assert err.context == {}
        assert err.original_exception is None

    def test_custom_fields(self):
        orig = ValueError("bad value")
        ctx = {"key": "val"}
        err = RedTeamError(
            message="custom",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            context=ctx,
            original_exception=orig,
        )
        assert err.message == "custom"
        assert err.category == ErrorCategory.NETWORK
        assert err.severity == ErrorSeverity.HIGH
        assert err.context is ctx
        assert err.original_exception is orig

    def test_is_exception(self):
        err = RedTeamError("test")
        assert isinstance(err, Exception)

    def test_none_context_defaults_to_empty_dict(self):
        err = RedTeamError("msg", context=None)
        assert err.context == {}


# ---------------------------------------------------------------------------
# ExceptionHandler – categorize_exception
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestCategorizeException:
    """Test ExceptionHandler.categorize_exception with every exception type."""

    @pytest.fixture(autouse=True)
    def _handler(self):
        self.handler = ExceptionHandler(logger=logging.getLogger("test"))

    # -- Network exceptions --------------------------------------------------
    def test_httpx_connect_timeout(self):
        exc = httpx.ConnectTimeout("timeout")
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_httpx_read_timeout(self):
        exc = httpx.ReadTimeout("timeout")
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_httpx_connect_error(self):
        exc = httpx.ConnectError("refused")
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_httpx_http_error(self):
        exc = httpx.HTTPError("error")
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_httpx_timeout_exception(self):
        exc = httpx.TimeoutException("timeout")
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_httpcore_read_timeout(self):
        exc = httpcore.ReadTimeout("timeout")
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_connection_error(self):
        assert self.handler.categorize_exception(ConnectionError("err")) == ErrorCategory.NETWORK

    def test_connection_refused_error(self):
        assert self.handler.categorize_exception(ConnectionRefusedError("err")) == ErrorCategory.NETWORK

    def test_connection_reset_error(self):
        assert self.handler.categorize_exception(ConnectionResetError("err")) == ErrorCategory.NETWORK

    # -- Timeout exceptions ---------------------------------------------------
    def test_asyncio_timeout_error(self):
        assert self.handler.categorize_exception(asyncio.TimeoutError()) == ErrorCategory.TIMEOUT

    def test_builtin_timeout_error(self):
        assert self.handler.categorize_exception(TimeoutError("t")) == ErrorCategory.TIMEOUT

    # -- File I/O exceptions --------------------------------------------------
    def test_io_error(self):
        assert self.handler.categorize_exception(IOError("io")) == ErrorCategory.FILE_IO

    def test_os_error(self):
        assert self.handler.categorize_exception(OSError("os")) == ErrorCategory.FILE_IO

    def test_file_not_found_error(self):
        assert self.handler.categorize_exception(FileNotFoundError("nf")) == ErrorCategory.FILE_IO

    def test_permission_error(self):
        assert self.handler.categorize_exception(PermissionError("perm")) == ErrorCategory.FILE_IO

    # -- HTTP status code based categorization --------------------------------
    def _make_http_status_error(self, status_code):
        """Create an httpx.HTTPStatusError with the given status code."""
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(status_code, request=request)
        return httpx.HTTPStatusError("err", request=request, response=response)

    def test_http_500_server_error(self):
        # 500 is a network exception via isinstance first, but also has .response
        # isinstance(HTTPStatusError, HTTPError) is True → NETWORK
        exc = self._make_http_status_error(500)
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_http_502_server_error(self):
        exc = self._make_http_status_error(502)
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_http_429_rate_limit(self):
        # HTTPStatusError is a subclass of HTTPError → caught by isinstance → NETWORK
        exc = self._make_http_status_error(429)
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_http_401_with_non_httpx_exception(self):
        """Test 401 status categorization via the hasattr branch."""
        exc = Exception("unauthorized")
        exc.response = MagicMock(status_code=401)
        assert self.handler.categorize_exception(exc) == ErrorCategory.AUTHENTICATION

    def test_http_403_with_non_httpx_exception(self):
        exc = Exception("forbidden")
        exc.response = MagicMock(status_code=403)
        assert self.handler.categorize_exception(exc) == ErrorCategory.CONFIGURATION

    def test_http_500_with_non_httpx_exception(self):
        exc = Exception("internal error")
        exc.response = MagicMock(status_code=500)
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    def test_http_503_with_non_httpx_exception(self):
        exc = Exception("service unavailable")
        exc.response = MagicMock(status_code=503)
        assert self.handler.categorize_exception(exc) == ErrorCategory.NETWORK

    # -- String-based keyword categorization ----------------------------------
    def test_keyword_authentication(self):
        assert self.handler.categorize_exception(ValueError("authentication failed")) == ErrorCategory.AUTHENTICATION

    def test_keyword_unauthorized(self):
        assert self.handler.categorize_exception(RuntimeError("unauthorized access")) == ErrorCategory.AUTHENTICATION

    def test_keyword_configuration(self):
        assert self.handler.categorize_exception(Exception("bad configuration")) == ErrorCategory.CONFIGURATION

    def test_keyword_config(self):
        assert self.handler.categorize_exception(Exception("invalid config")) == ErrorCategory.CONFIGURATION

    def test_keyword_orchestrator(self):
        assert self.handler.categorize_exception(Exception("orchestrator failed")) == ErrorCategory.ORCHESTRATOR

    def test_keyword_evaluation(self):
        assert self.handler.categorize_exception(Exception("evaluation error")) == ErrorCategory.EVALUATION

    def test_keyword_evaluate(self):
        assert self.handler.categorize_exception(Exception("cannot evaluate")) == ErrorCategory.EVALUATION

    def test_keyword_model_error(self):
        assert self.handler.categorize_exception(Exception("model_error occurred")) == ErrorCategory.EVALUATION

    def test_keyword_data(self):
        assert self.handler.categorize_exception(Exception("bad data format")) == ErrorCategory.DATA_PROCESSING

    def test_keyword_json(self):
        assert self.handler.categorize_exception(Exception("json parse error")) == ErrorCategory.DATA_PROCESSING

    # -- Unknown fallback -----------------------------------------------------
    def test_generic_exception_falls_to_unknown(self):
        assert self.handler.categorize_exception(RuntimeError("something")) == ErrorCategory.UNKNOWN

    def test_plain_value_error_unknown(self):
        assert self.handler.categorize_exception(ValueError("nope")) == ErrorCategory.UNKNOWN


# ---------------------------------------------------------------------------
# ExceptionHandler – determine_severity
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestDetermineSeverity:
    """Test ExceptionHandler.determine_severity."""

    @pytest.fixture(autouse=True)
    def _handler(self):
        self.handler = ExceptionHandler(logger=logging.getLogger("test"))

    def test_memory_error_is_fatal(self):
        assert self.handler.determine_severity(MemoryError(), ErrorCategory.UNKNOWN) == ErrorSeverity.FATAL

    def test_system_exit_is_fatal(self):
        assert self.handler.determine_severity(SystemExit(), ErrorCategory.UNKNOWN) == ErrorSeverity.FATAL

    def test_keyboard_interrupt_is_fatal(self):
        assert self.handler.determine_severity(KeyboardInterrupt(), ErrorCategory.UNKNOWN) == ErrorSeverity.FATAL

    def test_authentication_category_is_high(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.AUTHENTICATION) == ErrorSeverity.HIGH

    def test_configuration_category_is_high(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.CONFIGURATION) == ErrorSeverity.HIGH

    def test_file_io_critical_file_is_high(self):
        assert (
            self.handler.determine_severity(IOError("x"), ErrorCategory.FILE_IO, context={"critical_file": True})
            == ErrorSeverity.HIGH
        )

    def test_file_io_non_critical_is_medium(self):
        assert self.handler.determine_severity(IOError("x"), ErrorCategory.FILE_IO) == ErrorSeverity.MEDIUM

    def test_file_io_critical_false_is_medium(self):
        assert (
            self.handler.determine_severity(IOError("x"), ErrorCategory.FILE_IO, context={"critical_file": False})
            == ErrorSeverity.MEDIUM
        )

    def test_network_is_medium(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.NETWORK) == ErrorSeverity.MEDIUM

    def test_timeout_is_medium(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.TIMEOUT) == ErrorSeverity.MEDIUM

    def test_orchestrator_is_medium(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.ORCHESTRATOR) == ErrorSeverity.MEDIUM

    def test_evaluation_is_medium(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.EVALUATION) == ErrorSeverity.MEDIUM

    def test_data_processing_is_medium(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.DATA_PROCESSING) == ErrorSeverity.MEDIUM

    def test_unknown_category_is_low(self):
        assert self.handler.determine_severity(Exception("x"), ErrorCategory.UNKNOWN) == ErrorSeverity.LOW

    def test_none_context_handled(self):
        # context=None should not blow up
        sev = self.handler.determine_severity(Exception("x"), ErrorCategory.FILE_IO, context=None)
        assert sev == ErrorSeverity.MEDIUM


# ---------------------------------------------------------------------------
# ExceptionHandler – handle_exception
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestHandleException:
    """Test ExceptionHandler.handle_exception."""

    @pytest.fixture(autouse=True)
    def _handler(self):
        self.logger = MagicMock(spec=logging.Logger)
        self.logger.isEnabledFor.return_value = False
        self.handler = ExceptionHandler(logger=self.logger)

    def test_returns_red_team_error(self):
        result = self.handler.handle_exception(ValueError("bad"))
        assert isinstance(result, RedTeamError)

    def test_message_contains_category_and_original(self):
        result = self.handler.handle_exception(RuntimeError("oops"))
        assert "oops" in result.message

    def test_message_includes_task_name(self):
        result = self.handler.handle_exception(RuntimeError("x"), task_name="scan_step")
        assert "scan_step" in result.message

    def test_category_title_in_message(self):
        result = self.handler.handle_exception(ConnectionError("fail"))
        assert "Network" in result.message

    def test_error_counts_incremented(self):
        self.handler.handle_exception(ConnectionError("a"))
        self.handler.handle_exception(ConnectionError("b"))
        assert self.handler.error_counts[ErrorCategory.NETWORK] == 2

    def test_context_propagated(self):
        ctx = {"file": "test.json"}
        result = self.handler.handle_exception(RuntimeError("x"), context=ctx)
        assert result.context is ctx

    def test_original_exception_stored(self):
        orig = ValueError("orig")
        result = self.handler.handle_exception(orig)
        assert result.original_exception is orig

    def test_reraise_raises(self):
        with pytest.raises(RedTeamError) as exc_info:
            self.handler.handle_exception(RuntimeError("x"), reraise=True)
        assert "x" in str(exc_info.value)

    def test_already_red_team_error_passthrough(self):
        original = RedTeamError("existing", category=ErrorCategory.EVALUATION, severity=ErrorSeverity.HIGH)
        result = self.handler.handle_exception(original)
        assert result is original

    def test_already_red_team_error_reraise(self):
        original = RedTeamError("existing")
        with pytest.raises(RedTeamError) as exc_info:
            self.handler.handle_exception(original, reraise=True)
        assert exc_info.value is original

    def test_logging_called(self):
        self.handler.handle_exception(RuntimeError("log me"), task_name="task1")
        self.logger.log.assert_called()

    def test_log_level_fatal(self):
        self.handler.handle_exception(MemoryError("oom"))
        self.logger.log.assert_called()
        call_args = self.logger.log.call_args
        assert call_args[0][0] == logging.CRITICAL

    def test_log_level_high(self):
        # auth error → HIGH → logging.ERROR
        exc = Exception("auth problem")
        exc.response = MagicMock(status_code=401)
        self.handler.handle_exception(exc)
        call_args = self.logger.log.call_args
        assert call_args[0][0] == logging.ERROR

    def test_log_level_medium(self):
        self.handler.handle_exception(ConnectionError("net"))
        call_args = self.logger.log.call_args
        assert call_args[0][0] == logging.WARNING

    def test_log_level_low(self):
        # unknown category → LOW → logging.INFO
        self.handler.handle_exception(RuntimeError("whatever"))
        call_args = self.logger.log.call_args
        assert call_args[0][0] == logging.INFO

    def test_log_includes_task_name_bracket(self):
        self.handler.handle_exception(RuntimeError("x"), task_name="mytask")
        log_msg = self.logger.log.call_args[0][1]
        assert "[mytask]" in log_msg

    def test_log_includes_category_and_severity(self):
        self.handler.handle_exception(ConnectionError("net"))
        log_msg = self.logger.log.call_args[0][1]
        assert "[network]" in log_msg
        assert "[medium]" in log_msg

    def test_context_logged_as_debug(self):
        self.handler.handle_exception(RuntimeError("x"), context={"k": "v"})
        self.logger.debug.assert_called()
        debug_msg = self.logger.debug.call_args[0][0]
        assert "k" in debug_msg

    def test_original_traceback_logged_when_debug_enabled(self):
        self.logger.isEnabledFor.return_value = True
        self.handler.handle_exception(RuntimeError("x"))
        # debug called at least twice: context (empty dict not logged) + traceback
        debug_calls = [str(c) for c in self.logger.debug.call_args_list]
        assert any("traceback" in c.lower() for c in debug_calls)

    def test_no_context_no_debug_context_log(self):
        """When context is empty, the debug 'Error context' line should not fire."""
        mock_logger = MagicMock(spec=logging.Logger)
        mock_logger.isEnabledFor.return_value = False
        handler = ExceptionHandler(logger=mock_logger)
        handler.handle_exception(RuntimeError("x"), context={})
        # debug should not have been called (empty context + debug not enabled)
        mock_logger.debug.assert_not_called()


# ---------------------------------------------------------------------------
# ExceptionHandler – should_abort_scan
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestShouldAbortScan:
    """Test ExceptionHandler.should_abort_scan."""

    @pytest.fixture(autouse=True)
    def _handler(self):
        self.handler = ExceptionHandler(logger=logging.getLogger("test"))

    def test_no_errors_does_not_abort(self):
        assert self.handler.should_abort_scan() is False

    def test_few_auth_errors_does_not_abort(self):
        self.handler.error_counts[ErrorCategory.AUTHENTICATION] = 2
        assert self.handler.should_abort_scan() is False

    def test_many_auth_errors_aborts(self):
        self.handler.error_counts[ErrorCategory.AUTHENTICATION] = 3
        assert self.handler.should_abort_scan() is True

    def test_many_config_errors_aborts(self):
        self.handler.error_counts[ErrorCategory.CONFIGURATION] = 3
        assert self.handler.should_abort_scan() is True

    def test_combined_auth_config_aborts(self):
        self.handler.error_counts[ErrorCategory.AUTHENTICATION] = 2
        self.handler.error_counts[ErrorCategory.CONFIGURATION] = 1
        assert self.handler.should_abort_scan() is True

    def test_many_network_errors_aborts(self):
        self.handler.error_counts[ErrorCategory.NETWORK] = 11
        assert self.handler.should_abort_scan() is True

    def test_ten_network_errors_does_not_abort(self):
        self.handler.error_counts[ErrorCategory.NETWORK] = 10
        assert self.handler.should_abort_scan() is False

    def test_other_categories_do_not_trigger_abort(self):
        self.handler.error_counts[ErrorCategory.EVALUATION] = 100
        self.handler.error_counts[ErrorCategory.DATA_PROCESSING] = 100
        assert self.handler.should_abort_scan() is False


# ---------------------------------------------------------------------------
# ExceptionHandler – get_error_summary
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetErrorSummary:
    """Test ExceptionHandler.get_error_summary."""

    @pytest.fixture(autouse=True)
    def _handler(self):
        self.handler = ExceptionHandler(logger=logging.getLogger("test"))

    def test_empty_summary(self):
        summary = self.handler.get_error_summary()
        assert summary["total_errors"] == 0
        assert summary["most_common_category"] is None
        assert summary["should_abort"] is False

    def test_summary_with_errors(self):
        self.handler.error_counts[ErrorCategory.NETWORK] = 5
        self.handler.error_counts[ErrorCategory.TIMEOUT] = 2
        summary = self.handler.get_error_summary()

        assert summary["total_errors"] == 7
        assert summary["most_common_category"] == ErrorCategory.NETWORK

    def test_summary_includes_all_category_keys(self):
        summary = self.handler.get_error_summary()
        counts = summary["error_counts_by_category"]
        for cat in ErrorCategory:
            assert cat in counts

    def test_should_abort_reflected(self):
        self.handler.error_counts[ErrorCategory.AUTHENTICATION] = 5
        summary = self.handler.get_error_summary()
        assert summary["should_abort"] is True


# ---------------------------------------------------------------------------
# ExceptionHandler – log_error_summary
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestLogErrorSummary:
    """Test ExceptionHandler.log_error_summary."""

    def test_no_errors_logs_clean_message(self):
        logger = MagicMock(spec=logging.Logger)
        handler = ExceptionHandler(logger=logger)
        handler.log_error_summary()
        logger.info.assert_called_once_with("No errors encountered during operation")

    def test_with_errors_logs_total_and_categories(self):
        logger = MagicMock(spec=logging.Logger)
        handler = ExceptionHandler(logger=logger)
        handler.error_counts[ErrorCategory.NETWORK] = 3
        handler.error_counts[ErrorCategory.TIMEOUT] = 1

        handler.log_error_summary()

        info_calls = [str(c) for c in logger.info.call_args_list]
        # Total errors line
        assert any("4 total errors" in c for c in info_calls)
        # Per-category lines
        assert any("3" in c and "network" in c.lower() for c in info_calls)
        assert any("1" in c and "timeout" in c.lower() for c in info_calls)
        # Most common line
        assert any("Most common" in c for c in info_calls)

    def test_zero_count_categories_not_logged(self):
        logger = MagicMock(spec=logging.Logger)
        handler = ExceptionHandler(logger=logger)
        handler.error_counts[ErrorCategory.NETWORK] = 1

        handler.log_error_summary()

        info_msgs = [str(c) for c in logger.info.call_args_list]
        # Categories with 0 count should not appear as "  category: 0"
        assert not any("evaluation" in m.lower() and "0" in m for m in info_msgs)


# ---------------------------------------------------------------------------
# create_exception_handler factory
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestCreateExceptionHandler:
    """Test create_exception_handler factory function."""

    def test_returns_exception_handler(self):
        handler = create_exception_handler()
        assert isinstance(handler, ExceptionHandler)

    def test_custom_logger(self):
        logger = logging.getLogger("custom")
        handler = create_exception_handler(logger=logger)
        assert handler.logger is logger

    def test_default_logger_when_none(self):
        handler = create_exception_handler(logger=None)
        assert handler.logger is not None


# ---------------------------------------------------------------------------
# exception_context context manager
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestExceptionContext:
    """Test exception_context context manager."""

    @pytest.fixture(autouse=True)
    def _handler(self):
        self.logger = MagicMock(spec=logging.Logger)
        self.logger.isEnabledFor.return_value = False
        self.handler = ExceptionHandler(logger=self.logger)

    def test_enter_returns_self(self):
        ctx = exception_context(self.handler, "task")
        result = ctx.__enter__()
        assert result is ctx

    def test_no_exception_sets_no_error(self):
        with exception_context(self.handler, "task") as ctx:
            pass  # no error
        assert ctx.error is None

    def test_exit_returns_false_on_no_exception(self):
        ctx = exception_context(self.handler, "task")
        ctx.__enter__()
        result = ctx.__exit__(None, None, None)
        assert result is False

    def test_low_severity_exception_suppressed(self):
        """Low-severity exceptions should be suppressed (not reraised)."""
        with exception_context(self.handler, "task") as ctx:
            raise RuntimeError("minor issue")  # UNKNOWN → LOW severity
        assert ctx.error is not None
        assert ctx.error.severity == ErrorSeverity.LOW

    def test_medium_severity_exception_suppressed(self):
        with exception_context(self.handler, "task") as ctx:
            raise ConnectionError("network blip")  # NETWORK → MEDIUM
        assert ctx.error is not None
        assert ctx.error.severity == ErrorSeverity.MEDIUM

    def test_high_severity_exception_suppressed(self):
        """HIGH severity is suppressed because it's not FATAL."""
        exc = Exception("auth fail")
        exc.response = MagicMock(status_code=401)

        with exception_context(self.handler, "task") as ctx:
            raise exc
        assert ctx.error is not None
        assert ctx.error.severity == ErrorSeverity.HIGH

    def test_fatal_exception_reraised_by_default(self):
        with pytest.raises(RedTeamError) as exc_info:
            with exception_context(self.handler, "task") as ctx:
                raise MemoryError("oom")
        assert exc_info.value.severity == ErrorSeverity.FATAL

    def test_fatal_exception_suppressed_when_reraise_disabled(self):
        with exception_context(self.handler, "task", reraise_fatal=False) as ctx:
            raise MemoryError("oom")
        assert ctx.error is not None
        assert ctx.error.severity == ErrorSeverity.FATAL

    def test_context_dict_passed_through(self):
        my_ctx = {"step": 42}
        with exception_context(self.handler, "task", context=my_ctx) as ctx:
            raise RuntimeError("x")
        assert ctx.error.context is my_ctx

    def test_error_counts_updated(self):
        with exception_context(self.handler, "task"):
            raise ConnectionError("net")
        assert self.handler.error_counts[ErrorCategory.NETWORK] == 1

    def test_task_name_in_error_message(self):
        with exception_context(self.handler, "my_scan") as ctx:
            raise RuntimeError("fail")
        assert "my_scan" in ctx.error.message


# ---------------------------------------------------------------------------
# ExceptionHandler – init defaults
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestExceptionHandlerInit:
    """Test ExceptionHandler initialization."""

    def test_default_logger(self):
        handler = ExceptionHandler()
        assert handler.logger is not None
        assert isinstance(handler.logger, logging.Logger)

    def test_error_counts_initialized_to_zero(self):
        handler = ExceptionHandler()
        for cat in ErrorCategory:
            assert handler.error_counts[cat] == 0

    def test_custom_logger_used(self):
        logger = logging.getLogger("my_logger")
        handler = ExceptionHandler(logger=logger)
        assert handler.logger is logger
