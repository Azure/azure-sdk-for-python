# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Original source:
# - promptflow-core/promptflow/_core/log_manager.py
# - promptflow-core/promptflow/_utils/logger_utils.py

import os
import logging
import re
import sys
from re import Pattern
from contextvars import ContextVar
from datetime import datetime, timezone
from dataclasses import dataclass
from io import StringIO, TextIOBase
from typing import Any, Dict, Final, Mapping, Optional, Set, TextIO, Tuple, Union


valid_logging_level: Final[Set[str]] = {"CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "NOTSET"}


def get_pf_logging_level(default=logging.INFO):
    logging_level = os.environ.get("PF_LOGGING_LEVEL", None)
    if logging_level not in valid_logging_level:
        # Fall back to info if user input is invalid.
        logging_level = default
    return logging_level


def _get_format_for_logger(
    default_log_format: Optional[str] = None, default_date_format: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get the logging format and date format for logger.

    This function attempts to find the handler of the root logger with a configured formatter.
    If such a handler is found, it returns the format and date format used by this handler.
    This can be configured through logging.basicConfig. If no configured formatter is found,
    it defaults to LOG_FORMAT and DATETIME_FORMAT.
    """
    log_format = (
        os.environ.get("PF_LOG_FORMAT")
        or default_log_format
        or "%(asctime)s %(thread)7d %(name)-18s %(levelname)-8s %(message)s"
    )
    datetime_format = os.environ.get("PF_LOG_DATETIME_FORMAT") or default_date_format or "%Y-%m-%d %H:%M:%S %z"
    return log_format, datetime_format


def get_logger(name: str) -> logging.Logger:
    """Get logger used during execution."""
    logger = logging.Logger(name)
    logger.setLevel(get_pf_logging_level())
    # logger.addHandler(FileHandlerConcurrentWrapper())
    stdout_handler = logging.StreamHandler(sys.stdout)
    fmt, datefmt = _get_format_for_logger()
    # TODO ralphe: Do we need a credentials scrubber here like the old code had? We are not logging
    #              logging anything that sensitive here.
    stdout_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(stdout_handler)
    return logger


def scrub_credentials(s: str):
    """Scrub credentials in string s.

    For example, for input string: "print accountkey=accountKey", the output will be:
    "print accountkey=**data_scrubbed**"
    """
    # for h in logger.handlers:
    #     if isinstance(h, FileHandlerConcurrentWrapper):
    #         if h.handler and h.handler._formatter:
    #             credential_scrubber = h.handler._formatter.credential_scrubber
    #             if credential_scrubber:
    #                 return credential_scrubber.scrub(s)
    return CredentialScrubber.scrub(s)


class CredentialScrubber:
    """Scrub sensitive information in string."""

    PLACE_HOLDER = "**data_scrubbed**"
    LENGTH_THRESHOLD = 2
    DEFAULT_REGEX_SET: Final[Set[Pattern[str]]] = {
        re.compile(r"(?<=sig=)[^\s;&]+", flags=re.IGNORECASE),  # Replace signature.
        re.compile(r"(?<=key=)[^\s;&]+", flags=re.IGNORECASE),  # Replace key.
    }

    @staticmethod
    def scrub(input: str) -> str:
        """Replace sensitive information in input string with PLACE_HOLDER.

        For example, for input string: "print accountkey=accountKey", the output will be:
        "print accountkey=**data_scrubbed**"
        """
        output = input
        for regex in CredentialScrubber.DEFAULT_REGEX_SET:
            output = regex.sub(CredentialScrubber.PLACE_HOLDER, output)
        return output


# Logs by flow_logger will only be shown in flow mode.
# These logs should contain all detailed logs from executor and runtime.
flow_logger = get_logger("execution.flow")

# Logs by bulk_logger will only be shown in bulktest and eval modes.
# These logs should contain overall progress logs and error logs.
bulk_logger = get_logger("execution.bulk")

# Logs by logger will be shown in all the modes above,
# such as error logs.
logger = get_logger("execution")


def log_progress(
    run_start_time: datetime,
    total_count: int,
    current_count: int,
    logger: logging.Logger = bulk_logger,
    formatter="Finished {count} / {total_count} lines.",
) -> None:
    if current_count > 0:
        delta = datetime.now(timezone.utc).timestamp() - run_start_time.timestamp()
        average_execution_time = round(delta / current_count, 2)
        estimated_execution_time = round(average_execution_time * (total_count - current_count), 2)
        logger.info(formatter.format(count=current_count, total_count=total_count))
        logger.info(
            f"Average execution time for completed lines: {average_execution_time} seconds. "
            f"Estimated time for incomplete lines: {estimated_execution_time} seconds."
        )


def incremental_print(log: str, printed: int, fileout: Union[TextIO, Any]) -> int:
    count = 0
    for line in log.splitlines():
        if count >= printed:
            fileout.write(line + "\n")
            printed += 1
        count += 1
    return printed


def print_red_error(message):
    try:
        from colorama import Fore, init

        init(autoreset=True)
        print(Fore.RED + message)
    except ImportError:
        print(message)


@dataclass
class NodeInfo:
    run_id: str
    node_name: str
    line_number: int


class NodeLogManager:
    """Replace sys.stdout and sys.stderr with NodeLogWriter.

    This class intercepts and saves logs to stdout/stderr when executing a node. For example:
    with NodeLogManager() as log_manager:
        print('test stdout')
        print('test stderr', file=sys.stderr)

    log_manager.get_logs() will return: {'stdout': 'test stdout\n', 'stderr': 'test stderr\n'}
    """

    def __init__(self, record_datetime: bool = True):
        self.stdout_logger = NodeLogWriter(sys.stdout, record_datetime)
        self.stderr_logger = NodeLogWriter(sys.stderr, record_datetime, is_stderr=True)

    def __enter__(self) -> "NodeLogManager":
        """Replace sys.stdout and sys.stderr with NodeLogWriter."""
        self._prev_stdout = sys.stdout
        self._prev_stderr = sys.stderr
        sys.stdout = self.stdout_logger
        sys.stderr = self.stderr_logger
        return self

    def __exit__(self, *args) -> None:
        """Restore sys.stdout and sys.stderr."""
        sys.stdout = self._prev_stdout
        sys.stderr = self._prev_stderr

    def set_node_context(self, run_id: str, node_name: str, line_number: int) -> None:
        """Set node context."""
        self.stdout_logger.set_node_info(run_id, node_name, line_number)
        self.stderr_logger.set_node_info(run_id, node_name, line_number)

    def clear_node_context(self, run_id: str) -> None:
        """Clear node context."""
        self.stdout_logger.clear_node_info(run_id)
        self.stderr_logger.clear_node_info(run_id)

    def get_logs(self, run_id: str) -> Mapping[str, str]:
        return {
            "stdout": self.stdout_logger.get_log(run_id),
            "stderr": self.stderr_logger.get_log(run_id),
        }


class NodeLogWriter(TextIOBase):
    """Record node run logs."""

    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, prev_stdout: Union[TextIOBase, Any], record_datetime: bool = True, is_stderr: bool = False):
        self.run_id_to_stdout: Dict[str, StringIO] = {}
        self._context: ContextVar[Optional[NodeInfo]] = ContextVar("run_log_info", default=None)
        self._prev_out: Union[TextIOBase, Any] = prev_stdout
        self._record_datetime: bool = record_datetime
        self._is_stderr: bool = is_stderr

    def set_node_info(self, run_id: str, node_name: str, line_number: int) -> None:
        """Set node info to a context variable.

        After set node info, write method will write to string IO associated with this node.
        """
        run_log_info = NodeInfo(run_id, node_name, line_number)
        self._context.set(run_log_info)
        self.run_id_to_stdout.update({run_id: StringIO()})

    def clear_node_info(self, run_id: str):
        """Clear context variable associated with run id."""
        log_info: Optional[NodeInfo] = self._context.get()
        if log_info and log_info.run_id == run_id:
            self._context.set(None)

        if run_id in self.run_id_to_stdout:
            self.run_id_to_stdout.pop(run_id)

    def get_log(self, run_id: str) -> str:
        """Get log associated with run id."""
        string_io: Optional[StringIO] = self.run_id_to_stdout.get(run_id)
        if string_io is None:
            return ""

        return string_io.getvalue()

    def write(self, s: str) -> int:
        """Override TextIO's write method and writes input string into a string IO

        The written string is compliant without any credentials.
        The string is also recorded to flow/bulk logger.
        If node info is not set, write to previous stdout.
        """
        log_info: Optional[NodeInfo] = self._context.get()
        s = scrub_credentials(s)  # Remove credential from string.
        if log_info is None:
            return self._prev_out.write(s)
        else:
            self._write_to_flow_log(log_info, s)
            stdout: Optional[StringIO] = self.run_id_to_stdout.get(log_info.run_id)
            # When the line execution timeout is reached, all running nodes will be cancelled and node info will
            # be cleared. This will remove StringIO from self.run_id_to_stdout. For sync tools running in a worker
            # thread, they can't be stopped and self._context won't change in the worker
            # thread because it's a thread-local variable. Therefore, we need to check if StringIO is None here.
            if stdout is None:
                return 0
            if self._record_datetime and s != "\n":  # For line breaker, do not add datetime prefix.
                s = f"[{datetime.now(timezone.utc).strftime(self.DATETIME_FORMAT)}] {s}"
            return stdout.write(s)

    def flush(self):
        """Override TextIO's flush method."""
        node_info: Optional[NodeInfo] = self._context.get()
        if node_info is None:
            self._prev_out.flush()
        else:
            string_io = self.run_id_to_stdout.get(node_info.run_id)
            if string_io is not None:
                string_io.flush()

    def _write_to_flow_log(self, log_info: NodeInfo, s: str):
        """Save stdout log to flow_logger and stderr log to logger."""
        # If user uses "print('log message.')" to log, then
        # "write" method will be called twice and the second time input is only '\n'.
        # For this case, should not log '\n' in flow_logger.
        if s != "\n":
            if self._is_stderr:
                flow_log = f"[{str(log_info)}] stderr> " + s.rstrip("\n")
                # Log stderr in all scenarios so we can diagnose problems.
                logger.warning(flow_log)
            else:
                flow_log = f"[{str(log_info)}] stdout> " + s.rstrip("\n")
                # Log stdout only in flow mode.
                flow_logger.info(flow_log)
