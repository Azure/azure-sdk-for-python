import pytest
import copy
from unittest.mock import MagicMock, patch
from azure.ai.evaluation._evaluate._evaluate_aoai import _combine_item_schemas, _get_single_run_results
from azure.ai.evaluation._exceptions import ErrorBlame, EvaluationException


@pytest.fixture
def default_data_source_config():
    return {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["id", "text"],
        },
        "include_sample_schema": False,
    }


class TestCombineItemSchemas:
    """Unit tests for _combine_item_schemas"""

    @pytest.mark.parametrize("required", [None, [], ["id"]])
    @pytest.mark.parametrize("additional_properties", [True, False, {"type": "number"}])
    def test_explicit_subtrees_override_inference_without_mutation(
        self, default_data_source_config, required, additional_properties
    ):
        config = copy.deepcopy(default_data_source_config)
        inferred_schema = config["item_schema"]
        inferred_snapshot = copy.deepcopy(inferred_schema)
        schema = {
            "type": "object",
            "properties": {
                "id": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "minimum": 0, "maximum": 2, "enum": [0, 2]},
                        "values": {"type": "array", "items": {"type": "number"}, "minItems": 1},
                    },
                    "required": ["count"],
                    "additionalProperties": False,
                }
            },
            "additionalProperties": additional_properties,
        }
        if required is not None:
            schema["required"] = required
        snapshot = copy.deepcopy(schema)

        _combine_item_schemas(config, {"item_schema": schema})

        combined = config["item_schema"]
        assert combined["properties"]["id"] == schema["properties"]["id"]
        if additional_properties is True:
            assert combined["properties"]["text"] == {"type": "string"}
            assert combined["required"] == ["text"] + (required or [])
            combined["properties"]["text"]["type"] = "integer"
        else:
            assert set(combined["properties"]) == {"id"}
            assert combined["required"] == (required or [])
        assert combined["additionalProperties"] == additional_properties
        combined["properties"]["id"]["properties"]["count"]["enum"].append(3)
        assert schema == snapshot
        assert inferred_schema == inferred_snapshot

    def test_combine_item_schemas_success(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)
        kwargs = {
            "item_schema": {
                "properties": {
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": ["metadata"],
            }
        }
        _combine_item_schemas(data_source_config, kwargs)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
            "metadata": {"type": "object"},
            "timestamp": {"type": "string", "format": "date-time"},
        }
        expected_required = ["id", "text", "metadata"]
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

    def test_combine_item_schemas_without_item_schema(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
        }
        expected_required = ["id", "text"]

        # No "item_schema" in kwargs
        kwargs = {}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

        # "item_schema" as None in kwargs
        kwargs = {"item_schema": None}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

        # "item_schema" is a wrong value in kwargs
        kwargs = {"item_schema": 12345}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

        # "item_schema" without "properties" in kwargs
        kwargs = {"item_schema": {}}
        _combine_item_schemas(data_source_config, kwargs)
        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

    def test_combine_item_schemas_with_empty_external_properties(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)
        kwargs = {
            "item_schema": {
                "properties": {},
                "required": [],
            }
        }
        _combine_item_schemas(data_source_config, kwargs)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
        }
        expected_required = ["id", "text"]

        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required

    def test_combine_item_schemas_with_external_properties_without_required(self, default_data_source_config):
        data_source_config = copy.deepcopy(default_data_source_config)
        kwargs = {
            "item_schema": {
                "properties": {
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
            }
        }
        _combine_item_schemas(data_source_config, kwargs)

        expected_properties = {
            "id": {"type": "string"},
            "text": {"type": "string"},
            "metadata": {"type": "object"},
            "timestamp": {"type": "string", "format": "date-time"},
        }
        expected_required = ["id", "text"]

        assert data_source_config["item_schema"]["properties"] == expected_properties
        assert data_source_config["item_schema"]["required"] == expected_required


class TestGetSingleRunResultsBlame:
    """Unit tests for blame attribution in _get_single_run_results."""

    def _make_run_info(self, client):
        return {
            "client": client,
            "eval_group_id": "group-1",
            "eval_run_id": "run-1",
            "grader_name_map": {},
        }

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion")
    @pytest.mark.parametrize("code", ["UserError", "usererror", "USERERROR", "uSeReRrOr"])
    def test_user_error_code_sets_user_blame(self, mock_wait, code):
        """When run fails with error.code matching 'usererror' (case-insensitive), blame should be USER_ERROR."""
        run_result = MagicMock()
        run_result.status = "failed"
        run_result.error.code = code
        mock_wait.return_value = run_result
        client = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            _get_single_run_results(self._make_run_info(client))

        assert exc_info.value.blame == ErrorBlame.USER_ERROR

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion")
    def test_non_user_error_code_sets_unknown_blame(self, mock_wait):
        """When run fails with a non-UserError code, blame should be UNKNOWN."""
        run_result = MagicMock()
        run_result.status = "failed"
        run_result.error.code = "SystemError"
        mock_wait.return_value = run_result
        client = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            _get_single_run_results(self._make_run_info(client))

        assert exc_info.value.blame == ErrorBlame.UNKNOWN

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion")
    def test_missing_error_attribute_sets_unknown_blame(self, mock_wait):
        """When run fails and error attribute is absent, blame should be UNKNOWN."""
        run_result = MagicMock(spec=["status"])
        run_result.status = "failed"
        mock_wait.return_value = run_result
        client = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            _get_single_run_results(self._make_run_info(client))

        assert exc_info.value.blame == ErrorBlame.UNKNOWN

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion")
    def test_error_present_but_code_missing_sets_unknown_blame(self, mock_wait):
        """When error object exists but has no code attribute, blame should be UNKNOWN."""
        run_result = MagicMock()
        run_result.status = "failed"
        run_result.error = MagicMock(spec=[])  # error object without 'code'
        mock_wait.return_value = run_result
        client = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            _get_single_run_results(self._make_run_info(client))

        assert exc_info.value.blame == ErrorBlame.UNKNOWN

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion")
    def test_error_is_none_sets_unknown_blame(self, mock_wait):
        """When error attribute is None, blame should be UNKNOWN."""
        run_result = MagicMock()
        run_result.status = "failed"
        run_result.error = None
        mock_wait.return_value = run_result
        client = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            _get_single_run_results(self._make_run_info(client))

        assert exc_info.value.blame == ErrorBlame.UNKNOWN
