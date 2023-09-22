# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Provide access to settings for globally used Azure configuration values.
"""
from __future__ import annotations
from enum import Enum
import logging
import sys
from typing import Type, Optional, Callable, Union, Dict, TypeVar

from generic.core.settings import PrioritizedSetting, Settings as GenericSettings, convert_bool, convert_logging
from generic.core.tracing import AbstractSpan


ValidInputType = TypeVar("ValidInputType")
ValueType = TypeVar("ValueType")


__all__ = ("settings", "Settings")


# https://www.python.org/dev/peps/pep-0484/#support-for-singleton-types-in-unions
class _Unset(Enum):
    token = 0


_unset = _Unset.token


def _get_opencensus_span() -> Optional[Type[AbstractSpan]]:
    """Returns the OpenCensusSpan if the opencensus tracing plugin is installed else returns None.

    :rtype: type[AbstractSpan] or None
    :returns: OpenCensusSpan type or None
    """
    try:
        from azure.core.tracing.ext.opencensus_span import (  # pylint:disable=redefined-outer-name
            OpenCensusSpan,
        )

        return OpenCensusSpan
    except ImportError:
        return None


def _get_opentelemetry_span() -> Optional[Type[AbstractSpan]]:
    """Returns the OpenTelemetrySpan if the opentelemetry tracing plugin is installed else returns None.

    :rtype: type[AbstractSpan] or None
    :returns: OpenTelemetrySpan type or None
    """
    try:
        from azure.core.tracing.ext.opentelemetry_span import (  # pylint:disable=redefined-outer-name
            OpenTelemetrySpan,
        )

        return OpenTelemetrySpan
    except ImportError:
        return None


def _get_opencensus_span_if_opencensus_is_imported() -> Optional[Type[AbstractSpan]]:
    if "opencensus" not in sys.modules:
        return None
    return _get_opencensus_span()


def _get_opentelemetry_span_if_opentelemetry_is_imported() -> Optional[Type[AbstractSpan]]:
    if "opentelemetry" not in sys.modules:
        return None
    return _get_opentelemetry_span()


_tracing_implementation_dict: Dict[str, Callable[[], Optional[Type[AbstractSpan]]]] = {
    "opencensus": _get_opencensus_span,
    "opentelemetry": _get_opentelemetry_span,
}


def convert_tracing_impl(value: Optional[Union[str, Type[AbstractSpan]]]) -> Optional[Type[AbstractSpan]]:
    """Convert a string to AbstractSpan

    If a AbstractSpan is passed in, it is returned as-is. Otherwise the function
    understands the following strings, ignoring case:

    * "opencensus"
    * "opentelemetry"

    :param value: the value to convert
    :type value: string
    :returns: AbstractSpan
    :raises ValueError: If conversion to AbstractSpan fails

    """
    if value is None:
        return (
            _get_opencensus_span_if_opencensus_is_imported() or _get_opentelemetry_span_if_opentelemetry_is_imported()
        )

    if not isinstance(value, str):
        return value

    value = value.lower()
    get_wrapper_class = _tracing_implementation_dict.get(value, lambda: _unset)
    wrapper_class: Optional[Union[_Unset, Type[AbstractSpan]]] = get_wrapper_class()
    if wrapper_class is _unset:
        raise ValueError(
            "Cannot convert {} to AbstractSpan, valid values are: {}".format(
                value, ", ".join(_tracing_implementation_dict)
            )
        )
    return wrapper_class


class Settings(GenericSettings):
    """Settings for globally used Azure configuration values.

    You probably don't want to create an instance of this class, but call the singleton instance:

    .. code-block:: python

        from azure.core.settings import settings
        settings.log_level = log_level = logging.DEBUG

    The following methods are searched in order for a setting:

    4. immediate values
    3. previously user-set value
    2. environment variable
    1. system setting
    0. implicit default

    An implicit default is (optionally) defined by the setting attribute itself.

    A system setting value can be obtained from registries or other OS configuration
    for settings that support that method.

    An environment variable value is obtained from ``os.environ``

    User-set values many be specified by assigning to the attribute:

    .. code-block:: python

        settings.log_level = log_level = logging.DEBUG

    Immediate values are (optionally) provided when the setting is retrieved:

    .. code-block:: python

        settings.log_level(logging.DEBUG())

    Immediate values are most often useful to provide from optional arguments
    to client functions. If the argument value is not None, it will be returned
    as-is. Otherwise, the setting searches other methods according to the
    precedence rules.

    Immutable configuration snapshots can be created with the following methods:

    * settings.defaults returns the base defaultsvalues , ignoring any environment or system
      or user settings

    * settings.current returns the current computation of settings including prioritization
      of configuration sources, unless defaults_only is set to True (in which case the result
      is identical to settings.defaults)

    * settings.config can be called with specific values to override what settings.current
      would provide

    .. code-block:: python

        # return current settings with log level overridden
        settings.config(log_level=logging.DEBUG)

    :cvar log_level: a log level to use across all Azure client SDKs (AZURE_LOG_LEVEL)
    :type log_level: PrioritizedSetting
    :cvar tracing_enabled: Whether tracing should be enabled across Azure SDKs (AZURE_TRACING_ENABLED)
    :type tracing_enabled: PrioritizedSetting
    :cvar tracing_implementation: The tracing implementation to use (AZURE_SDK_TRACING_IMPLEMENTATION)
    :type tracing_implementation: PrioritizedSetting

    :Example:

    >>> import logging
    >>> from azure.core.settings import settings
    >>> settings.log_level = logging.DEBUG
    >>> settings.log_level()
    10

    >>> settings.log_level(logging.WARN)
    30

    """

    # TODO: Consider allowing generic env vars to work in tandem.
    log_level: PrioritizedSetting[Union[str, int], int] = PrioritizedSetting(
        "log_level",
        env_var="AZURE_LOG_LEVEL",
        convert=convert_logging,
        default=logging.INFO,
    )

    tracing_enabled: PrioritizedSetting[Union[str, bool], bool] = PrioritizedSetting(
        "tracing_enabled",
        env_var="AZURE_TRACING_ENABLED",
        convert=convert_bool,
        default=False,
    )

    tracing_implementation: PrioritizedSetting[
        Optional[Union[str, Type[AbstractSpan]]], Optional[Type[AbstractSpan]]
    ] = PrioritizedSetting(
        "tracing_implementation",
        env_var="AZURE_SDK_TRACING_IMPLEMENTATION",
        convert=convert_tracing_impl,
        default=None,
    )



settings: Settings = Settings()
"""The settings unique instance.

:type settings: Settings
"""
