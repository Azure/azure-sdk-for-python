import sys
from contextlib import ExitStack
from io import StringIO

import pytest

from azure.ai.evaluation._legacy._common._logging import NodeLogManager, NodeLogWriter


@pytest.mark.unittest
def test_node_log_writer_unwraps_nested_prev_out(monkeypatch):
    base_out = StringIO()
    inner = NodeLogWriter(base_out)
    outer = NodeLogWriter(inner)

    outer.write("hello")

    assert base_out.getvalue() == "hello"


@pytest.mark.unittest
def test_nested_node_log_manager_restores_outer_run_context(monkeypatch):
    # Regression test for https://github.com/Azure/azure-sdk-for-python/issues/49274:
    # a nested manager reuses the outer writer, and its set_node_context overwrites the
    # writer's shared context. Exiting the inner manager must restore the outer run id so
    # later outer output is not attributed to the inner run.
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    outer = NodeLogManager()
    outer.set_node_context("r1", "Flex", 1)
    with outer:
        print("outer-before")
        inner = NodeLogManager()
        inner.set_node_context("r2", "Flex", 1)
        with inner:
            print("inner-line")
        print("outer-after")
        r1_logs = outer.get_logs("r1")["stdout"]
        r2_logs = outer.get_logs("r2")["stdout"]

    assert "outer-before" in r1_logs
    assert "outer-after" in r1_logs
    assert "inner-line" in r2_logs
    assert "outer-after" not in r2_logs


@pytest.mark.unittest
def test_nested_node_log_manager_does_not_recurse(monkeypatch):
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    original_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(300)
    try:
        with ExitStack() as stack:
            for _ in range(500):
                stack.enter_context(NodeLogManager())
            print("nested")
            sys.stderr.write("stderr")
    finally:
        sys.setrecursionlimit(original_limit)

    assert "nested" in base_out.getvalue()
    assert "stderr" in base_err.getvalue()
