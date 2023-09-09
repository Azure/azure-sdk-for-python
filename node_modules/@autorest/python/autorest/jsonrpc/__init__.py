# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional, Union
import logging
import logging.config  # need to include this extra import so mypy doesn't throw logging module has no config
from pathlib import Path


class Channel(Enum):
    # Information is considered the mildest of responses; not necesarily actionable.
    Information = "information"

    # Warnings are considered important for best practices, but not catastrophic in nature.
    Warning = "warning"

    # Errors are considered blocking issues that block a successful operation.
    Error = "error"

    # Debug messages are designed for the developer to communicate internal autorest implementation details.
    Debug = "debug"

    # Verbose messages give the user additional clarity on the process.
    Verbose = "verbose"

    # Catastrophic failure, likely abending the process.
    Fatal = "fatal"


_LEVEL_MAPPING = {
    logging.CRITICAL: Channel.Fatal,
    logging.ERROR: Channel.Error,
    logging.WARNING: Channel.Warning,
    logging.INFO: Channel.Information,
    logging.DEBUG: Channel.Debug,
}


class AutorestHandler(logging.Handler):
    def __init__(self, autorest_api: "AutorestAPI") -> None:
        # Initialize this handler with the max loglevel, since
        # autorest is deciding what to show, not us
        # so we want to log everything and let autorest filters.
        super().__init__(logging.DEBUG)
        self._autorest_api = autorest_api

    @staticmethod
    def _get_log_level(level: int) -> Channel:
        """Convert Python log levels to Autorest Channel."""
        return _LEVEL_MAPPING.get(level, Channel.Warning)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._autorest_api.message(self._get_log_level(record.levelno), msg)
        except RecursionError:  # See issue 36272
            raise
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)


class AutorestAPI(ABC):
    """Defines the base interface of communication to Autorest from the plugin."""

    def __init__(self) -> None:
        if Path("logging.conf").exists():
            logging.config.fileConfig(Path("logging.conf"))
        else:
            self._handler: Optional["AutorestHandler"] = AutorestHandler(self)
            fmt = logging.Formatter("[%(name)s.%(funcName)s:%(lineno)d] %(message)s")
            self._handler.setFormatter(fmt)
            logging.getLogger().addHandler(self._handler)
            logging.getLogger().setLevel(logging.DEBUG)

    def close(self) -> None:
        if self._handler:
            logging.getLogger().removeHandler(self._handler)
            self._handler = None

    @abstractmethod
    def write_file(self, filename: Union[str, Path], file_content: str) -> None:
        """Ask autorest to write the content to the current path.

        pathlib.Path object are acceptable but must be relative.

        :param filename: A file path
        :param file_content: The content as string
        """

    @abstractmethod
    def read_file(self, filename: Union[str, Path]) -> str:
        """Ask autorest to read a file for me.

        pathlib.Path object are acceptable but must be relative.

        :param filename: A file path
        :return: The content of the file
        :rtype: str
        """

    @abstractmethod
    def list_inputs(self) -> List[str]:
        """List possible inputs for this plugin."""

    @abstractmethod
    def get_value(self, key: str) -> Any:
        """Get a value from configuration."""

    @abstractmethod
    def message(self, channel: Channel, text: str) -> None:
        """Send a log message to autorest."""

    def get_boolean_value(
        self, key: str, default: Optional[bool] = None
    ) -> Optional[bool]:
        """Check if value is present on the line, and interpret it as bool if it was.

        If value is not not on the line, return the "default".
        If the value is present, will also accept "true" or 1 as True.

        For autorest, empty dict means "it was on the line", so we want it to true.

        :returns: A boolean if it was present, or None if not
        :rtype: Optional[bool]
        """
        result = self.get_value(key)
        if result is None:
            return default
        if result == {}:  # autorest received --myoption
            return True
        if isinstance(result, bool):
            return result
        # Try as a string
        try:
            return result.lower() == "true"
        except AttributeError:  # not a string
            pass
        return result == 1
