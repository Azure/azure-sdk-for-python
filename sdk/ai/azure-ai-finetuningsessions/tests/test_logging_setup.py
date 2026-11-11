# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for ``azure.ai.finetuningsessions._logging_setup``.

Verifies the no-handler timestamp filter the SDK installs on its emitting
loggers at package import time. The filter prepends an ISO-8601 UTC
timestamp to ``record.msg`` only when no handler is reachable; otherwise
it is a no-op (the caller's formatter owns the timestamp).
"""

from __future__ import annotations

import logging
import re
from typing import Iterator

import pytest

import azure.ai.finetuningsessions  # noqa: F401 -- triggers install_default_logging()
from azure.ai.finetuningsessions._logging_setup import (
    _ENV_VAR,
    _SDK_EMITTING_LOGGERS,
    _SdkTimestampFilter,
    _enabled_from_env,
    _has_any_handler,
    install_default_logging,
)

# Matches "[YYYY-MM-DDTHH:MM:SS.mmm+00:00] " at the start of a string.
_PREFIX_RE = re.compile(r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+00:00\] ")


def _make_record(name: str, msg: str = "hello", args: tuple = ()) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=logging.WARNING,
        pathname=__file__,
        lineno=0,
        msg=msg,
        args=args,
        exc_info=None,
    )


@pytest.fixture
def no_handlers_anywhere(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Make ``_has_any_handler`` return False for the SDK emitting loggers
    for the duration of the test.

    We flip ``propagate=False`` on each SDK emitting logger and clear its
    own handlers, reproducing the runtime condition where ``lastResort``
    would be invoked in a real unconfigured caller.

    Since pytest 9.1 (pytest-dev/pytest#3697) the logging plugin captures
    non-propagating loggers by attaching its own ``LogCaptureHandler``
    directly to each logger at the *start of the call phase* -- after this
    fixture's setup has already run. That handler would make
    ``_has_any_handler`` observe a handler a real caller would never have,
    so we also block ``addHandler`` on the SDK loggers for the duration of
    the test to keep them handler-free. ``monkeypatch`` restores the
    original ``handlers`` list, ``propagate`` flag, and ``addHandler``
    method on teardown.
    """
    sdk_loggers = [logging.getLogger(n) for n in _SDK_EMITTING_LOGGERS]
    for lg in sdk_loggers:
        monkeypatch.setattr(lg, "handlers", [])
        monkeypatch.setattr(lg, "propagate", False)
        monkeypatch.setattr(lg, "addHandler", lambda handler: None)
    yield


# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
class TestInstallation:
    def test_filter_attached_to_every_emitting_logger(self) -> None:
        for name in _SDK_EMITTING_LOGGERS:
            logger = logging.getLogger(name)
            assert any(
                isinstance(f, _SdkTimestampFilter) for f in logger.filters
            ), f"_SdkTimestampFilter not attached to {name!r}"

    def test_install_is_idempotent(self) -> None:
        install_default_logging()
        install_default_logging()
        for name in _SDK_EMITTING_LOGGERS:
            count = sum(isinstance(f, _SdkTimestampFilter) for f in logging.getLogger(name).filters)
            assert count == 1, f"{name!r} has {count} filters, expected 1"

    def test_no_handler_installed_by_sdk(self) -> None:
        for name in ("azure.ai.finetuningsessions", *_SDK_EMITTING_LOGGERS):
            assert logging.getLogger(name).handlers == [], f"SDK unexpectedly attached a handler to {name!r}"

    def test_propagation_unchanged(self) -> None:
        for name in _SDK_EMITTING_LOGGERS:
            assert logging.getLogger(name).propagate is True


# ---------------------------------------------------------------------------
# _has_any_handler chain walker
# ---------------------------------------------------------------------------
class TestHasAnyHandler:
    def test_true_when_root_has_handler(self) -> None:
        # Either pytest's plugin or a test-local handler will be present;
        # the SDK logger propagates up to root, so the walker sees it.
        root = logging.getLogger()
        had = bool(root.handlers)
        if not had:
            root.addHandler(logging.NullHandler())
        try:
            assert _has_any_handler(_SDK_EMITTING_LOGGERS[0]) is True
        finally:
            if not had:
                root.handlers.pop()

    def test_false_when_no_handler_anywhere(self, no_handlers_anywhere: None) -> None:
        assert _has_any_handler(_SDK_EMITTING_LOGGERS[0]) is False

    def test_propagate_false_blocks_walk(self, no_handlers_anywhere: None) -> None:
        # The fixture itself sets propagate=False on the SDK logger and
        # clears its handlers, so _has_any_handler must return False even
        # though the root logger has handlers (pytest's plugin).
        assert logging.getLogger().handlers, "test premise: root has handlers"
        assert _has_any_handler(_SDK_EMITTING_LOGGERS[0]) is False


# ---------------------------------------------------------------------------
# Filter behavior: prepend in Case B, no-op in Case A
# ---------------------------------------------------------------------------
class TestTimestampPrefix:
    def test_prepends_when_no_handler(self, no_handlers_anywhere: None) -> None:
        record = _make_record(_SDK_EMITTING_LOGGERS[0], "session crashed")
        # The filter both mutates the record and reports True (never
        # drops -- only annotates).
        assert _SdkTimestampFilter().filter(record) is True
        assert _PREFIX_RE.match(record.msg)
        assert record.msg.endswith("session crashed")

    def test_no_op_when_handler_present(self) -> None:
        logger = logging.getLogger(_SDK_EMITTING_LOGGERS[0])
        h = logging.NullHandler()
        logger.addHandler(h)
        try:
            sentinel = "untouched payload"
            record = _make_record(logger.name, sentinel)
            assert _has_any_handler(logger.name) is True
            assert _SdkTimestampFilter().filter(record) is True
            assert record.msg == sentinel
        finally:
            logger.removeHandler(h)

    def test_args_still_interpolate(self, no_handlers_anywhere: None) -> None:
        record = _make_record(_SDK_EMITTING_LOGGERS[0], "hello %s number %d", ("world", 7))
        _SdkTimestampFilter().filter(record)
        rendered = record.getMessage()
        assert _PREFIX_RE.match(rendered)
        assert rendered.endswith("hello world number 7")

    def test_uses_record_created_not_wall_clock(self, no_handlers_anywhere: None) -> None:
        # Pin record.created to a known epoch (2020-01-02 03:04:05.678 UTC).
        record = _make_record(_SDK_EMITTING_LOGGERS[0])
        record.created = 1577934245.678
        _SdkTimestampFilter().filter(record)
        assert record.msg.startswith("[2020-01-02T03:04:05.678+00:00] ")

    def test_timestamp_visible_under_lastresort_format(self, no_handlers_anywhere: None) -> None:
        """Rendering through ``logging.lastResort``'s format string
        (``"%(levelname)s:%(name)s:%(message)s"``) must include a
        timestamp, because the filter put it inside ``record.msg``.
        """
        record = _make_record(_SDK_EMITTING_LOGGERS[0], "session crashed")
        _SdkTimestampFilter().filter(record)
        rendered = logging.Formatter("%(levelname)s:%(name)s:%(message)s").format(record)
        assert "session crashed" in rendered
        assert re.search(
            r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+00:00\]", rendered
        ), f"timestamp missing from lastResort-formatted output: {rendered!r}"


# ---------------------------------------------------------------------------
# End-to-end: actual SDK module loggers, dispatched through lastResort
# ---------------------------------------------------------------------------
class TestEndToEndSessionCrash:
    """Drive the real SDK ``_patch`` / ``aio._patch`` loggers the way the
    SDK does at a session-crash / heartbeat-failure call site, route the
    record through ``logging.lastResort``, and verify the stderr line a
    real unconfigured caller would see includes a timestamp.
    """

    @pytest.mark.parametrize("module_name", list(_SDK_EMITTING_LOGGERS))
    def test_heartbeat_warning_includes_timestamp_via_lastresort(
        self, module_name: str, no_handlers_anywhere: None
    ) -> None:
        import importlib
        import io

        mod = importlib.import_module(module_name)
        sdk_logger = mod._logger
        assert sdk_logger.name == module_name

        # Capture what lastResort would write to stderr by swapping it
        # for a StringIO-backed StreamHandler that uses lastResort's
        # exact hardcoded format.
        buf = io.StringIO()
        capture = logging.StreamHandler(buf)
        capture.setLevel(logging.WARNING)
        capture.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
        prior_lastresort = logging.lastResort
        logging.lastResort = capture
        try:
            sdk_logger.warning("[heartbeat] failed for %s: %s", "sess-123", "ConnectionError")
        finally:
            logging.lastResort = prior_lastresort

        line = buf.getvalue()
        assert "[heartbeat] failed for sess-123: ConnectionError" in line
        assert re.search(
            r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+00:00\]", line
        ), f"timestamp missing from end-to-end output: {line!r}"

    @pytest.mark.parametrize(
        ("level_method", "level_label"),
        [
            ("debug", "DEBUG"),
            ("info", "INFO"),
            ("warning", "WARNING"),
            ("error", "ERROR"),
            ("critical", "CRITICAL"),
            ("exception", "ERROR"),
        ],
    )
    def test_all_levels_get_timestamp_via_lastresort(
        self,
        level_method: str,
        level_label: str,
        no_handlers_anywhere: None,
    ) -> None:
        """The filter is level-agnostic: every severity (DEBUG through
        CRITICAL, plus ``exception``) gets a timestamp prefix when the
        record reaches lastResort. Both Python-side level gates (the
        logger's and lastResort's, default WARNING) are opened so the
        test exercises the filter at every level, including the ones
        that would otherwise be dropped before dispatch.
        """
        import importlib
        import io

        mod = importlib.import_module(_SDK_EMITTING_LOGGERS[0])
        sdk_logger = mod._logger

        buf = io.StringIO()
        capture = logging.StreamHandler(buf)
        capture.setLevel(logging.DEBUG)  # Gate 2: lastResort
        capture.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
        prior_lastresort = logging.lastResort
        prior_logger_level = sdk_logger.level
        logging.lastResort = capture
        sdk_logger.setLevel(logging.DEBUG)  # Gate 1: logger
        try:
            if level_method == "exception":
                try:
                    raise RuntimeError("boom")
                except RuntimeError:
                    sdk_logger.exception("session crashed: %s", "sess-123")
            else:
                getattr(sdk_logger, level_method)("session crashed: %s", "sess-123")
        finally:
            logging.lastResort = prior_lastresort
            sdk_logger.setLevel(prior_logger_level)

        line = buf.getvalue()
        assert line.startswith(f"{level_label}:"), f"unexpected level in {line!r}"
        assert "session crashed: sess-123" in line
        assert re.search(
            r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+00:00\]", line
        ), f"timestamp missing from {level_label} output: {line!r}"


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------
class TestPublicSurface:
    def test_only_install_default_logging_is_public(self) -> None:
        from azure.ai.finetuningsessions import _logging_setup as m

        assert m.__all__ == ["install_default_logging"]


# ---------------------------------------------------------------------------
# Env-var opt-out + programmatic enable/disable
# ---------------------------------------------------------------------------
@pytest.fixture
def restore_filter() -> Iterator[None]:
    yield
    install_default_logging(enabled=True)


class TestEnableDisableFlag:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            # Falsey values -> filter disabled.
            ("0", False),
            ("false", False),
            ("FALSE", False),
            ("No", False),
            ("off", False),
            ("disable", False),
            ("disabled", False),
            (" 0 ", False),
            # Truthy / unrecognized -> filter enabled (opt-out semantics).
            ("1", True),
            ("true", True),
            ("yes", True),
            ("on", True),
            ("enable", True),
            ("enabled", True),
            ("", True),
            ("anything", True),
            # Unset env var -> enabled.
            (None, True),
        ],
    )
    def test_enabled_from_env(
        self,
        raw: str | None,
        expected: bool,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        if raw is None:
            monkeypatch.delenv(_ENV_VAR, raising=False)
        else:
            monkeypatch.setenv(_ENV_VAR, raw)
        assert _enabled_from_env() is expected

    @pytest.mark.parametrize(
        "trigger",
        ["explicit_flag", "env_var"],
        ids=["enabled=False", "env=0"],
    )
    def test_disable_removes_filter(
        self,
        trigger: str,
        monkeypatch: pytest.MonkeyPatch,
        restore_filter: None,
    ) -> None:
        if trigger == "explicit_flag":
            install_default_logging(enabled=False)
        else:
            # Wipe any pre-installed filter, then install with env=falsey
            # and no explicit ``enabled`` so the env var is consulted.
            install_default_logging(enabled=False)
            monkeypatch.setenv(_ENV_VAR, "0")
            install_default_logging()
        for name in _SDK_EMITTING_LOGGERS:
            assert not any(
                isinstance(f, _SdkTimestampFilter) for f in logging.getLogger(name).filters
            ), f"filter still present on {name!r} after disable via {trigger}"

    def test_disable_then_enable_reinstalls(self, restore_filter: None) -> None:
        install_default_logging(enabled=False)
        install_default_logging(enabled=True)
        for name in _SDK_EMITTING_LOGGERS:
            count = sum(isinstance(f, _SdkTimestampFilter) for f in logging.getLogger(name).filters)
            assert count == 1, f"{name!r} has {count} filters, expected 1"

    def test_disabled_filter_does_not_mutate(self, no_handlers_anywhere: None, restore_filter: None) -> None:
        install_default_logging(enabled=False)
        logger = logging.getLogger(_SDK_EMITTING_LOGGERS[0])
        # No filter installed -> calling logger.warning() goes straight
        # through the (empty) filter list. Simulate the dispatch by hand:
        # walk filters, then check msg is unchanged.
        record = _make_record(logger.name, "raw")
        for f in logger.filters:
            f.filter(record)
        assert record.msg == "raw"
