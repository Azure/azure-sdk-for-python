# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging

from azure.ai.agentserver.core import experimental
from azure.ai.agentserver.core._experimental import (
    DISABLE_EXPERIMENTAL_WARNING_ENV_VAR,
    EXPERIMENTAL_CLASS_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
    EXPERIMENTAL_METHOD_MESSAGE,
    _warning_cache,
)
from azure.ai.agentserver.core.tasks import resilient_tasks_enabled


@experimental
class ExperimentalClass:
    """A test class."""

    def __init__(self) -> None:
        self.value = 1


@experimental
def experimental_function() -> bool:
    """A test function."""
    return True


def test_experimental_decorator_on_class(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        ExperimentalClass()

    assert ExperimentalClass.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_CLASS_MESSAGE in ExperimentalClass.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in ExperimentalClass.__doc__
    assert len(caplog.records) == 1
    assert EXPERIMENTAL_CLASS_MESSAGE in caplog.records[0].message


def test_experimental_decorator_on_function(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        assert experimental_function() is True

    assert experimental_function.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_METHOD_MESSAGE in experimental_function.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in experimental_function.__doc__
    assert len(caplog.records) == 1
    assert EXPERIMENTAL_METHOD_MESSAGE in caplog.records[0].message


def test_experimental_decorator_no_duplicate_warnings(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        experimental_function()
        experimental_function()

    assert len(caplog.records) == 1


def test_experimental_decorator_env_var_suppresses_warning(monkeypatch, caplog) -> None:
    _warning_cache.clear()
    monkeypatch.setenv(DISABLE_EXPERIMENTAL_WARNING_ENV_VAR, "true")

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        experimental_function()

    assert len(caplog.records) == 0


def test_resilient_task_public_api_is_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        resilient_tasks_enabled()

    assert resilient_tasks_enabled.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_METHOD_MESSAGE in resilient_tasks_enabled.__doc__
    assert len(caplog.records) == 1
