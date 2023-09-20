# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import getLogger
from os import environ
from typing import Dict

from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.instrumentation.environment_variables import (
    OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
)
from opentelemetry.sdk.environment_variables import OTEL_TRACES_SAMPLER_ARG

from azure.monitor.opentelemetry._constants import (
    DISABLE_AZURE_CORE_TRACING_ARG,
    DISABLE_LOGGING_ARG,
    DISABLE_METRICS_ARG,
    DISABLE_TRACING_ARG,
    DISABLED_INSTRUMENTATIONS_ARG,
    SAMPLING_RATIO_ARG,
)
from azure.monitor.opentelemetry._types import ConfigurationValue


_INVALID_FLOAT_MESSAGE = "Value of %s must be a float. Defaulting to %s: %s"
_INVALID_INT_MESSAGE = "Value of %s must be a integer. Defaulting to %s: %s"


# TODO: remove when sampler uses env var instead
SAMPLING_RATIO_ENV_VAR = OTEL_TRACES_SAMPLER_ARG


_logger = getLogger(__name__)


def _get_configurations(**kwargs) -> Dict[str, ConfigurationValue]:
    configurations = {}

    for key, val in kwargs.items():
        configurations[key] = val

    _default_disable_logging(configurations)
    _default_disable_metrics(configurations)
    _default_disable_tracing(configurations)
    _default_disabled_instrumentations(configurations)
    _default_sampling_ratio(configurations)
    _default_disable_azure_core_tracing(configurations)

    return configurations


def _default_disable_logging(configurations):
    default = False
    if OTEL_LOGS_EXPORTER in environ:
        if environ[OTEL_LOGS_EXPORTER].lower().strip() == "none":
            default = True
    configurations[DISABLE_LOGGING_ARG] = default


def _default_disable_metrics(configurations):
    default = False
    if OTEL_METRICS_EXPORTER in environ:
        if environ[OTEL_METRICS_EXPORTER].lower().strip() == "none":
            default = True
    configurations[DISABLE_METRICS_ARG] = default


def _default_disable_tracing(configurations):
    default = False
    if OTEL_TRACES_EXPORTER in environ:
        if environ[OTEL_TRACES_EXPORTER].lower().strip() == "none":
            default = True
    configurations[DISABLE_TRACING_ARG] = default


def _default_disabled_instrumentations(configurations):
    disabled_instrumentation = environ.get(
        OTEL_PYTHON_DISABLED_INSTRUMENTATIONS, []
    )
    if isinstance(disabled_instrumentation, str):
        disabled_instrumentation = disabled_instrumentation.split(",")
        # to handle users entering "requests , flask" or "requests, flask" with spaces
        disabled_instrumentation = [
            x.strip() for x in disabled_instrumentation
        ]
    configurations[DISABLED_INSTRUMENTATIONS_ARG] = disabled_instrumentation


# TODO: remove when sampler uses env var instead
def _default_sampling_ratio(configurations):
    default = 1.0
    if SAMPLING_RATIO_ENV_VAR in environ:
        try:
            default = float(environ[SAMPLING_RATIO_ENV_VAR])
        except ValueError as e:
            _logger.error(
                _INVALID_FLOAT_MESSAGE,
                SAMPLING_RATIO_ENV_VAR,
                default,
                e,
            )
    configurations[SAMPLING_RATIO_ARG] = default


# TODO: Placeholder for future configuration
def _default_disable_azure_core_tracing(configurations):
    configurations[DISABLE_AZURE_CORE_TRACING_ARG] = False
