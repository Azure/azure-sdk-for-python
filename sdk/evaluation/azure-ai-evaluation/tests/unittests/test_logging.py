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
    assert "inner-line" not in r1_logs
    assert "outer-before" not in r2_logs


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


@pytest.mark.unittest
def test_nested_node_log_manager_restores_outer_stderr_context(monkeypatch):
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    outer = NodeLogManager()
    outer.set_node_context("r1", "Flex", 1)
    with outer:
        sys.stderr.write("outer-err-before\n")
        inner = NodeLogManager()
        inner.set_node_context("r2", "Flex", 1)
        with inner:
            sys.stderr.write("inner-err-line\n")
        sys.stderr.write("outer-err-after\n")
        r1_err = outer.get_logs("r1")["stderr"]
        r2_err = outer.get_logs("r2")["stderr"]

    assert "outer-err-before" in r1_err
    assert "outer-err-after" in r1_err
    assert "inner-err-line" in r2_err
    assert "outer-err-after" not in r2_err
    assert "inner-err-line" not in r1_err
    assert "outer-err-before" not in r2_err


@pytest.mark.unittest
def test_multi_level_nested_node_log_manager(monkeypatch):
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    mgr1 = NodeLogManager()
    mgr1.set_node_context("r1", "node1", 1)
    with mgr1:
        print("m1-before")
        mgr2 = NodeLogManager()
        mgr2.set_node_context("r2", "node2", 2)
        with mgr2:
            print("m2-before")
            mgr3 = NodeLogManager()
            mgr3.set_node_context("r3", "node3", 3)
            with mgr3:
                print("m3-body")
            print("m2-after")
        print("m1-after")

        logs1 = mgr1.get_logs("r1")["stdout"]
        logs2 = mgr1.get_logs("r2")["stdout"]
        logs3 = mgr1.get_logs("r3")["stdout"]

    assert "m1-before" in logs1
    assert "m1-after" in logs1
    assert "m2-before" not in logs1
    assert "m2-after" not in logs1
    assert "m3-body" not in logs1

    assert "m2-before" in logs2
    assert "m2-after" in logs2
    assert "m1-before" not in logs2
    assert "m1-after" not in logs2
    assert "m3-body" not in logs2

    assert "m3-body" in logs3
    assert "m1-before" not in logs3
    assert "m1-after" not in logs3
    assert "m2-before" not in logs3
    assert "m2-after" not in logs3


@pytest.mark.unittest
def test_nested_node_log_manager_exception_recovery(monkeypatch):
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
        try:
            inner = NodeLogManager()
            inner.set_node_context("r2", "Flex", 2)
            with inner:
                print("inner-body")
                raise ValueError("simulated inner failure")
        except ValueError:
            pass
        print("outer-after")

        r1_logs = outer.get_logs("r1")["stdout"]
        r2_logs = outer.get_logs("r2")["stdout"]

    assert "outer-before" in r1_logs
    assert "outer-after" in r1_logs
    assert "inner-body" in r2_logs
    assert "outer-after" not in r2_logs
    assert "inner-body" not in r1_logs
    assert "outer-before" not in r2_logs


@pytest.mark.unittest
def test_nested_node_log_manager_outer_without_context(monkeypatch):
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    outer = NodeLogManager()
    with outer:
        print("outer-before")
        inner = NodeLogManager()
        inner.set_node_context("r2", "Flex", 2)
        with inner:
            print("inner-body")
        print("outer-after")

        r2_logs = outer.get_logs("r2")["stdout"]

    assert "inner-body" in r2_logs
    assert "outer-after" not in r2_logs
    assert "outer-before" not in r2_logs
    assert "outer-before" in base_out.getvalue()
    assert "outer-after" in base_out.getvalue()
    assert "inner-body" not in base_out.getvalue()


@pytest.mark.unittest
def test_nested_node_log_manager_both_instantiated_before_enter(monkeypatch):
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    outer = NodeLogManager()
    inner = NodeLogManager()
    outer.set_node_context("r1", "Flex", 1)
    inner.set_node_context("r2", "Flex", 2)

    with outer:
        print("outer-before")
        with inner:
            print("inner-line")
        print("outer-after")

        r1_logs = outer.get_logs("r1")["stdout"]
        r2_logs = inner.get_logs("r2")["stdout"]

    assert "outer-before" in r1_logs
    assert "outer-after" in r1_logs
    assert "inner-line" in r2_logs
    assert "outer-after" not in r2_logs
    assert "inner-line" not in r1_logs
    assert "outer-before" not in r2_logs
