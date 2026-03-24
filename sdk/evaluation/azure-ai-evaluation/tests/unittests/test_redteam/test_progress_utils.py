"""
Unit tests for red_team._utils.progress_utils module.
"""

import asyncio
import time
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from azure.ai.evaluation.red_team._utils.progress_utils import (
    ProgressManager,
    create_progress_manager,
)
from azure.ai.evaluation.red_team._utils.constants import TASK_STATUS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def mock_logger():
    """Create a mock logger with standard log-level methods."""
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger


@pytest.fixture(scope="function")
def progress_manager():
    """Create a basic ProgressManager with progress bar disabled."""
    return ProgressManager(total_tasks=5, show_progress_bar=False)


@pytest.fixture(scope="function")
def progress_manager_with_logger(mock_logger):
    """Create a ProgressManager with a mock logger and progress bar disabled."""
    return ProgressManager(total_tasks=5, logger=mock_logger, show_progress_bar=False)


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestProgressManagerInit:
    """Test ProgressManager.__init__."""

    def test_default_init(self):
        """Test initialization with default parameters."""
        pm = ProgressManager()

        assert pm.total_tasks == 0
        assert pm.completed_tasks == 0
        assert pm.failed_tasks == 0
        assert pm.timeout_tasks == 0
        assert pm.logger is None
        assert pm.show_progress_bar is True
        assert pm.progress_desc == "Processing"
        assert pm.task_statuses == {}
        assert pm.start_time is None
        assert pm.end_time is None
        assert pm.progress_bar is None

    def test_custom_init(self, mock_logger):
        """Test initialization with custom parameters."""
        pm = ProgressManager(
            total_tasks=10,
            logger=mock_logger,
            show_progress_bar=False,
            progress_desc="Red Team Scan",
        )

        assert pm.total_tasks == 10
        assert pm.logger is mock_logger
        assert pm.show_progress_bar is False
        assert pm.progress_desc == "Red Team Scan"

    def test_zero_total_tasks(self):
        """Test initialization with zero total tasks."""
        pm = ProgressManager(total_tasks=0)

        assert pm.total_tasks == 0


# ---------------------------------------------------------------------------
# start / stop
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestProgressManagerStartStop:
    """Test ProgressManager.start and .stop methods."""

    def test_start_sets_start_time(self, progress_manager):
        """Test that start() records the start time."""
        assert progress_manager.start_time is None
        progress_manager.start()

        assert progress_manager.start_time is not None
        assert isinstance(progress_manager.start_time, float)

    @patch("azure.ai.evaluation.red_team._utils.progress_utils.tqdm")
    def test_start_creates_progress_bar(self, mock_tqdm_cls):
        """Test that start() creates a tqdm progress bar when enabled."""
        mock_bar = MagicMock()
        mock_tqdm_cls.return_value = mock_bar

        pm = ProgressManager(total_tasks=3, show_progress_bar=True, progress_desc="Testing")
        pm.start()

        mock_tqdm_cls.assert_called_once()
        call_kwargs = mock_tqdm_cls.call_args
        assert call_kwargs.kwargs["total"] == 3
        assert "Testing" in call_kwargs.kwargs["desc"]
        mock_bar.set_postfix.assert_called_once_with({"current": "initializing"})

    def test_start_no_progress_bar_when_disabled(self, progress_manager):
        """Test that start() does not create a progress bar when disabled."""
        progress_manager.start()

        assert progress_manager.progress_bar is None

    @patch("azure.ai.evaluation.red_team._utils.progress_utils.tqdm")
    def test_start_no_progress_bar_when_zero_tasks(self, mock_tqdm_cls):
        """Test that start() does not create a progress bar when total_tasks is 0."""
        pm = ProgressManager(total_tasks=0, show_progress_bar=True)
        pm.start()

        mock_tqdm_cls.assert_not_called()
        assert pm.progress_bar is None

    def test_stop_sets_end_time(self, progress_manager):
        """Test that stop() records the end time."""
        progress_manager.start()
        progress_manager.stop()

        assert progress_manager.end_time is not None
        assert progress_manager.end_time >= progress_manager.start_time

    def test_stop_closes_progress_bar(self):
        """Test that stop() closes and clears the progress bar."""
        pm = ProgressManager(total_tasks=5, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar

        pm.stop()

        mock_bar.close.assert_called_once()
        assert pm.progress_bar is None

    def test_stop_without_progress_bar(self, progress_manager):
        """Test that stop() works cleanly when no progress bar exists."""
        progress_manager.start()
        progress_manager.stop()
        # Should not raise


# ---------------------------------------------------------------------------
# update_task_status (async)
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestUpdateTaskStatus:
    """Test ProgressManager.update_task_status."""

    @pytest.mark.asyncio
    async def test_update_to_completed(self, progress_manager):
        """Test transitioning a task to COMPLETED increments completed_tasks."""
        progress_manager.task_statuses["task-1"] = TASK_STATUS["PENDING"]

        await progress_manager.update_task_status("task-1", TASK_STATUS["COMPLETED"])

        assert progress_manager.completed_tasks == 1
        assert progress_manager.task_statuses["task-1"] == TASK_STATUS["COMPLETED"]

    @pytest.mark.asyncio
    async def test_update_to_failed(self, progress_manager):
        """Test transitioning a task to FAILED increments failed_tasks."""
        progress_manager.task_statuses["task-1"] = TASK_STATUS["PENDING"]

        await progress_manager.update_task_status("task-1", TASK_STATUS["FAILED"])

        assert progress_manager.failed_tasks == 1
        assert progress_manager.task_statuses["task-1"] == TASK_STATUS["FAILED"]

    @pytest.mark.asyncio
    async def test_update_to_timeout(self, progress_manager):
        """Test transitioning a task to TIMEOUT increments timeout_tasks."""
        progress_manager.task_statuses["task-1"] = TASK_STATUS["PENDING"]

        await progress_manager.update_task_status("task-1", TASK_STATUS["TIMEOUT"])

        assert progress_manager.timeout_tasks == 1
        assert progress_manager.task_statuses["task-1"] == TASK_STATUS["TIMEOUT"]

    @pytest.mark.asyncio
    async def test_same_status_does_not_increment(self, progress_manager):
        """Test that setting the same status twice does not double-count."""
        progress_manager.task_statuses["task-1"] = TASK_STATUS["COMPLETED"]
        progress_manager.completed_tasks = 1

        await progress_manager.update_task_status("task-1", TASK_STATUS["COMPLETED"])

        assert progress_manager.completed_tasks == 1  # unchanged

    @pytest.mark.asyncio
    async def test_new_task_key_created(self, progress_manager):
        """Test that a brand-new task key is created in task_statuses."""
        await progress_manager.update_task_status("new-task", TASK_STATUS["RUNNING"])

        assert progress_manager.task_statuses["new-task"] == TASK_STATUS["RUNNING"]

    @pytest.mark.asyncio
    async def test_status_change_logged_with_details(self, progress_manager_with_logger, mock_logger):
        """Test that status changes with details are logged."""
        await progress_manager_with_logger.update_task_status("task-1", TASK_STATUS["COMPLETED"], details="All done")

        mock_logger.debug.assert_called_once()
        log_msg = mock_logger.debug.call_args[0][0]
        assert "task-1" in log_msg
        assert "All done" in log_msg

    @pytest.mark.asyncio
    async def test_no_log_without_details(self, progress_manager_with_logger, mock_logger):
        """Test that status changes without details are NOT logged."""
        await progress_manager_with_logger.update_task_status("task-1", TASK_STATUS["COMPLETED"])

        mock_logger.debug.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_log_without_logger(self, progress_manager):
        """Test that status change with details does not crash without a logger."""
        await progress_manager.update_task_status("task-1", TASK_STATUS["COMPLETED"], details="info")
        # Should not raise

    @pytest.mark.asyncio
    async def test_multiple_tasks_tracked(self, progress_manager):
        """Test tracking multiple independent tasks."""
        await progress_manager.update_task_status("t1", TASK_STATUS["COMPLETED"])
        await progress_manager.update_task_status("t2", TASK_STATUS["FAILED"])
        await progress_manager.update_task_status("t3", TASK_STATUS["TIMEOUT"])
        await progress_manager.update_task_status("t4", TASK_STATUS["COMPLETED"])

        assert progress_manager.completed_tasks == 2
        assert progress_manager.failed_tasks == 1
        assert progress_manager.timeout_tasks == 1


# ---------------------------------------------------------------------------
# _update_progress_bar (async)
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestUpdateProgressBar:
    """Test ProgressManager._update_progress_bar."""

    @pytest.mark.asyncio
    async def test_no_op_without_bar(self, progress_manager):
        """Test that _update_progress_bar is a no-op when no bar exists."""
        await progress_manager._update_progress_bar()
        # Should not raise

    @pytest.mark.asyncio
    async def test_bar_update_called(self):
        """Test that progress bar's update(1) is called."""
        pm = ProgressManager(total_tasks=5, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar
        pm.start_time = time.time() - 10
        pm.completed_tasks = 2
        pm.total_tasks = 5

        await pm._update_progress_bar()

        mock_bar.update.assert_called_once_with(1)
        mock_bar.set_postfix.assert_called_once()

    @pytest.mark.asyncio
    async def test_postfix_contains_eta(self):
        """Test that postfix includes eta when remaining tasks exist."""
        pm = ProgressManager(total_tasks=10, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar
        pm.start_time = time.time() - 20
        pm.completed_tasks = 5  # 5 done, 5 remaining

        await pm._update_progress_bar()

        postfix = mock_bar.set_postfix.call_args[0][0]
        assert "completed" in postfix
        assert "failed" in postfix
        assert "timeout" in postfix
        assert "eta" in postfix

    @pytest.mark.asyncio
    async def test_postfix_no_eta_when_all_done(self):
        """Test that postfix omits eta when no remaining tasks."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar
        pm.start_time = time.time() - 10
        pm.completed_tasks = 3  # all done

        await pm._update_progress_bar()

        postfix = mock_bar.set_postfix.call_args[0][0]
        assert "eta" not in postfix

    @pytest.mark.asyncio
    async def test_zero_completed_no_set_postfix(self):
        """Test that set_postfix is not called when completed_tasks == 0."""
        pm = ProgressManager(total_tasks=5, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar
        pm.start_time = time.time()
        pm.completed_tasks = 0

        await pm._update_progress_bar()

        mock_bar.update.assert_called_once_with(1)
        mock_bar.set_postfix.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_start_time_no_set_postfix(self):
        """Test that set_postfix is not called when start_time is None."""
        pm = ProgressManager(total_tasks=5, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar
        pm.start_time = None
        pm.completed_tasks = 2

        await pm._update_progress_bar()

        mock_bar.update.assert_called_once_with(1)
        mock_bar.set_postfix.assert_not_called()

    @pytest.mark.asyncio
    async def test_zero_total_tasks_completion_pct(self):
        """Test completion_pct is 0 when total_tasks is 0 (avoids division by zero)."""
        pm = ProgressManager(total_tasks=0, show_progress_bar=False)
        mock_bar = MagicMock()
        pm.progress_bar = mock_bar
        pm.start_time = time.time()
        pm.completed_tasks = 0

        # Should not raise ZeroDivisionError
        await pm._update_progress_bar()
        mock_bar.update.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# write_progress_message
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestWriteProgressMessage:
    """Test ProgressManager.write_progress_message."""

    @patch("azure.ai.evaluation.red_team._utils.progress_utils.tqdm")
    def test_uses_tqdm_write_when_bar_exists(self, mock_tqdm_module):
        """Test that tqdm.write is used when a progress bar is active."""
        pm = ProgressManager(show_progress_bar=False)
        pm.progress_bar = MagicMock()  # pretend bar is active

        pm.write_progress_message("hello")

        mock_tqdm_module.write.assert_called_once_with("hello")

    @patch("builtins.print")
    def test_uses_print_when_no_bar(self, mock_print):
        """Test that print() is used when no progress bar exists."""
        pm = ProgressManager(show_progress_bar=False)

        pm.write_progress_message("hello")

        mock_print.assert_called_once_with("hello")


# ---------------------------------------------------------------------------
# log_task_completion
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestLogTaskCompletion:
    """Test ProgressManager.log_task_completion."""

    @patch("builtins.print")
    def test_success_message(self, mock_print, progress_manager):
        """Test success completion message format."""
        progress_manager.log_task_completion("scan", 12.345, success=True)

        msg = mock_print.call_args[0][0]
        assert "✅" in msg
        assert "scan" in msg
        assert "12.3s" in msg

    @patch("builtins.print")
    def test_failure_message(self, mock_print, progress_manager):
        """Test failure completion message format."""
        progress_manager.log_task_completion("scan", 5.0, success=False)

        msg = mock_print.call_args[0][0]
        assert "❌" in msg

    @patch("builtins.print")
    def test_details_appended(self, mock_print, progress_manager):
        """Test that optional details are appended to the message."""
        progress_manager.log_task_completion("scan", 1.0, details="3 findings")

        msg = mock_print.call_args[0][0]
        assert "3 findings" in msg

    def test_logger_info_on_success(self, progress_manager_with_logger, mock_logger):
        """Test that logger.info is called on success."""
        with patch("builtins.print"):
            progress_manager_with_logger.log_task_completion("scan", 1.0, success=True)

        mock_logger.info.assert_called_once()

    def test_logger_warning_on_failure(self, progress_manager_with_logger, mock_logger):
        """Test that logger.warning is called on failure."""
        with patch("builtins.print"):
            progress_manager_with_logger.log_task_completion("scan", 1.0, success=False)

        mock_logger.warning.assert_called_once()


# ---------------------------------------------------------------------------
# log_task_timeout
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestLogTaskTimeout:
    """Test ProgressManager.log_task_timeout."""

    @patch("builtins.print")
    def test_timeout_message(self, mock_print, progress_manager):
        """Test timeout message format."""
        progress_manager.log_task_timeout("scan", 120.0)

        msg = mock_print.call_args[0][0]
        assert "TIMEOUT" in msg
        assert "scan" in msg
        assert "120" in msg

    def test_logger_warning_on_timeout(self, progress_manager_with_logger, mock_logger):
        """Test that logger.warning is called on timeout."""
        with patch("builtins.print"):
            progress_manager_with_logger.log_task_timeout("scan", 60.0)

        mock_logger.warning.assert_called_once()

    @patch("builtins.print")
    def test_no_logger_does_not_crash(self, mock_print, progress_manager):
        """Test that log_task_timeout works without a logger."""
        progress_manager.log_task_timeout("scan", 30.0)
        # Should not raise


# ---------------------------------------------------------------------------
# log_task_error
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestLogTaskError:
    """Test ProgressManager.log_task_error."""

    @patch("builtins.print")
    def test_error_message(self, mock_print, progress_manager):
        """Test error message format includes class name and message."""
        err = ValueError("bad input")
        progress_manager.log_task_error("scan", err)

        msg = mock_print.call_args[0][0]
        assert "ERROR" in msg
        assert "scan" in msg
        assert "ValueError" in msg
        assert "bad input" in msg

    def test_logger_error_on_error(self, progress_manager_with_logger, mock_logger):
        """Test that logger.error is called on task error."""
        with patch("builtins.print"):
            progress_manager_with_logger.log_task_error("scan", RuntimeError("fail"))

        mock_logger.error.assert_called_once()

    @patch("builtins.print")
    def test_no_logger_does_not_crash(self, mock_print, progress_manager):
        """Test that log_task_error works without a logger."""
        progress_manager.log_task_error("scan", Exception("oops"))
        # Should not raise


# ---------------------------------------------------------------------------
# get_summary
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestGetSummary:
    """Test ProgressManager.get_summary."""

    def test_summary_before_start(self, progress_manager):
        """Test summary when tracking has not started."""
        summary = progress_manager.get_summary()

        assert summary["total_tasks"] == 5
        assert summary["completed_tasks"] == 0
        assert summary["failed_tasks"] == 0
        assert summary["timeout_tasks"] == 0
        assert summary["success_rate"] == 0
        assert summary["total_time_seconds"] is None
        assert summary["average_time_per_task"] is None
        assert summary["task_statuses"] == {}

    def test_summary_after_start_and_stop(self, progress_manager):
        """Test summary after full lifecycle."""
        progress_manager.start()
        # Force a non-zero elapsed time so total_time is truthy
        progress_manager.start_time = progress_manager.start_time - 10.0
        progress_manager.completed_tasks = 3
        progress_manager.failed_tasks = 1
        progress_manager.timeout_tasks = 1
        progress_manager.task_statuses = {"t1": "completed", "t2": "failed"}
        progress_manager.stop()

        summary = progress_manager.get_summary()

        assert summary["total_tasks"] == 5
        assert summary["completed_tasks"] == 3
        assert summary["failed_tasks"] == 1
        assert summary["timeout_tasks"] == 1
        assert summary["success_rate"] == 60.0
        assert summary["total_time_seconds"] is not None
        assert summary["total_time_seconds"] >= 10.0
        assert summary["average_time_per_task"] is not None
        assert summary["average_time_per_task"] > 0
        # task_statuses should be a copy
        assert summary["task_statuses"] == {"t1": "completed", "t2": "failed"}
        summary["task_statuses"]["t3"] = "new"
        assert "t3" not in progress_manager.task_statuses

    def test_summary_zero_total_tasks(self):
        """Test success_rate is 0 when total_tasks is 0."""
        pm = ProgressManager(total_tasks=0)
        summary = pm.get_summary()

        assert summary["success_rate"] == 0

    def test_summary_all_successes(self):
        """Test summary when all tasks succeed."""
        pm = ProgressManager(total_tasks=4, show_progress_bar=False)
        pm.start()
        pm.completed_tasks = 4
        pm.stop()

        summary = pm.get_summary()
        assert summary["success_rate"] == 100.0

    def test_summary_all_failures(self):
        """Test summary when all tasks fail."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)
        pm.start()
        pm.failed_tasks = 3
        pm.stop()

        summary = pm.get_summary()
        assert summary["success_rate"] == 0
        assert summary["average_time_per_task"] is None  # no completed tasks

    def test_summary_uses_current_time_before_stop(self):
        """Test that summary uses time.time() if stop() has not been called."""
        pm = ProgressManager(total_tasks=1, show_progress_bar=False)
        pm.start()
        pm.completed_tasks = 1

        summary = pm.get_summary()
        assert summary["total_time_seconds"] is not None
        assert summary["total_time_seconds"] >= 0


# ---------------------------------------------------------------------------
# print_summary
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestPrintSummary:
    """Test ProgressManager.print_summary."""

    @patch("builtins.print")
    def test_prints_formatted_summary(self, mock_print, progress_manager):
        """Test that print_summary outputs a complete formatted summary."""
        progress_manager.start()
        # Force a non-zero elapsed time so total_time is truthy
        progress_manager.start_time = progress_manager.start_time - 10.0
        progress_manager.completed_tasks = 3
        progress_manager.failed_tasks = 1
        progress_manager.timeout_tasks = 1
        progress_manager.stop()

        progress_manager.print_summary()

        all_output = " ".join(call[0][0] for call in mock_print.call_args_list)
        assert "EXECUTION SUMMARY" in all_output
        assert "Total Tasks: 5" in all_output
        assert "Completed: 3" in all_output
        assert "Failed: 1" in all_output
        assert "Timeouts: 1" in all_output
        assert "Success Rate: 60.0%" in all_output
        assert "Total Time:" in all_output
        assert "Avg Time/Task:" in all_output

    @patch("builtins.print")
    def test_summary_no_time_info_before_start(self, mock_print):
        """Test that time-related lines are omitted when not started."""
        pm = ProgressManager(total_tasks=2, show_progress_bar=False)
        pm.print_summary()

        all_output = " ".join(call[0][0] for call in mock_print.call_args_list)
        assert "Total Time:" not in all_output

    @patch("builtins.print")
    def test_summary_no_avg_time_with_zero_completed(self, mock_print):
        """Test that Avg Time/Task is omitted when no tasks completed."""
        pm = ProgressManager(total_tasks=2, show_progress_bar=False)
        pm.start()
        pm.stop()
        pm.print_summary()

        all_output = " ".join(call[0][0] for call in mock_print.call_args_list)
        assert "Avg Time/Task:" not in all_output


# ---------------------------------------------------------------------------
# Context manager (__enter__ / __exit__)
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestContextManager:
    """Test ProgressManager context manager protocol."""

    def test_enter_starts_tracking(self):
        """Test that __enter__ calls start() and returns self."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)

        with pm as mgr:
            assert mgr is pm
            assert pm.start_time is not None

    def test_exit_stops_tracking(self):
        """Test that __exit__ calls stop()."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)

        with pm:
            pass

        assert pm.end_time is not None

    def test_exit_on_exception(self):
        """Test that __exit__ runs even on exception."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)

        with pytest.raises(ValueError):
            with pm:
                raise ValueError("boom")

        assert pm.end_time is not None

    def test_context_manager_closes_bar(self):
        """Test that the progress bar is closed by __exit__."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)
        mock_bar = MagicMock()

        with pm:
            pm.progress_bar = mock_bar

        mock_bar.close.assert_called_once()
        assert pm.progress_bar is None


# ---------------------------------------------------------------------------
# create_progress_manager factory
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestCreateProgressManager:
    """Test create_progress_manager factory function."""

    def test_returns_progress_manager(self):
        """Test that factory returns a ProgressManager instance."""
        pm = create_progress_manager()

        assert isinstance(pm, ProgressManager)

    def test_passes_all_params(self, mock_logger):
        """Test that factory forwards all parameters."""
        pm = create_progress_manager(
            total_tasks=7,
            logger=mock_logger,
            show_progress_bar=False,
            progress_desc="Red Team",
        )

        assert pm.total_tasks == 7
        assert pm.logger is mock_logger
        assert pm.show_progress_bar is False
        assert pm.progress_desc == "Red Team"

    def test_defaults(self):
        """Test factory defaults match ProgressManager defaults."""
        pm = create_progress_manager()

        assert pm.total_tasks == 0
        assert pm.logger is None
        assert pm.show_progress_bar is True
        assert pm.progress_desc == "Processing"


# ---------------------------------------------------------------------------
# Integration-style async tests
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestProgressManagerIntegration:
    """Integration-style tests exercising multiple methods together."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test complete lifecycle: start → update tasks → stop → summary."""
        pm = ProgressManager(total_tasks=3, show_progress_bar=False)
        pm.start()

        await pm.update_task_status("t1", TASK_STATUS["COMPLETED"])
        await pm.update_task_status("t2", TASK_STATUS["FAILED"])
        await pm.update_task_status("t3", TASK_STATUS["COMPLETED"])

        pm.stop()
        summary = pm.get_summary()

        assert summary["completed_tasks"] == 2
        assert summary["failed_tasks"] == 1
        assert summary["timeout_tasks"] == 0
        assert summary["success_rate"] == pytest.approx(66.666, rel=0.01)
        assert summary["total_time_seconds"] is not None

    @pytest.mark.asyncio
    async def test_pending_to_running_to_completed(self):
        """Test a realistic status progression for a single task."""
        pm = ProgressManager(total_tasks=1, show_progress_bar=False)

        await pm.update_task_status("t1", TASK_STATUS["PENDING"])
        assert pm.completed_tasks == 0

        await pm.update_task_status("t1", TASK_STATUS["RUNNING"])
        assert pm.completed_tasks == 0

        await pm.update_task_status("t1", TASK_STATUS["COMPLETED"])
        assert pm.completed_tasks == 1

    @pytest.mark.asyncio
    async def test_context_manager_with_async_updates(self):
        """Test context manager combined with async status updates."""
        with ProgressManager(total_tasks=2, show_progress_bar=False) as pm:
            await pm.update_task_status("t1", TASK_STATUS["COMPLETED"])
            await pm.update_task_status("t2", TASK_STATUS["TIMEOUT"])

        assert pm.completed_tasks == 1
        assert pm.timeout_tasks == 1
        assert pm.end_time is not None
