# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline tests. Run with --confcutdir=tests/samples/ci to avoid service fixtures."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import select_samples
from select_samples import SampleCollector, SampleTest, matches, normalize, select_tests

SYNC = SampleTest(
    "tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_mcp_with_project_connection]",
    "samples/agents/tools/sample_agent_mcp_with_project_connection.py",
    "sample_agent_mcp_with_project_connection",
)
ASYNC = SampleTest(
    "tests/samples/test_samples_async.py::TestSamplesAsync::"
    "test_agent_tools_samples_async[sample_agent_mcp_with_project_connection_async]",
    "samples/agents/tools/sample_agent_mcp_with_project_connection_async.py",
    "sample_agent_mcp_with_project_connection_async",
)
BASIC = SampleTest(
    "tests/samples/test_samples.py::TestSamples::test_agents_samples[sample_agent_basic]",
    "samples/agents/sample_agent_basic.py",
    "sample_agent_basic",
)


@pytest.mark.parametrize(
    "pattern,expected",
    [
        (SYNC.sample_path, [SYNC]),
        (r"samples\agents\tools\sample_agent_mcp*project_connection*.py", [SYNC, ASYNC]),
        ("samples/agents/tools/*project_connection_async.py", [ASYNC]),
        ("./samples/agents/tools/*project_connection.py", [SYNC]),
        ("sdk/ai/azure-ai-projects/samples/agents/tools/*project_connection.py", [SYNC]),
        ("SAMPLES/AGENTS/TOOLS/*PROJECT_CONNECTION.PY", [SYNC]),
    ],
)
def test_sample_path_wildcards(pattern, expected):
    assert select_tests([BASIC, ASYNC, SYNC], "sample-path", pattern) == expected


@pytest.mark.parametrize(
    "pattern,expected",
    [
        (SYNC.node_id, [SYNC]),
        (SYNC.test_id, [SYNC]),
        ("*test_agent_tools_samples*[*mcp*project_connection*]", [SYNC, ASYNC]),
        ("sample_agent_mcp_with_project_connection*", [SYNC, ASYNC]),
        ("*test_samples_async.py::*[sample_agent_mcp_with_project_connection_async]", [ASYNC]),
    ],
)
def test_node_and_parameter_id_wildcards(pattern, expected):
    assert select_tests([ASYNC, SYNC, BASIC], "test-id", pattern) == expected


def test_or_queries_deduplicate_and_sort():
    query = f"{SYNC.sample_path}; samples/agents/sample_agent_basic.py\n{SYNC.sample_path}"
    assert select_tests([SYNC, BASIC, SYNC], "sample-path", query) == sorted(
        [SYNC, BASIC], key=lambda test: test.node_id
    )


@pytest.mark.parametrize("query", ["", " ", ";\n;", "*does_not_exist*", "mcp or basic"])
def test_empty_or_unmatched_query_fails_closed(query):
    with pytest.raises(ValueError, match="empty query|No collected sample tests"):
        select_tests([SYNC, BASIC], "sample-path", query)


def test_unknown_selection_kind_is_rejected():
    with pytest.raises(ValueError, match="Selection kind"):
        select_tests([SYNC], "shell", "*")


def test_parameter_brackets_are_literal_not_glob_character_classes():
    assert matches("method[sample]", "method[sample]")
    assert matches("method[sample]", "method[*]")
    assert not matches("methods", "method[sample]")


def test_question_mark_matches_one_character_and_regex_is_escaped():
    assert matches("sample_a.py", "sample_?.py")
    assert not matches("sample_ab.py", "sample_?.py")
    assert not matches("sample_axpy", "sample_?.py")
    assert not matches("sample_foo.py", "sample_(foo|bar).py")


def test_normalization_preserves_pytest_brackets():
    assert normalize(r".\tests\samples\test_samples.py::Test[variant]") == (
        "tests/samples/test_samples.py::Test[variant]"
    )


def test_collector_uses_real_sample_parameter_not_test_name(tmp_path: Path):
    sample = tmp_path / SYNC.sample_path
    collector = SampleCollector(tmp_path)
    session = SimpleNamespace(
        items=[
            SimpleNamespace(
                nodeid=SYNC.node_id, callspec=SimpleNamespace(params={"sample_path": sample}, id=SYNC.test_id)
            ),
            SimpleNamespace(nodeid="test_without_sample", callspec=SimpleNamespace(params={}, id="other")),
            SimpleNamespace(nodeid="test_not_parametrized"),
            SimpleNamespace(
                nodeid="empty_parametrization", callspec=SimpleNamespace(params={"sample_path": None}, id="empty")
            ),
            SimpleNamespace(
                nodeid="outside_samples",
                callspec=SimpleNamespace(params={"sample_path": tmp_path / "outside.py"}, id="outside"),
            ),
        ]
    )
    collector.pytest_collection_finish(session)
    assert collector.tests == [SYNC]


@pytest.mark.parametrize("count", [1, 2, 3, 4, 5, 9])
@pytest.mark.parametrize("requested", [1, 2, 3, 4])
def test_round_robin_runs_every_selected_case_once(count, requested):
    tests = [SampleTest(f"node-{index}", f"sample-{index}.py", str(index)) for index in range(count)]
    queues = select_samples.partition_tests(tests, requested)
    active = min(count, requested)
    assert list(queues) == [f"q{number}" for number in range(1, active + 1)]
    for index, shard in enumerate(queues.values()):
        assert shard == tests[index::active]
        assert shard
    all_nodes = [test.node_id for shard in queues.values() for test in shard]
    assert len(all_nodes) == len(set(all_nodes)) == count
    assert max(map(len, queues.values())) - min(map(len, queues.values())) <= 1


@pytest.mark.parametrize("requested", [0, 5, -1, True, 1.5])
def test_round_robin_rejects_invalid_worker_count(requested):
    with pytest.raises(ValueError, match="one to four"):
        select_samples.partition_tests([SYNC], requested)


@pytest.mark.parametrize("tests", [[], [SYNC, SYNC]])
def test_round_robin_rejects_empty_or_duplicate_selection(tests):
    with pytest.raises(ValueError, match="nonempty.*unique"):
        select_samples.partition_tests(tests, 4)


def test_default_pair_creates_two_nonempty_shards_and_dynamic_matrix(tmp_path, monkeypatch):
    monkeypatch.setattr(select_samples, "collect_tests", lambda root: [ASYNC, SYNC])
    output = tmp_path / "plan" / "selected-tests.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "select_samples.py",
            "--selection-kind",
            "sample-path",
            "--selection",
            "*",
            "--queue-count",
            "4",
            "--output",
            str(output),
        ],
    )
    assert select_samples.main() == 0
    matrix = json.loads((output.parent / "queue-matrix.json").read_text())
    assert matrix == {"q1": {"QueueName": "q1"}, "q2": {"QueueName": "q2"}}
    manifest = json.loads(output.read_text())
    assert [test["node_id"] for test in manifest["tests"]] == [SYNC.node_id, ASYNC.node_id]
    for queue, expected in (("q1", SYNC), ("q2", ASYNC)):
        shard = json.loads((output.parent / queue / "selected-tests.json").read_text())
        assert [test["node_id"] for test in shard["tests"]] == [expected.node_id]
    assert not (output.parent / "q3").exists()
    assert not (output.parent / "q4").exists()
    with pytest.raises(SystemExit):
        select_samples.main()
    assert json.loads(output.read_text()) == manifest
