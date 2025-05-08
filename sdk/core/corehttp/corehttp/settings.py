# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Union


def _convert_bool(value: Union[str, bool]) -> bool:
    """Convert a string to True or False

    If a boolean is passed in, it is returned as-is. Otherwise the function
    maps the following strings, ignoring case:

    * "yes", "1", "on" -> True
    * "no", "0", "off" -> False

    :param value: the value to convert
    :type value: str or bool
    :returns: A boolean value matching the intent of the input
    :rtype: bool
    :raises ValueError: If conversion to bool fails

    """
    if isinstance(value, bool):
        return value
    val = value.lower()
    if val in ["yes", "1", "on", "true", "True"]:
        return True
    if val in ["no", "0", "off", "false", "False"]:
        return False
    raise ValueError("Cannot convert {} to boolean value".format(value))


class Settings:
    """Global settings for the SDK."""

    def __init__(self) -> None:
        self._tracing_enabled: bool = _convert_bool(os.environ.get("SDK_TRACING_ENABLED", False))

    @property
    def tracing_enabled(self) -> bool:
        """Whether tracing for SDKs is enabled.

        :return: True if tracing is enabled, False otherwise.
        :rtype: bool
        """
        return self._tracing_enabled

    @tracing_enabled.setter
    def tracing_enabled(self, value: bool):
        self._tracing_enabled = _convert_bool(value)


settings: Settings = Settings()
"""The settings global instance.

:type settings: Settings
"""
