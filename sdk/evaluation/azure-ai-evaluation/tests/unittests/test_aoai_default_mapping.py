# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import importlib
import json
import socket
from copy import deepcopy
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader
from azure.ai.evaluation._evaluate._evaluate import _complete_aoai_default_column_mapping
from azure.ai.evaluation._evaluate._evaluate_aoai import _generate_data_source_config, _get_data_source


evaluate_module = importlib.import_module("azure.ai.evaluation._evaluate._evaluate")
pytestmark = pytest.mark.unittest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def reject_connection(*args, **kwargs):
        pytest.fail("Mapping regressions must not open network connections.")

    monkeypatch.setattr(socket.socket, "connect", reject_connection)


@pytest.mark.parametrize("occupied", range(6))
def test_alias_uses_shortest_available_suffix(occupied):
    path = "outer.middle.inner.donors"
    aliases = ["donors", "inner.donors", "middle.inner.donors", path, f"{path}__1"]
    original = {
        "default": {alias: f"${{data.existing{index}}}" for index, alias in enumerate(aliases[:occupied])},
        "explicit": {"selected": "${data.reference_answer.donors}"},
    }
    snapshot = deepcopy(original)
    result = _complete_aoai_default_column_mapping(original, pd.DataFrame([{path: "2"}]))

    expected_alias = aliases[occupied] if occupied < len(aliases) else f"{path}__2"
    assert result["default"] == {**original["default"], expected_alias: f"${{data.{path}}}"}
    assert original == snapshot
    assert result["explicit"] == original["explicit"]
    assert result["explicit"] is not original["explicit"]
    assert list(result["default"])[:occupied] == aliases[:occupied]


def test_same_source_is_not_added_again_and_allocation_is_deterministic():
    mapping = {"default": {"donors": "${data.reference.donors}", "selected": "${data.already.donors}"}}
    columns = ["reference.donors", "already.donors", "z.output.donors", "a.output.donors"]
    frame = pd.DataFrame([["0", "1", "2", "3"]], columns=columns)
    expected = {
        "default": {
            **mapping["default"],
            "output.donors": "${data.a.output.donors}",
            "z.output.donors": "${data.z.output.donors}",
        }
    }
    assert _complete_aoai_default_column_mapping(mapping, frame) == expected
    assert _complete_aoai_default_column_mapping(mapping, frame[columns[::-1]]) == expected
    assert _complete_aoai_default_column_mapping(expected, frame) == expected


@pytest.mark.parametrize("target_source", ["${target.donors}", "${run.outputs.donors}", "${data.__outputs.donors}"])
def test_target_precedence_and_flat_mappings_are_unchanged(target_source):
    mapping = {"default": {"donors": target_source, "query": "${data.query}"}}
    frame = pd.DataFrame([{"query": "test", "donors": "1", "input.donors": "0", "__outputs.donors": "2"}])
    result = _complete_aoai_default_column_mapping(mapping, frame)
    assert result == {"default": {**mapping["default"], "input.donors": "${data.input.donors}"}}
    flat = {"default": {"renamed": "${data.query}"}}
    assert _complete_aoai_default_column_mapping(flat, pd.DataFrame([{"query": "test"}])) == flat


def test_wrapped_input_does_not_replace_target_at_same_destination():
    mapping = {"default": {"renamed": "${run.outputs.generated.donors}"}}
    frame = pd.DataFrame([{"item.donors": "0", "item.reference.donors": "1", "__outputs.generated.donors": "2"}])
    result = _complete_aoai_default_column_mapping(mapping, frame)
    assert result == {"default": {**mapping["default"], "donors": "${data.item.reference.donors}"}}


@pytest.mark.parametrize("wrapper_position", range(4))
def test_wrapper_mapping_does_not_shift_leaf_types(wrapper_position):
    row = {"donors": "0", "values": ["1", "2"], "metadata": {"key": "value"}}
    frame = pd.DataFrame([{"item": row, **{f"item.{key}": value for key, value in row.items()}}])
    entries = [(key, f"${{data.item.{key}}}") for key in row]
    entries.insert(wrapper_position, ("item", "${data.item}"))
    mapping = dict(entries)

    schema = _generate_data_source_config(frame, mapping)["item_schema"]
    assert schema["properties"] == {
        "donors": {"type": "string"},
        "values": {"type": "array"},
        "metadata": {"type": "object"},
    }
    assert _get_data_source(frame, mapping)["source"]["content"] == [{"item": row}]


@pytest.fixture
def aoai_boundary(monkeypatch):
    """Replace only remote boundaries; preprocessing, schema and run payload generation stay real."""
    client = Mock()
    client.evals.create.return_value = Mock(id="group-id", testing_criteria=[Mock(id="criterion-id")])
    client.evals.runs.create.return_value = Mock(id="run-id")
    monkeypatch.setattr(AzureOpenAIGrader, "get_client", lambda self: client)
    monkeypatch.setattr(
        evaluate_module,
        "_get_evaluation_run_results",
        Mock(return_value=(pd.DataFrame({"outputs.grader.score": [0]}), {"grader.score": 0})),
    )
    # CodeClient does not provide run summaries.
    monkeypatch.setattr(evaluate_module, "_print_summary", Mock())
    return client


def _grader():
    return AzureOpenAIGrader(
        model_config={"api_key": "unused"},
        grader_config={
            "type": "string_check",
            "name": "compare",
            "operation": "eq",
            "input": "{{item.model_sample.output_json.donors}} {{item.model_sample.output_json.acceptors}}",
            "reference": "{{item.reference_answer.donors}} {{item.reference_answer.acceptors}}",
        },
    )


def _write_row(tmp_path, wrapped=False, reverse=False):
    row = {
        "reference_answer": {"donors": "0", "acceptors": "2"},
        "_loom_trajectory_id": "validation-step-000000:0",
        "query": "test query",
        "model_sample": {
            "output_text": '{"acceptors":"1","donors":"2"}',
            "output_json": {"acceptors": "1", "donors": "2"},
        },
    }
    if reverse:
        row = dict(reversed(list(row.items())))
        row["reference_answer"] = dict(reversed(list(row["reference_answer"].items())))
        row["model_sample"]["output_json"] = dict(reversed(list(row["model_sample"]["output_json"].items())))
    if wrapped:
        row = {"item": row}
    data = tmp_path / "data.jsonl"
    data.write_text(json.dumps(row) + "\n", encoding="utf-8")
    return data


def _evaluate(data, graders, **kwargs):
    return evaluate_module._evaluate(
        data=data,
        evaluators_and_graders=graders,
        _use_run_submitter_client=False,
        _use_pf_client=False,
        **kwargs,
    )


@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("reverse", [False, True])
def test_preprocessing_preserves_both_references_at_request_boundary(tmp_path, aoai_boundary, wrapped, reverse):
    grader = _grader()
    with patch.object(evaluate_module, "_begin_aoai_evaluation", wraps=evaluate_module._begin_aoai_evaluation) as begin:
        result = _evaluate(_write_row(tmp_path, wrapped, reverse), {"grader": grader})

    aoai_boundary.evals.create.assert_called_once()
    aoai_boundary.evals.runs.create.assert_called_once()
    group = aoai_boundary.evals.create.call_args.kwargs
    assert group["testing_criteria"] == [grader._grader_config]
    schema = group["data_source_config"]["item_schema"]
    content = aoai_boundary.evals.runs.create.call_args.kwargs["data_source"]["source"]["content"]
    assert len(content) == 1
    item = content[0]["item"]
    expected = {
        "reference_answer.donors": "0",
        "reference_answer.acceptors": "2",
        "model_sample.output_json.donors": "2",
        "model_sample.output_json.acceptors": "1",
    }
    for path, value in expected.items():
        leaf_schema, leaf_value = schema, item
        for segment in path.split("."):
            leaf_schema = leaf_schema["properties"][segment]
            leaf_value = leaf_value[segment]
        assert leaf_schema == {"type": "string"}
        assert leaf_value == value
        source_path = f"item.{path}" if wrapped else path
        assert f"${{data.{source_path}}}" in begin.call_args.args[1]["default"].values()
    assert result["oai_eval_run_ids"] == [{"eval_group_id": "group-id", "eval_run_id": "run-id"}]
    run_info = evaluate_module._get_evaluation_run_results.call_args.args[0][0]
    assert run_info["grader_name_map"] == {"criterion-id": "grader"}


@pytest.mark.parametrize("scope", ["default", "grader"])
def test_explicit_mapping_selection_is_unchanged(tmp_path, aoai_boundary, scope):
    config = {scope: {"column_mapping": {"selected": "${data.reference_answer.donors}", "query": "${data.query}"}}}
    snapshot = deepcopy(config)
    captured = []
    preprocess = evaluate_module._preprocess_data

    def capture_preprocessing(*args, **kwargs):
        validated = preprocess(*args, **kwargs)
        captured.append(deepcopy(validated["column_mapping"]))
        return validated

    with (
        patch.object(evaluate_module, "_preprocess_data", side_effect=capture_preprocessing),
        patch.object(evaluate_module, "_begin_aoai_evaluation", wraps=evaluate_module._begin_aoai_evaluation) as begin,
    ):
        _evaluate(_write_row(tmp_path), {"grader": _grader()}, evaluator_config=config)

    assert config == snapshot
    for alias, source in captured[0][scope].items():
        assert begin.call_args.args[1][scope][alias] == source
    schema = aoai_boundary.evals.create.call_args.kwargs["data_source_config"]["item_schema"]
    if scope == "grader":
        assert begin.call_args.args[1][scope] == captured[0][scope]
        assert set(schema["properties"]) == {"reference_answer", "query"}
        assert set(schema["properties"]["reference_answer"]["properties"]) == {"donors"}
    else:
        for branch in [
            schema["properties"]["reference_answer"],
            schema["properties"]["model_sample"]["properties"]["output_json"],
        ]:
            assert set(branch["properties"]) == {"donors", "acceptors"}


@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("explicit_target", [False, True])
def test_target_output_mapping_survives_preprocessing(tmp_path, aoai_boundary, wrapped, explicit_target):
    def target(**kwargs):
        return {"donors": "9"}

    def apply_target(target, data, batch_client, initial_data, *args, **kwargs):
        return initial_data.assign(**{"__outputs.donors": target()["donors"]}), {"donors"}, None

    config = {"default": {"column_mapping": {"generated": "${target.donors}"}}} if explicit_target else None
    snapshot = deepcopy(config)
    with (
        patch.object(evaluate_module, "_apply_target_to_data", side_effect=apply_target),
        patch.object(evaluate_module, "_begin_aoai_evaluation", wraps=evaluate_module._begin_aoai_evaluation) as begin,
    ):
        _evaluate(_write_row(tmp_path, wrapped), {"grader": _grader()}, target=target, evaluator_config=config)

    mapping = begin.call_args.args[1]["default"]
    assert mapping["donors"] == "${data.__outputs.donors}"
    assert config == snapshot
    item = aoai_boundary.evals.runs.create.call_args.kwargs["data_source"]["source"]["content"][0]["item"]
    assert item["__outputs"]["donors"] == "9"
    assert item["reference_answer"]["donors"] == "0"
    assert item["model_sample"]["output_json"]["donors"] == "2"
    if explicit_target:
        assert mapping["generated"] == "${run.outputs.donors}"
        assert item["donors"] == "9"


@pytest.mark.parametrize("wrapped", [False, True])
def test_mixed_evaluation_retains_python_mapping_and_kwargs(tmp_path, aoai_boundary, wrapped):
    data = _write_row(tmp_path, wrapped)

    def python_evaluator(**kwargs):
        return {"kwargs": kwargs}

    baseline = _evaluate(data, {"python": python_evaluator})
    captured = []
    preprocess = evaluate_module._preprocess_data

    def capture_preprocessing(*args, **kwargs):
        validated = preprocess(*args, **kwargs)
        captured.append(deepcopy(validated["column_mapping"]))
        return validated

    with (
        patch.object(evaluate_module, "_preprocess_data", side_effect=capture_preprocessing),
        patch.object(evaluate_module, "_begin_aoai_evaluation", wraps=evaluate_module._begin_aoai_evaluation) as begin,
        patch.object(
            evaluate_module, "_run_callable_evaluators", wraps=evaluate_module._run_callable_evaluators
        ) as run,
    ):
        result = _evaluate(data, {"grader": _grader(), "python": python_evaluator})

    local_mapping = run.call_args.kwargs["validated_data"]["column_mapping"]
    remote_mapping = begin.call_args.args[1]
    assert local_mapping == captured[0]
    assert remote_mapping is not local_mapping
    assert len(remote_mapping["default"]) == len(local_mapping["default"]) + 2
    for alias, source in local_mapping["default"].items():
        assert remote_mapping["default"][alias] == source
    assert result["rows"][0]["outputs.python.kwargs"] == baseline["rows"][0]["outputs.python.kwargs"]


def _write_mutable_row(tmp_path, wrapped, value):
    row = {
        "reference": {"donors": 0, "details": [{"values": [None, 1]}]},
        "model": {"donors": value, "details": [{"values": [None, 2]}]},
    }
    if wrapped:
        row = {"item": row}
    data = tmp_path / "mutable.jsonl"
    data.write_text(json.dumps(row) + "\n", encoding="utf-8")
    return data


def _mutable_grader():
    return AzureOpenAIGrader(
        model_config={"api_key": "unused"},
        grader_config={
            "type": "string_check",
            "name": "compare",
            "operation": "eq",
            "input": "{{item.model.donors}}",
            "reference": "{{item.reference.donors}}",
        },
    )


@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("value", [2, None])
def test_serialization_preserves_mutable_input(tmp_path, wrapped, value):
    validated = evaluate_module._preprocess_data(
        data=_write_mutable_row(tmp_path, wrapped, value),
        evaluators_and_graders={"grader": _mutable_grader()},
        _use_run_submitter_client=False,
        _use_pf_client=False,
    )
    frame = validated["input_data_df"]
    snapshot = deepcopy(frame.to_dict("records"))
    mapping = _complete_aoai_default_column_mapping(validated["column_mapping"], frame)["default"]

    item = _get_data_source(frame, mapping)["source"]["content"][0]["item"]

    assert frame.to_dict("records") == snapshot
    assert item["model"]["donors"] == ("" if value is None else str(value))
    assert item["model"]["details"] == [{"values": [None, 2]}]
    item["model"]["details"][0]["values"].append("payload-only")
    assert frame.to_dict("records") == snapshot


@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("value", [2, None])
def test_mixed_evaluation_preserves_mutable_python_input(tmp_path, aoai_boundary, wrapped, value):
    data = _write_mutable_row(tmp_path, wrapped, value)
    received = []

    def python_evaluator(**kwargs):
        received.append(deepcopy(kwargs))
        root = kwargs["item"] if wrapped else kwargs
        return {
            "model_type": type(root["model"]["donors"]).__name__,
            "model_value": root["model"]["donors"],
        }

    baseline = _evaluate(data, {"python": python_evaluator})
    result = _evaluate(data, {"grader": _mutable_grader(), "python": python_evaluator})

    assert received[1] == received[0]
    for field in ("model_type", "model_value"):
        key = f"outputs.python.{field}"
        assert result["rows"][0][key] == baseline["rows"][0][key]
    assert result["rows"][0]["outputs.python.model_type"] == type(value).__name__
    assert result["rows"][0]["outputs.python.model_value"] == value
    item = aoai_boundary.evals.runs.create.call_args.kwargs["data_source"]["source"]["content"][0]["item"]
    assert item["model"]["donors"] == ("" if value is None else str(value))


@pytest.mark.parametrize("source", ["mapped", "unmapped", "target"])
@pytest.mark.parametrize("container", ["list", "dict"])
def test_serialized_containers_do_not_alias_input(source, container):
    nested = [{"values": [None, 2]}]
    value = nested if container == "list" else {"nested": nested}
    column = "__outputs.structured" if source == "target" else "structured"
    frame = pd.DataFrame([{column: value}])
    snapshot = deepcopy(value)
    mapping = {}
    if source != "unmapped":
        mapping["structured"] = "${run.outputs.structured}" if source == "target" else "${data.structured}"

    item = _get_data_source(frame, mapping)["source"]["content"][0]["item"]
    payload = item["structured"]
    assert payload == snapshot
    assert payload is not value
    payload_nested = payload if container == "list" else payload["nested"]
    assert payload_nested is not nested
    assert payload_nested[0] is not nested[0]
    assert payload_nested[0]["values"] is not nested[0]["values"]
    payload_nested[0]["values"].append("payload-only")
    assert value == snapshot
    assert frame.at[0, column] == snapshot
