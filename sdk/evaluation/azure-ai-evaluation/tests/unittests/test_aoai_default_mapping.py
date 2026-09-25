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
from jsonschema import Draft7Validator

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


def _grader(grader_config=None):
    return AzureOpenAIGrader(
        model_config={"api_key": "unused"},
        grader_config=(
            grader_config
            if grader_config is not None
            else {
                "type": "string_check",
                "name": "compare",
                "operation": "eq",
                "input": "{{item.model_sample.output_json.donors}} {{item.model_sample.output_json.acceptors}}",
                "reference": "{{item.reference_answer.donors}} {{item.reference_answer.acceptors}}",
            }
        ),
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


@pytest.fixture(params=["unwrapped", "item-wrapped", "flat"])
def explicit_integer_boundary(request, tmp_path, aoai_boundary):
    def object_schema(properties):
        return {
            "type": "object",
            "properties": properties,
            "required": list(properties),
            "additionalProperties": True,
        }

    if request.param == "flat":
        item = {"donors": 0}
        item_schema = object_schema({"donors": {"type": "integer"}})
        expected_counts = {"donors": 0}
        prompt = "Score this count: {{item.donors}}"
    else:
        item = {
            "reference_answer": {"donors": 0, "acceptors": 2},
            "query": "Compare the two synthetic counts.",
            "_train_trajectory_id": "synthetic-row-0",
            "sample": {
                "output_text": '{"acceptors":2,"donor":0}',
                "output_json": {"acceptors": 2, "donor": 0},
            },
        }
        item_schema = object_schema(
            {
                "reference_answer": object_schema({"donors": {"type": "integer"}, "acceptors": {"type": "integer"}}),
                "query": {"type": "string"},
                "_train_trajectory_id": {"type": "string"},
                "sample": object_schema(
                    {
                        "output_text": {"type": "string"},
                        "output_json": object_schema({"acceptors": {"type": "integer"}, "donor": {"type": "integer"}}),
                    }
                ),
            }
        )
        expected_counts = {
            "reference_answer.donors": 0,
            "reference_answer.acceptors": 2,
            "sample.output_json.acceptors": 2,
            "sample.output_json.donor": 0,
        }
        prompt = "Compare {{item.reference_answer.donors}} with {{item.sample.output_json.donor}}."
    row = {"item": item} if request.param == "item-wrapped" else item
    row_snapshot = deepcopy(row)
    schema_snapshot = deepcopy(item_schema)
    data = tmp_path / "explicit-integers.jsonl"
    serialized_row = json.dumps(row) + "\n"
    data.write_text(serialized_row, encoding="utf-8")
    grader = _grader(
        {
            "type": "score_model",
            "name": "compare_counts",
            "model": "synthetic-model",
            "input": [{"role": "user", "content": prompt}],
            "range": [0, 1],
        }
    )
    captured = []
    preprocess = evaluate_module._preprocess_data

    def capture_preprocessing(*args, **kwargs):
        validated = preprocess(*args, **kwargs)
        frame = validated["input_data_df"]
        captured.append((frame, deepcopy(frame.to_dict("records"))))
        return validated

    with patch.object(evaluate_module, "_preprocess_data", side_effect=capture_preprocessing):
        _evaluate(data, {"grader": grader}, item_schema=item_schema)

    assert item_schema == schema_snapshot
    assert row == row_snapshot
    assert data.read_text(encoding="utf-8") == serialized_row
    assert len(captured) == 1
    frame, frame_snapshot = captured[0]
    assert frame.to_dict("records") == frame_snapshot
    aoai_boundary.evals.create.assert_called_once()
    aoai_boundary.evals.runs.create.assert_called_once()
    assert aoai_boundary.evals.create.call_args.kwargs["testing_criteria"] == [grader._grader_config]
    return aoai_boundary, schema_snapshot, expected_counts


def test_explicit_integer_schema_at_request_boundary(explicit_integer_boundary):
    client, expected_schema, expected_counts = explicit_integer_boundary
    schema = client.evals.create.call_args.kwargs["data_source_config"]["item_schema"]
    leaf_types = {}
    for path in expected_counts:
        leaf = schema
        for segment in path.split("."):
            leaf = leaf["properties"][segment]
        leaf_types[path] = leaf["type"]
    assert leaf_types == {path: "integer" for path in expected_counts}
    assert schema["properties"] == expected_schema["properties"]
    assert set(schema["required"]) == set(expected_schema["required"])
    assert schema["additionalProperties"] is True


def test_explicit_integer_payload_at_request_boundary(explicit_integer_boundary):
    client, _, expected_counts = explicit_integer_boundary
    content = client.evals.runs.create.call_args.kwargs["data_source"]["source"]["content"]
    assert len(content) == 1
    values = {}
    for path in expected_counts:
        value = content[0]["item"]
        for segment in path.split("."):
            value = value[segment]
        values[path] = value
    assert {path: type(value) for path, value in values.items()} == {path: int for path in expected_counts}
    assert values == expected_counts
    schema = client.evals.create.call_args.kwargs["data_source_config"]["item_schema"]
    Draft7Validator(schema).validate(content[0]["item"])


@pytest.fixture
def capture_typed_requests(tmp_path, aoai_boundary):
    def capture(rows, schema, route, mixed=False):
        data = tmp_path / "typed-rows.jsonl"
        serialized = "".join(json.dumps(row, allow_nan=False) + "\n" for row in rows)
        data.write_text(serialized, encoding="utf-8")
        kwargs = (
            {"item_schema": schema}
            if route == "item_schema"
            else {"data_source_config": {"type": "custom", "item_schema": schema}}
        )
        kwargs_snapshot = deepcopy(kwargs)
        received = []

        def python_evaluator(**kwargs):
            received.append(deepcopy(kwargs))
            return {"count": len(kwargs)}

        graders = {"grader": _grader()}
        if mixed:
            baseline = _evaluate(data, {"python": python_evaluator})
            graders["second"] = _grader(
                {
                    "type": "score_model",
                    "name": "typed_score",
                    "model": "synthetic-model",
                    "input": [{"role": "user", "content": "Score the synthetic record."}],
                    "range": [0, 1],
                }
            )
            graders["python"] = python_evaluator
        group_count = 2 if mixed else 1
        evaluate_module._get_evaluation_run_results.return_value = (
            pd.DataFrame({f"outputs.{name}.score": [0] * len(rows) for name in ("grader", "second")[:group_count]}),
            {"grader.score": 0},
        )
        captured_frames = []
        preprocess = evaluate_module._preprocess_data
        begin_aoai = evaluate_module._begin_aoai_evaluation

        def capture_preprocessing(*args, **options):
            validated = preprocess(*args, **options)
            frame = validated["input_data_df"]
            snapshot = frame.copy(deep=True)
            for column in frame:
                snapshot[column] = pd.Series(
                    deepcopy(frame[column].tolist()), index=frame.index, dtype=frame[column].dtype
                )
            captured_frames.append((frame, snapshot))
            return validated

        def capture_aoai(*args, **options):
            result = begin_aoai(*args, **options)
            # Check before callable-result processing intentionally prefixes DataFrame column names.
            for frame, snapshot in captured_frames:
                pd.testing.assert_frame_equal(frame, snapshot)
            return result

        with (
            patch.object(evaluate_module, "_preprocess_data", side_effect=capture_preprocessing),
            patch.object(evaluate_module, "_begin_aoai_evaluation", side_effect=capture_aoai),
        ):
            result = _evaluate(data, graders, **kwargs)

        assert kwargs == kwargs_snapshot
        assert data.read_text(encoding="utf-8") == serialized
        if mixed:
            # Concurrent evaluator calls can arrive in different orders; preserve values and duplicate counts.
            baseline_inputs = sorted(json.dumps(row, sort_keys=True) for row in received[: len(rows)])
            mixed_inputs = sorted(json.dumps(row, sort_keys=True) for row in received[len(rows) :])
            assert baseline_inputs == mixed_inputs
            assert [row["outputs.python.count"] for row in result["rows"]] == [
                row["outputs.python.count"] for row in baseline["rows"]
            ]
        assert aoai_boundary.evals.create.call_count == aoai_boundary.evals.runs.create.call_count == group_count
        requests = []
        for definition, run in zip(
            aoai_boundary.evals.create.call_args_list, aoai_boundary.evals.runs.create.call_args_list
        ):
            captured_schema = definition.kwargs["data_source_config"]["item_schema"]
            items = [row["item"] for row in run.kwargs["data_source"]["source"]["content"]]
            assert captured_schema == schema
            Draft7Validator.check_schema(captured_schema)
            assert len(items) == len(rows)
            requests.append((Draft7Validator(captured_schema), items))
        return requests, captured_frames[0][0]

    return capture


@pytest.fixture
def constrained_record():
    schema = {
        "type": "object",
        "properties": {
            "count": {"type": "integer", "minimum": 0, "maximum": 4, "enum": [0, 2, 4]},
            "ratio": {"type": "number", "minimum": 0, "maximum": 2},
            "flag": {"type": "boolean"},
            "text": {"type": "string", "minLength": 2, "maxLength": 4, "pattern": "^ok"},
            "empty": {"type": "null"},
            "values": {"type": "array", "items": {"type": "integer"}, "minItems": 1, "maxItems": 2},
            "empty_list": {"type": "array", "items": {"type": "integer"}},
            "metadata": {
                "type": "object",
                "properties": {"optional": {"type": "integer"}},
                "additionalProperties": False,
            },
            "details": {
                "type": "object",
                "properties": {"sibling": {"type": "integer"}, "optional": {"type": ["integer", "null"]}},
                "required": ["sibling"],
                "additionalProperties": False,
            },
        },
        "required": ["count", "ratio", "flag", "text", "empty", "values", "details"],
        "additionalProperties": False,
    }
    item = {
        "count": 0,
        "ratio": 1.5,
        "flag": False,
        "text": "ok",
        "empty": None,
        "values": [0, 2],
        "empty_list": [],
        "metadata": {},
        "details": {"sibling": 2, "optional": None},
    }
    return schema, item


@pytest.mark.parametrize("route", ["item_schema", "data_source_config"])
@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize(
    "declaration,value",
    [
        ({"type": "number", "minimum": 0}, 2),
        ({"type": "number"}, "2"),
        ({"type": "string"}, 2),
        ({"type": "integer"}, False),
        ({"type": "integer", "minimum": 0}, -1),
        ({"type": "boolean"}, False),
        ({"type": "array", "items": {"type": "integer"}}, [0, 2]),
        ({"type": "array", "items": {"type": "integer"}}, [0, False]),
        (
            {
                "type": "object",
                "properties": {"count": {"type": "integer"}, "optional": {"type": "null"}},
                "required": ["count"],
                "additionalProperties": False,
            },
            {"count": 0, "optional": None},
        ),
        ({"type": "object", "properties": {}}, {}),
    ],
)
def test_additional_properties_preserve_values_at_request_boundary(
    capture_typed_requests, route, wrapped, declaration, value
):
    schema = {
        "type": "object",
        "properties": {"label": {"type": "string"}},
        "required": ["label"],
        "additionalProperties": declaration,
    }
    row = {"label": "synthetic", "extra": value}
    snapshot = deepcopy(row)
    expected_errors = {(tuple(error.path), error.validator) for error in Draft7Validator(schema).iter_errors(row)}
    requests, _ = capture_typed_requests([{"item": row} if wrapped else row], schema, route, mixed=True)

    for validator, items in requests:
        assert items == [snapshot]
        assert type(items[0]["extra"]) is type(value)
        assert {(tuple(error.path), error.validator) for error in validator.iter_errors(items[0])} == expected_errors
    assert row == snapshot


@pytest.mark.parametrize("route", ["item_schema", "data_source_config"])
@pytest.mark.parametrize("wrapped", [False, True])
def test_additional_properties_without_named_properties_at_request_boundary(tmp_path, aoai_boundary, route, wrapped):
    schema = {"type": "object", "additionalProperties": {"type": "number", "minimum": 0}}
    snapshot = deepcopy(schema)
    row = {"count": 0, "ratio": 1.5}
    data = tmp_path / "additional-properties.jsonl"
    data.write_text(json.dumps({"item": row} if wrapped else row) + "\n", encoding="utf-8")
    kwargs = (
        {"item_schema": schema}
        if route == "item_schema"
        else {"data_source_config": {"type": "custom", "item_schema": schema}}
    )

    _evaluate(data, {"grader": _grader()}, **kwargs)

    captured_schema = aoai_boundary.evals.create.call_args.kwargs["data_source_config"]["item_schema"]
    items = [
        entry["item"] for entry in aoai_boundary.evals.runs.create.call_args.kwargs["data_source"]["source"]["content"]
    ]
    assert captured_schema.get("properties", {}) == {}
    assert captured_schema.get("required", []) == []
    assert captured_schema["additionalProperties"] == schema["additionalProperties"]
    assert items == [row]
    assert type(items[0]["count"]) is int
    assert type(items[0]["ratio"]) is float
    Draft7Validator(captured_schema).validate(items[0])
    assert schema == snapshot


@pytest.mark.parametrize("route", ["item_schema", "data_source_config"])
@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("nested", [False, True])
def test_captured_schema_validates_typed_mixed_evaluation(
    capture_typed_requests, constrained_record, route, wrapped, nested
):
    schema, first = constrained_record
    second = deepcopy(first)
    second.update(count=2, ratio=0.5, flag=True, text="okay", values=[4])
    del second["details"]["optional"]
    if nested:
        schema = {
            "type": "object",
            "properties": {"record": schema},
            "required": ["record"],
            "additionalProperties": False,
        }
        items = [{"record": first}, {"record": second}]
    else:
        # Lossy top-level null loading is outside this AOAI serialization regression's scope.
        del schema["properties"]["empty"]
        schema["required"].remove("empty")
        del first["empty"]
        del second["empty"]
        items = [first, second]
    snapshot = deepcopy(items)
    rows = [{"item": item} for item in items] if wrapped else items
    requests, _ = capture_typed_requests(rows, schema, route, mixed=True)

    for validator, actual_items in requests:
        for actual, expected in zip(actual_items, items):
            validator.validate(actual)
            assert actual == expected
            record = actual["record"] if nested else actual
            assert type(record["count"]) is int
            assert type(record["flag"]) is bool
            json.dumps(actual, allow_nan=False)
    first_payload = requests[0][1][0]
    (first_payload["record"] if nested else first_payload)["values"].append(9)
    assert requests[1][1] == snapshot
    assert items == snapshot


@pytest.mark.parametrize("route", ["item_schema", "data_source_config"])
@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize(
    "field,value,keyword",
    [
        ("count", False, "type"),
        ("count", "0", "type"),
        ("count", 1.5, "type"),
        ("count", -2, "minimum"),
        ("count", 6, "maximum"),
        ("count", 1, "enum"),
        ("ratio", True, "type"),
        ("ratio", "1.5", "type"),
        ("ratio", 3.5, "maximum"),
        ("flag", "false", "type"),
        ("text", 0, "type"),
        ("text", "o", "minLength"),
        ("text", "okay!", "maxLength"),
        ("text", "no", "pattern"),
        ("empty", "", "type"),
        ("values", [], "minItems"),
        ("values", [0, 2, 4], "maxItems"),
        ("values", [False], "type"),
        ("values", {}, "type"),
        ("details", [], "type"),
        ("details", {}, "required"),
        ("details", {"sibling": 0, "extra": 1}, "additionalProperties"),
    ],
)
def test_captured_schema_rejects_invalid_typed_values(
    capture_typed_requests, constrained_record, route, wrapped, field, value, keyword
):
    record_schema, item = constrained_record
    item[field] = value
    schema = {
        "type": "object",
        "properties": {"record": record_schema},
        "required": ["record"],
        "additionalProperties": False,
    }
    row = {"record": item}
    source_errors = list(Draft7Validator(schema).iter_errors(row))
    assert any(error.validator == keyword for error in source_errors)
    requests, _ = capture_typed_requests([{"item": row} if wrapped else row], schema, route)

    validator, items = requests[0]
    assert items == [row]
    assert type(items[0]["record"][field]) is type(value)
    errors = list(validator.iter_errors(items[0]))
    assert {(tuple(error.path), error.validator) for error in errors} == {
        (tuple(error.path), error.validator) for error in source_errors
    }


@pytest.mark.parametrize("route", ["item_schema", "data_source_config"])
@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("invalid", ["missing-required", "extra-property"])
def test_captured_schema_rejects_structural_violations(
    capture_typed_requests, constrained_record, route, wrapped, invalid
):
    schema, item = constrained_record
    schema = {"type": "object", "properties": {"record": schema}, "required": ["record"], "additionalProperties": False}
    row = {"record": item}
    if invalid == "missing-required":
        del item["count"]
        keyword = "required"
    else:
        row["extra"] = "unexpected"
        keyword = "additionalProperties"
    requests, _ = capture_typed_requests([{"item": row} if wrapped else row], schema, route)

    validator, items = requests[0]
    assert items == [row]
    assert {error.validator for error in validator.iter_errors(items[0])} == {keyword}


@pytest.mark.parametrize("route", ["item_schema", "data_source_config"])
@pytest.mark.parametrize("wrapped", [True])
@pytest.mark.parametrize("case", ["null-missing", "mixed-number", "large-integer"])
def test_multirow_loader_preserves_explicit_values(capture_typed_requests, route, wrapped, case):
    if case == "null-missing":
        items = [{"id": "a", "count": 0}, {"id": "b", "count": None}, {"id": "c"}]
        declaration = {"type": ["integer", "null"]}
    elif case == "mixed-number":
        items = [{"id": "a", "count": 0}, {"id": "b", "count": 1.5}]
        declaration = {"type": "number"}
    else:
        items = [{"id": "a", "count": 9007199254740993}, {"id": "b", "count": None}]
        declaration = {"type": ["integer", "null"], "enum": [9007199254740993, None]}
    schema = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "count": declaration},
        "required": ["id"],
        "additionalProperties": False,
    }
    for item in items:
        Draft7Validator(schema).validate(item)
    rows = [{"item": item} for item in items] if wrapped else items
    requests, frame = capture_typed_requests(rows, schema, route)
    validator, actual_items = requests[0]
    errors = [
        (index, list(error.path), error.message)
        for index, item in enumerate(actual_items)
        for error in validator.iter_errors(item)
    ]
    diagnostics = f"Before AOAI: {frame.to_dict('records')!r}; native items: {actual_items!r}"
    assert not errors, f"{errors!r}; {diagnostics}"
    assert actual_items == items, diagnostics
    for actual, expected in zip(actual_items, items):
        if "count" in expected:
            assert type(actual["count"]) is type(expected["count"]), diagnostics
        json.dumps(actual, allow_nan=False)


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
