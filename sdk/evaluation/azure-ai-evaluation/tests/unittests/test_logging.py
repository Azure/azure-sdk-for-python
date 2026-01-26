import sys
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
def test_nested_node_log_manager_does_not_recurse(monkeypatch):
    base_out = StringIO()
    base_err = StringIO()
    monkeypatch.setattr(sys, "stdout", base_out)
    monkeypatch.setattr(sys, "stderr", base_err)
    monkeypatch.setattr(sys, "__stdout__", base_out)
    monkeypatch.setattr(sys, "__stderr__", base_err)

    with NodeLogManager():
        with NodeLogManager():
            print("nested")
            sys.stderr.write("stderr")

    assert "nested" in base_out.getvalue()
    assert "stderr" in base_err.getvalue()
