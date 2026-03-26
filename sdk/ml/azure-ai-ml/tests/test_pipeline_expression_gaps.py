import pytest
from types import SimpleNamespace

from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR
from azure.ai.ml.constants._component import ComponentParameterTypes
from azure.ai.ml.entities._job.pipeline._pipeline_expression import (
    ExpressionInput,
    PipelineExpression,
    PipelineExpressionOperator,
)
from azure.ai.ml.exceptions import UserErrorException


class _DummyBindingValue:
    def __init__(self, binding):
        self._binding = binding

    def _data_binding(self):
        return self._binding


def test_string_concatenation_data_binding_generation():
    expression = PipelineExpression([
        "'hello'",
        "'world'",
        PipelineExpressionOperator.ADD,
    ], {})
    assert expression._to_data_binding() == "helloworld"


def test_to_data_binding_rejects_non_add_operator():
    expression = PipelineExpression([
        "'a'",
        "'b'",
        PipelineExpressionOperator.SUB,
    ], {})
    with pytest.raises(UserErrorException) as excinfo:
        expression._to_data_binding()
    assert "Only string concatenation expression is supported to convert to data binding" in str(
        excinfo.value
    )
    assert "('a' - 'b')" in str(excinfo.value)


def test_to_data_binding_rejects_non_string_pipeline_input():
    binding_value = _DummyBindingValue("${{parent.inputs.bad_input}}")
    inputs = {
        "bad_input": ExpressionInput(
            "bad_input",
            ComponentParameterTypes.INTEGER,
            binding_value,
        ),
    }
    expression = PipelineExpression([
        "bad_input",
        "'unit'",
        PipelineExpressionOperator.ADD,
    ], inputs)
    with pytest.raises(UserErrorException) as excinfo:
        expression._to_data_binding()
    assert "Only string concatenation expression is supported to convert to data binding" in str(
        excinfo.value
    )


def test_parse_pipeline_inputs_from_data_binding_returns_names():
    data_binding = "prefix ${{parent.inputs.first}} and ${{parent.inputs.second}} suffix"
    assert PipelineExpression.parse_pipeline_inputs_from_data_binding(data_binding) == [
        "first",
        "second",
    ]


def test_get_operation_result_type_rejects_invalid_operand_type():
    with pytest.raises(UserErrorException) as excinfo:
        PipelineExpression._get_operation_result_type(
            "unsupported",
            PipelineExpressionOperator.ADD,
            ComponentParameterTypes.STRING,
        )
    assert "Pipeline input type 'unsupported' is not supported in expression" in str(
        excinfo.value
    )


def test_get_operation_result_type_propagates_invalid_operation():
    with pytest.raises(UserErrorException) as excinfo:
        PipelineExpression._get_operation_result_type(
            ComponentParameterTypes.STRING,
            PipelineExpressionOperator.SUB,
            ComponentParameterTypes.STRING,
        )
    assert "Operator '-' is not supported between instances of" in str(excinfo.value)


def test_parse_pipeline_inputs_from_data_binding_extracts_names():
    data_binding = "${{parent.inputs.alpha}}-${{parent.inputs.beta}}"
    assert PipelineExpression.parse_pipeline_inputs_from_data_binding(data_binding) == ["alpha", "beta"]


def test_get_operation_result_type_returns_the_result_for_supported_types():
    result = PipelineExpression._get_operation_result_type(
        ComponentParameterTypes.INTEGER,
        PipelineExpressionOperator.ADD,
        ComponentParameterTypes.INTEGER,
    )
    assert result == ComponentParameterTypes.INTEGER


def test_get_operation_result_type_rejects_non_supported_operand_type():
    with pytest.raises(UserErrorException) as excinfo:
        PipelineExpression._get_operation_result_type(
            "UnsupportedType",
            PipelineExpressionOperator.ADD,
            ComponentParameterTypes.INTEGER,
        )
    assert "Pipeline input type 'UnsupportedType' is not supported in expression" in str(
        excinfo.value
    )


def test_get_operation_result_type_invalid_operation_raises_user_error():
    with pytest.raises(UserErrorException) as excinfo:
        PipelineExpression._get_operation_result_type(
            ComponentParameterTypes.STRING,
            PipelineExpressionOperator.SUB,
            ComponentParameterTypes.STRING,
        )
    assert "Operator '-' is not supported between instances of 'string' and 'string'." in str(excinfo.value)


def test_string_concatenation_rejects_non_add_operator():
    left = ExpressionInput(
        'left',
        ComponentParameterTypes.STRING,
        SimpleNamespace(_data_binding=lambda: 'left_value'),
    )
    right = ExpressionInput(
        'right',
        ComponentParameterTypes.STRING,
        SimpleNamespace(_data_binding=lambda: 'right_value'),
    )
    expression = PipelineExpression(['left', 'right', PipelineExpressionOperator.SUB], {'left': left, 'right': right})
    assert expression._string_concatenation is False


def test_string_concatenation_rejects_non_string_input():
    expression = PipelineExpression(
        ['count'],
        {
            'count': ExpressionInput('count', ComponentParameterTypes.INTEGER, object()),
        },
    )
    assert expression._string_concatenation is False


def test_string_concatenation_rejects_non_string_constant():
    expression = PipelineExpression(['1', '2', PipelineExpressionOperator.ADD], {})
    assert expression._string_concatenation is False


def test_to_data_binding_raises_when_not_string_concatenation():
    left = ExpressionInput(
        'left',
        ComponentParameterTypes.STRING,
        SimpleNamespace(_data_binding=lambda: 'left_value'),
    )
    right = ExpressionInput(
        'right',
        ComponentParameterTypes.STRING,
        SimpleNamespace(_data_binding=lambda: 'right_value'),
    )
    expression = PipelineExpression(['left', 'right', PipelineExpressionOperator.SUB], {'left': left, 'right': right})
    with pytest.raises(UserErrorException) as excinfo:
        expression._to_data_binding()
    expected_message = (
        'Only string concatenation expression is supported to convert to data binding, '
        f"current expression is '{expression.expression}'."
    )
    assert excinfo.value.message == expected_message


def test_to_data_binding_concatenates_string_inputs():
    first = ExpressionInput(
        'first',
        ComponentParameterTypes.STRING,
        SimpleNamespace(_data_binding=lambda: 'hello'),
    )
    second = ExpressionInput(
        'second',
        ComponentParameterTypes.STRING,
        SimpleNamespace(_data_binding=lambda: 'world'),
    )
    expression = PipelineExpression(['first', 'second', PipelineExpressionOperator.ADD], {'first': first, 'second': second})
    assert expression._to_data_binding() == 'helloworld'


def test_component_code_reuses_cached_lines():
    inputs = {
        "a": ExpressionInput("a", ComponentParameterTypes.STRING, SimpleNamespace()),
        "b": ExpressionInput("b", ComponentParameterTypes.STRING, SimpleNamespace()),
    }
    expression = PipelineExpression(["a", "b", "+", "a", "b", "+", "+"], inputs)
    code = expression._component_code
    assert "inter_var_0 = a + b" in code
    assert code.count("inter_var_0 = a + b") == 1
    assert "inter_var_1 = inter_var_0 + inter_var_0" in code
    assert "return inter_var_1" in code
    assert "@command_component(" in code
    assert '"string"' in code


def test_create_component_sets_environment(monkeypatch):
    inputs = {
        "a": ExpressionInput("a", ComponentParameterTypes.STRING, "alpha"),
        "b": ExpressionInput("b", ComponentParameterTypes.STRING, "beta"),
    }
    expression = PipelineExpression(["a", "b", "+"], inputs)
    captured_kwargs = {}

    def dummy_component(**kwargs):
        captured_kwargs.update(kwargs)
        return SimpleNamespace(environment_variables=None)

    def dummy_load_component(path):
        return dummy_component

    monkeypatch.setattr("azure.ai.ml.load_component", dummy_load_component)
    component = expression._create_component()
    assert captured_kwargs == {"a": "alpha", "b": "beta"}
    assert component.environment_variables == {AZUREML_PRIVATE_FEATURES_ENV_VAR: "true"}
    assert expression._create_component() is component


def test_operation_result_type_valid_and_invalid():
    assert PipelineExpression._get_operation_result_type(
        ComponentParameterTypes.STRING,
        PipelineExpressionOperator.ADD,
        ComponentParameterTypes.STRING,
    ) == ComponentParameterTypes.STRING

    with pytest.raises(UserErrorException) as exc_info:
        PipelineExpression._get_operation_result_type(
            ComponentParameterTypes.STRING,
            PipelineExpressionOperator.SUB,
            ComponentParameterTypes.STRING,
        )
    assert "Operator" in str(exc_info.value)


def test_operand_type_prefers_expression_inputs_then_primitives():
    inputs = {
        "alpha": ExpressionInput("alpha", ComponentParameterTypes.INTEGER, object()),
    }
    expression = PipelineExpression([], inputs)
    assert expression._get_operand_type("alpha") == ComponentParameterTypes.INTEGER
    assert expression._get_operand_type("True") == ComponentParameterTypes.BOOLEAN


def test_component_code_reuses_cached_operations_and_decorator_format():
    postfix = ["a", "b", "+", "a", "b", "+", "+"]
    inputs = {
        "a": ExpressionInput("a", ComponentParameterTypes.NUMBER, object()),
        "b": ExpressionInput("b", ComponentParameterTypes.NUMBER, object()),
    }
    expression = PipelineExpression(postfix, inputs)
    code = expression._component_code

    assert "    inter_var_0 = a + b" in code
    assert code.count("    inter_var_0 = a + b") == 1
    assert "    inter_var_1 = inter_var_0 + inter_var_0" in code
    assert 'display_name="Expression: ((a + b) + (a + b))",' in code
    assert 'Output(type="number")' in code
    assert "    a: float," in code
    assert "    b: float," in code
    assert expression._result_type == ComponentParameterTypes.NUMBER
