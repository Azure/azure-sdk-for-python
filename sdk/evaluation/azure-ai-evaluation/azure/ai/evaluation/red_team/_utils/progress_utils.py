# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Progress and status management utilities for Red Team Agent.

This module provides centralized progress tracking, task status management,
and user feedback utilities for red team operations.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Optional, Any
from tqdm import tqdm

from .constants import TASK_STATUS


class ProgressManager:
    """Centralized progress and status tracking for Red Team operations."""

    def __init__(
        self, total_tasks: int = 0, logger=None, show_progress_bar: bool = True, progress_desc: str = "Processing"
    ):
        """Initialize progress manager.

        :param total_tasks: Total number of tasks to track
        :param logger: Logger instance for progress messages
        :param show_progress_bar: Whether to show a progress bar
        :param progress_desc: Description for the progress bar
        """
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.timeout_tasks = 0
        self.logger = logger
        self.show_progress_bar = show_progress_bar
        self.progress_desc = progress_desc

        # Task status tracking
        self.task_statuses: Dict[str, str] = {}

        # Timing
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Progress bar
        self.progress_bar: Optional[tqdm] = None
        self.progress_lock = asyncio.Lock()

    def start(self) -> None:
        """Start progress tracking."""
        self.start_time = time.time()

        if self.show_progress_bar and self.total_tasks > 0:
            self.progress_bar = tqdm(
                total=self.total_tasks,
                desc=f"{self.progress_desc}: ",
                ncols=100,
                unit="task",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
            )
            self.progress_bar.set_postfix({"current": "initializing"})

    def stop(self) -> None:
        """Stop progress tracking and cleanup."""
        self.end_time = time.time()

        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None

    async def update_task_status(self, task_key: str, status: str, details: Optional[str] = None) -> None:
        """Update the status of a specific task.

        :param task_key: Unique identifier for the task
        :param status: New status for the task
        :param details: Optional details about the status change
        """
        old_status = self.task_statuses.get(task_key)
        self.task_statuses[task_key] = status

        # Update counters based on status change
        if old_status != status:
            if status == TASK_STATUS["COMPLETED"]:
                self.completed_tasks += 1
                await self._update_progress_bar()
            elif status == TASK_STATUS["FAILED"]:
                self.failed_tasks += 1
                await self._update_progress_bar()
            elif status == TASK_STATUS["TIMEOUT"]:
                self.timeout_tasks += 1
                await self._update_progress_bar()

        # Log status change
        if self.logger and details:
            self.logger.debug(f"Task {task_key}: {old_status} -> {status} ({details})")

    async def _update_progress_bar(self) -> None:
        """Update the progress bar display."""
        if not self.progress_bar:
            return

        async with self.progress_lock:
            self.progress_bar.update(1)

            completion_pct = (self.completed_tasks / self.total_tasks) * 100 if self.total_tasks > 0 else 0

            # Calculate time estimates
            if self.start_time:
                elapsed_time = time.time() - self.start_time
                if self.completed_tasks > 0:
                    avg_time_per_task = elapsed_time / self.completed_tasks
                    remaining_tasks = self.total_tasks - self.completed_tasks - self.failed_tasks - self.timeout_tasks
                    est_remaining_time = avg_time_per_task * remaining_tasks if remaining_tasks > 0 else 0

                    postfix = {
                        "completed": f"{completion_pct:.1f}%",
                        "failed": self.failed_tasks,
                        "timeout": self.timeout_tasks,
                    }

                    if est_remaining_time > 0:
                        postfix["eta"] = f"{est_remaining_time/60:.1f}m"

                    self.progress_bar.set_postfix(postfix)

    def write_progress_message(self, message: str) -> None:
        """Write a message that respects the progress bar.

        :param message: Message to display
        """
        if self.progress_bar:
            tqdm.write(message)
        else:
            print(message)

    def log_task_completion(
        self, task_name: str, duration: float, success: bool = True, details: Optional[str] = None
    ) -> None:
        """Log the completion of a task.

        :param task_name: Name of the completed task
        :param duration: Duration in seconds
        :param success: Whether the task completed successfully
        :param details: Optional additional details
        """
        status_icon = "✅" if success else "❌"
        message = f"{status_icon} {task_name} completed in {duration:.1f}s"

        if details:
            message += f" - {details}"

        self.write_progress_message(message)

        if self.logger:
            log_level = "info" if success else "warning"
            getattr(self.logger, log_level)(message)

    def log_task_timeout(self, task_name: str, timeout_duration: float) -> None:
        """Log a task timeout.

        :param task_name: Name of the timed out task
        :param timeout_duration: Timeout duration in seconds
        """
        message = f"⚠️ TIMEOUT: {task_name} after {timeout_duration}s"
        self.write_progress_message(message)

        if self.logger:
            self.logger.warning(message)

    def log_task_error(self, task_name: str, error: Exception) -> None:
        """Log a task error.

        :param task_name: Name of the failed task
        :param error: The exception that occurred
        """
        message = f"❌ ERROR: {task_name} - {error.__class__.__name__}: {str(error)}"
        self.write_progress_message(message)

        if self.logger:
            self.logger.error(message)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of progress and statistics.

        :return: Dictionary containing progress summary
        """
        total_time = None
        if self.start_time:
            end_time = self.end_time or time.time()
            total_time = end_time - self.start_time

        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "timeout_tasks": self.timeout_tasks,
            "success_rate": (self.completed_tasks / self.total_tasks) * 100 if self.total_tasks > 0 else 0,
            "total_time_seconds": total_time,
            "average_time_per_task": (
                total_time / self.completed_tasks if total_time and self.completed_tasks > 0 else None
            ),
            "task_statuses": self.task_statuses.copy(),
        }

    def print_summary(self) -> None:
        """Print a formatted summary of the progress."""
        summary = self.get_summary()

        self.write_progress_message("\n" + "=" * 60)
        self.write_progress_message("EXECUTION SUMMARY")
        self.write_progress_message("=" * 60)
        self.write_progress_message(f"Total Tasks: {summary['total_tasks']}")
        self.write_progress_message(f"Completed: {summary['completed_tasks']}")
        self.write_progress_message(f"Failed: {summary['failed_tasks']}")
        self.write_progress_message(f"Timeouts: {summary['timeout_tasks']}")
        self.write_progress_message(f"Success Rate: {summary['success_rate']:.1f}%")

        if summary["total_time_seconds"]:
            self.write_progress_message(f"Total Time: {summary['total_time_seconds']:.1f}s")

        if summary["average_time_per_task"]:
            self.write_progress_message(f"Avg Time/Task: {summary['average_time_per_task']:.1f}s")

        self.write_progress_message("=" * 60)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def create_progress_manager(
    total_tasks: int = 0, logger=None, show_progress_bar: bool = True, progress_desc: str = "Processing"
) -> ProgressManager:
    """Create a ProgressManager instance.

    :param total_tasks: Total number of tasks to track
    :param logger: Logger instance
    :param show_progress_bar: Whether to show progress bar
    :param progress_desc: Description for progress bar
    :return: Configured ProgressManager
    """
    return ProgressManager(
        total_tasks=total_tasks, logger=logger, show_progress_bar=show_progress_bar, progress_desc=progress_desc
    )
