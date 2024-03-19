# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import re
import tempfile
from collections import namedtuple
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, cast

from azure.ai.ml._utils.utils import dump_yaml_to_file, get_all_data_binding_expressions, load_yaml
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR, DefaultOpenEncoding
from azure.ai.ml.constants._component import ComponentParameterTypes, IOConstants
from azure.ai.ml.exceptions import UserErrorException

if TYPE_CHECKING:
    from azure.ai.ml.entities._builders import BaseNode

ExpressionInput = namedtuple("ExpressionInput", ["name", "type", "value"])
NONE_PARAMETER_TYPE = "None"


class PipelineExpressionOperator:
    """Support operator in native Python experience."""

    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    POW = "**"
    FLOORDIV = "//"
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    EQ = "=="
    NE = "!="
    AND = "&"
    OR = "|"
    XOR = "^"


_SUPPORTED_OPERATORS = {
    getattr(PipelineExpressionOperator, attr)
    for attr in PipelineExpressionOperator.__dict__
    if not attr.startswith("__")
}


def _enumerate_operation_combination() -> Dict[str, Union[str, Exception]]:
    """Enumerate the result type of binary operations on types

    Leverages `eval` to validate operation and get its result type.

    :return: A dictionary that maps an operation to either:
      * A result type
      * An Exception
    :rtype: Dict[str, Union[str, Exception]]
    """
    res: Dict = {}
    primitive_types_values = {
        NONE_PARAMETER_TYPE: repr(None),
        ComponentParameterTypes.BOOLEAN: repr(True),
        ComponentParameterTypes.INTEGER: repr(1),
        ComponentParameterTypes.NUMBER: repr(1.0),
        ComponentParameterTypes.STRING: repr("1"),
    }
    for type1, operand1 in primitive_types_values.items():
        for type2, operand2 in primitive_types_values.items():
            for operator in _SUPPORTED_OPERATORS:
                k = f"{type1} {operator} {type2}"
                try:
                    eval_result = eval(f"{operand1} {operator} {operand2}")  # pylint: disable=eval-used # nosec
                    res[k] = IOConstants.PRIMITIVE_TYPE_2_STR[type(eval_result)]
                except TypeError:
                    error_message = (
                        f"Operator '{operator}' is not supported between instances of '{type1}' and '{type2}'."
                    )
                    res[k] = UserErrorException(message=error_message, no_personal_data_message=error_message)
    return res


# enumerate and store as a lookup table:
#   key format is "<operand1_type> <operator> <operand2_type>"
#   value can be either result type as str and UserErrorException for invalid operation
_OPERATION_RESULT_TYPE_LOOKUP = _enumerate_operation_combination()


class PipelineExpressionMixin:
    _SUPPORTED_PRIMITIVE_TYPES = (bool, int, float, str)
    _SUPPORTED_PIPELINE_INPUT_TYPES = (
        ComponentParameterTypes.BOOLEAN,
        ComponentParameterTypes.INTEGER,
        ComponentParameterTypes.NUMBER,
        ComponentParameterTypes.STRING,
    )

    def _validate_binary_operation(self, other: Any, operator: str) -> None:
        from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput

        if (
            other is not None
            and not isinstance(other, self._SUPPORTED_PRIMITIVE_TYPES)
            and not isinstance(other, (PipelineInput, NodeOutput, PipelineExpression))
        ):
            error_message = (
                f"Operator '{operator}' is not supported with {type(other)}; "
                "currently only support primitive types (None, bool, int, float and str), "
                "pipeline input, component output and expression."
            )
            raise UserErrorException(message=error_message, no_personal_data_message=error_message)

    def __add__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.ADD)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.ADD)

    def __radd__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.ADD)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.ADD)

    def __sub__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.SUB)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.SUB)

    def __rsub__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.SUB)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.SUB)

    def __mul__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.MUL)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.MUL)

    def __rmul__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.MUL)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.MUL)

    def __truediv__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.DIV)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.DIV)

    def __rtruediv__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.DIV)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.DIV)

    def __mod__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.MOD)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.MOD)

    def __rmod__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.MOD)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.MOD)

    def __pow__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.POW)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.POW)

    def __rpow__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.POW)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.POW)

    def __floordiv__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.FLOORDIV)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.FLOORDIV)

    def __rfloordiv__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.FLOORDIV)
        return PipelineExpression._from_operation(other, self, PipelineExpressionOperator.FLOORDIV)

    def __lt__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.LT)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.LT)

    def __gt__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.GT)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.GT)

    def __le__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.LTE)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.LTE)

    def __ge__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.GTE)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.GTE)

    # TODO: Bug Item number: 2883354
    def __eq__(self, other: Any) -> "PipelineExpression":  # type: ignore
        self._validate_binary_operation(other, PipelineExpressionOperator.EQ)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.EQ)

    # TODO: Bug Item number: 2883354
    def __ne__(self, other: Any) -> "PipelineExpression":  # type: ignore
        self._validate_binary_operation(other, PipelineExpressionOperator.NE)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.NE)

    def __and__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.AND)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.AND)

    def __or__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.OR)
        return PipelineExpression._from_operation(self, other, PipelineExpressionOperator.OR)

    def __xor__(self, other: Any) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.XOR)
        return PipelineExpression._from_operation(self, None, PipelineExpressionOperator.XOR)

    def __bool__(self) -> bool:  # pylint: disable=invalid-bool-returned
        """Python method that is used to implement truth value testing and the built-in operation bool().

        This method is not supported as PipelineExpressionMixin is designed to record operation history,
        while this method can only return False or True, leading to history breaks here.
        As overloadable boolean operators PEP (refer to: https://www.python.org/dev/peps/pep-0335/)
        was rejected, logical operations are also not supported.

        :return: True if not inside dsl pipeline func, raises otherwise
        :rtype: bool
        """
        from azure.ai.ml.dsl._pipeline_component_builder import _is_inside_dsl_pipeline_func

        # note: unexpected bool test always be checking if the object is None;
        # so for non-pipeline scenarios, directly return True to avoid unexpected breaking,
        # and for pipeline scenarios, will use is not None to replace bool test.
        if not _is_inside_dsl_pipeline_func():
            return True

        error_message = f"Type {type(self)} is not supported for operation bool()."
        raise UserErrorException(message=error_message, no_personal_data_message=error_message)


class PipelineExpression(PipelineExpressionMixin):
    """Pipeline expression entity.

    Use PipelineExpression to support simple and trivial parameter transformation tasks with constants
    or other parameters. Operations are recorded in this class during executions, and expected result
    will be generated for corresponding scenario.
    """

    _PIPELINE_INPUT_PREFIX = ["parent", "inputs"]
    _PIPELINE_INPUT_PATTERN = re.compile(pattern=r"parent.inputs.(?P<pipeline_input_name>[^.]+)")
    _PIPELINE_INPUT_NAME_GROUP = "pipeline_input_name"
    # AML type to Python type, for generated Python code
    _TO_PYTHON_TYPE = {
        ComponentParameterTypes.BOOLEAN: bool.__name__,
        ComponentParameterTypes.INTEGER: int.__name__,
        ComponentParameterTypes.NUMBER: float.__name__,
        ComponentParameterTypes.STRING: str.__name__,
    }

    _INDENTATION = "    "
    _IMPORT_MLDESIGNER_LINE = "from mldesigner import command_component, Output"
    _DECORATOR_LINE = "@command_component(@@decorator_parameters@@)"
    _COMPONENT_FUNC_NAME = "expression_func"
    _COMPONENT_FUNC_DECLARATION_LINE = (
        f"def {_COMPONENT_FUNC_NAME}(@@component_parameters@@)" " -> Output(type=@@return_type@@):"
    )
    _PYTHON_CACHE_FOLDER_NAME = "__pycache__"

    def __init__(self, postfix: List[str], inputs: Dict[str, ExpressionInput]):
        self._postfix = postfix
        self._inputs = inputs.copy()  # including PiplineInput and Output, extra stored name and type
        self._result_type: Optional[str] = None
        self._created_component = None

    @property
    def expression(self) -> str:
        """Infix expression string, wrapped with parentheses.

        :return: The infix expression
        :rtype: str
        """
        return self._to_infix()

    def __str__(self) -> str:
        return self._to_data_binding()

    def _data_binding(self) -> str:
        return self._to_data_binding()

    def _to_infix(self) -> str:
        stack = []
        for token in self._postfix:
            if token not in _SUPPORTED_OPERATORS:
                stack.append(token)
                continue
            operand2, operand1 = stack.pop(), stack.pop()
            stack.append(f"({operand1} {token} {operand2})")
        return stack.pop()

    # pylint: disable=too-many-statements
    @staticmethod
    def _handle_operand(
        operand: "PipelineExpression",
        postfix: List[str],
        expression_inputs: Dict[str, ExpressionInput],
        pipeline_inputs: dict,
    ) -> Tuple[List[str], Dict[str, ExpressionInput]]:
        """Handle operand in expression, update postfix expression and expression inputs.

        :param operand: The operand
        :type operand: "PipelineExpression"
        :param postfix:
        :type postfix: List[str]
        :param expression_inputs: The expression inputs
        :type expression_inputs: Dict[str, ExpressionInput]
        :param pipeline_inputs: The pipeline inputs
        :type pipeline_inputs: dict
        :return: A 2-tuple of the updated postfix expression and expression inputs
        :rtype: Tuple[List[str], Dict[str, ExpressionInput]]
        """
        from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput

        def _update_postfix(_postfix: List[str], _old_name: str, _new_name: str) -> List[str]:
            return list(map(lambda _x: _new_name if _x == _old_name else _x, _postfix))

        def _get_or_create_input_name(
            _original_name: str,
            _operand: Union[PipelineInput, NodeOutput],
            _expression_inputs: Dict[str, ExpressionInput],
        ) -> str:
            """Get or create expression input name as current operand may have appeared in expression.

            :param _original_name: The original name
            :type _original_name: str
            :param _operand: The expression operand
            :type _operand: Union[PipelineInput, NodeOutput]
            :param _expression_inputs: The expression inputs
            :type _expression_inputs: Dict[str, ExpressionInput]
            :return: The input name
            :rtype: str
            """
            _existing_id_to_name = {id(_v.value): _k for _k, _v in _expression_inputs.items()}
            if id(_operand) in _existing_id_to_name:
                return _existing_id_to_name[id(_operand)]
            # use a counter to generate a unique name for current operand
            _name, _counter = _original_name, 0
            while _name in _expression_inputs:
                _name = f"{_original_name}_{_counter}"
                _counter += 1
            return _name

        def _handle_pipeline_input(
            _pipeline_input: PipelineInput,
            _postfix: List[str],
            _expression_inputs: Dict[str, ExpressionInput],
        ) -> Tuple[List[str], dict]:
            _name = _pipeline_input._port_name
            # 1. use name with counter for pipeline input; 2. add component's name to component output
            if _name in _expression_inputs:
                _seen_input = _expression_inputs[_name]
                if isinstance(_seen_input.value, PipelineInput):
                    _name = _get_or_create_input_name(_name, _pipeline_input, _expression_inputs)
                else:
                    _expression_inputs.pop(_name)
                    _new_name = f"{_seen_input.value._owner.component.name}__{_seen_input.value._port_name}"
                    _postfix = _update_postfix(_postfix, _name, _new_name)
                    _expression_inputs[_new_name] = ExpressionInput(_new_name, _seen_input.type, _seen_input)
            _postfix.append(_name)

            param_input = pipeline_inputs
            for group_name in _pipeline_input._group_names:
                param_input = param_input[group_name].values
            _expression_inputs[_name] = ExpressionInput(
                _name, param_input[_pipeline_input._port_name].type, _pipeline_input
            )
            return _postfix, _expression_inputs

        def _handle_component_output(
            _component_output: NodeOutput,
            _postfix: List[str],
            _expression_inputs: Dict[str, ExpressionInput],
        ) -> Tuple[List[str], dict]:
            if _component_output._meta is not None and not _component_output._meta._is_primitive_type:
                error_message = (
                    f"Component output {_component_output._port_name} in expression must "
                    f"be a primitive type with value {True!r}, "
                    f"got {_component_output._meta._is_primitive_type!r}"
                )
                raise UserErrorException(message=error_message, no_personal_data_message=error_message)
            _name = _component_output._port_name
            _has_prefix = False
            # "output" is the default output name for command component, add component's name as prefix
            if _name == "output":
                if _component_output._owner is not None and not isinstance(_component_output._owner.component, str):
                    _name = f"{_component_output._owner.component.name}__output"
                _has_prefix = True
            # following loop is expected to execute at most twice:
            #   1. add component's name to output(s)
            #   2. use name with counter
            while _name in _expression_inputs:
                _seen_input = _expression_inputs[_name]
                if isinstance(_seen_input.value, PipelineInput):
                    if not _has_prefix:
                        if _component_output._owner is not None and not isinstance(
                            _component_output._owner.component, str
                        ):
                            _name = f"{_component_output._owner.component.name}__{_component_output._port_name}"
                        _has_prefix = True
                        continue
                    _name = _get_or_create_input_name(_name, _component_output, _expression_inputs)
                else:
                    if not _has_prefix:
                        _expression_inputs.pop(_name)
                        _new_name = f"{_seen_input.value._owner.component.name}__{_seen_input.value._port_name}"
                        _postfix = _update_postfix(_postfix, _name, _new_name)
                        _expression_inputs[_new_name] = ExpressionInput(_new_name, _seen_input.type, _seen_input)
                        if _component_output._owner is not None and not isinstance(
                            _component_output._owner.component, str
                        ):
                            _name = f"{_component_output._owner.component.name}__{_component_output._port_name}"
                        _has_prefix = True
                    _name = _get_or_create_input_name(_name, _component_output, _expression_inputs)
            _postfix.append(_name)
            _expression_inputs[_name] = ExpressionInput(_name, _component_output.type, _component_output)
            return _postfix, _expression_inputs

        if operand is None or isinstance(operand, PipelineExpression._SUPPORTED_PRIMITIVE_TYPES):
            postfix.append(repr(operand))
        elif isinstance(operand, PipelineInput):
            postfix, expression_inputs = _handle_pipeline_input(operand, postfix, expression_inputs)
        elif isinstance(operand, NodeOutput):
            postfix, expression_inputs = _handle_component_output(operand, postfix, expression_inputs)
        elif isinstance(operand, PipelineExpression):
            postfix.extend(operand._postfix.copy())
            expression_inputs.update(operand._inputs.copy())
        return postfix, expression_inputs

    @staticmethod
    def _from_operation(operand1: Any, operand2: Any, operator: str) -> "PipelineExpression":
        if operator not in _SUPPORTED_OPERATORS:
            error_message = (
                f"Operator '{operator}' is not supported operator, "
                f"currently supported operators are {','.join(_SUPPORTED_OPERATORS)}."
            )
            raise UserErrorException(message=error_message, no_personal_data_message=error_message)

        # get all pipeline input types from builder stack
        # TODO: check if there is pipeline input we cannot know its type (missing in `PipelineComponentBuilder.inputs`)?
        from azure.ai.ml.dsl._pipeline_component_builder import _definition_builder_stack

        res = _definition_builder_stack.top()
        pipeline_inputs = res.inputs if res is not None else {}
        postfix: List[str] = []
        inputs: Dict[str, ExpressionInput] = {}
        postfix, inputs = PipelineExpression._handle_operand(operand1, postfix, inputs, pipeline_inputs)
        postfix, inputs = PipelineExpression._handle_operand(operand2, postfix, inputs, pipeline_inputs)
        postfix.append(operator)
        return PipelineExpression(postfix, inputs)

    @property
    def _string_concatenation(self) -> bool:
        """If all operands are string and operations are addition, it is a string concatenation expression.

        :return: Whether this represents string concatenation
        :rtype: bool
        """
        for token in self._postfix:
            # operator can only be "+" for string concatenation
            if token in _SUPPORTED_OPERATORS:
                if token != PipelineExpressionOperator.ADD:
                    return False
                continue
            # constant and PiplineInput should be type string
            if token in self._inputs:
                if self._inputs[token].type != ComponentParameterTypes.STRING:
                    return False
            else:
                if not isinstance(eval(token), str):  # pylint: disable=eval-used # nosec
                    return False
        return True

    def _to_data_binding(self) -> str:
        """Convert operands to data binding and concatenate them in the order of postfix expression.

        :return: The data binding
        :rtype: str
        """
        if not self._string_concatenation:
            error_message = (
                "Only string concatenation expression is supported to convert to data binding, "
                f"current expression is '{self.expression}'."
            )
            raise UserErrorException(message=error_message, no_personal_data_message=error_message)

        stack = []
        for token in self._postfix:
            if token != PipelineExpressionOperator.ADD:
                if token in self._inputs:
                    stack.append(self._inputs[token].value._data_binding())
                else:
                    stack.append(eval(token))  # pylint: disable=eval-used # nosec
                continue
            operand2, operand1 = stack.pop(), stack.pop()
            stack.append(operand1 + operand2)
        res: str = stack.pop()
        return res

    def resolve(self) -> Union[str, "BaseNode"]:
        """Resolve expression to data binding or component, depend on the operations.

        :return: The data binding string or the component
        :rtype: Union[str, BaseNode]
        """
        if self._string_concatenation:
            return self._to_data_binding()
        return cast(Union[str, "BaseNode"], self._create_component())

    @staticmethod
    def parse_pipeline_inputs_from_data_binding(data_binding: str) -> List[str]:
        """Parse all PipelineInputs name from data binding expression.

        :param data_binding: Data binding expression
        :type data_binding: str
        :return: List of PipelineInput's name from given data binding expression
        :rtype: List[str]
        """
        pipeline_input_names = []
        for single_data_binding in get_all_data_binding_expressions(
            value=data_binding,
            binding_prefix=PipelineExpression._PIPELINE_INPUT_PREFIX,
            is_singular=False,
        ):
            m = PipelineExpression._PIPELINE_INPUT_PATTERN.match(single_data_binding)
            # `get_all_data_binding_expressions` should work as pre-filter, so no need to concern `m` is None
            if m is not None:
                pipeline_input_names.append(m.group(PipelineExpression._PIPELINE_INPUT_NAME_GROUP))
        return pipeline_input_names

    @staticmethod
    def _get_operation_result_type(type1: str, operator: str, type2: str) -> str:
        def _validate_operand_type(_type: str) -> None:
            if _type != NONE_PARAMETER_TYPE and _type not in PipelineExpression._SUPPORTED_PIPELINE_INPUT_TYPES:
                error_message = (
                    f"Pipeline input type {_type!r} is not supported in expression; "
                    f"currently only support None, "
                    + ", ".join(PipelineExpression._SUPPORTED_PIPELINE_INPUT_TYPES)
                    + "."
                )
                raise UserErrorException(message=error_message, no_personal_data_message=error_message)

        _validate_operand_type(type1)
        _validate_operand_type(type2)
        operation = f"{type1} {operator} {type2}"
        lookup_value = _OPERATION_RESULT_TYPE_LOOKUP.get(operation)
        if isinstance(lookup_value, str):
            return lookup_value  # valid operation, return result type
        _user_exception: UserErrorException = lookup_value
        raise _user_exception  # invalid operation, raise UserErrorException

    def _get_operand_type(self, operand: str) -> str:
        if operand in self._inputs:
            res: str = self._inputs[operand].type
            return res
        primitive_type = type(eval(operand))  # pylint: disable=eval-used # nosec
        res_type: str = IOConstants.PRIMITIVE_TYPE_2_STR.get(primitive_type, NONE_PARAMETER_TYPE)
        return res_type

    @property
    def _component_code(self) -> str:
        def _generate_function_code_lines() -> Tuple[List[str], str]:
            """Return lines of code and return type.

            :return: A 2-tuple of (function body, return type name)
            :rtype: Tuple[List[str], str]
            """
            _inter_id, _code, _stack = 0, [], []
            _line_recorder: Dict = {}
            for _token in self._postfix:
                if _token not in _SUPPORTED_OPERATORS:
                    _type = self._get_operand_type(_token)
                    _stack.append((_token, _type))
                    continue
                _operand2, _type2 = _stack.pop()
                _operand1, _type1 = _stack.pop()
                _current_line = f"{_operand1} {_token} {_operand2}"
                if _current_line in _line_recorder:
                    _inter_var, _inter_var_type = _line_recorder[_current_line]
                else:
                    _inter_var = f"inter_var_{_inter_id}"
                    _inter_id += 1
                    _inter_var_type = self._get_operation_result_type(_type1, _token, _type2)
                    _code.append(f"{self._INDENTATION}{_inter_var} = {_current_line}")
                    _line_recorder[_current_line] = (_inter_var, _inter_var_type)
                _stack.append((_inter_var, _inter_var_type))
            _return_var, _result_type = _stack.pop()
            _code.append(f"{self._INDENTATION}return {_return_var}")
            return _code, _result_type

        def _generate_function_decorator_and_declaration_lines(_return_type: str) -> List[str]:
            # decorator parameters
            _display_name = f'{self._INDENTATION}display_name="Expression: {self.expression}",'
            _decorator_parameters = "\n" + "\n".join([_display_name]) + "\n"
            # component parameters
            _component_parameters = []
            for _name in sorted(self._inputs):
                _type = self._TO_PYTHON_TYPE[self._inputs[_name].type]
                _component_parameters.append(f"{_name}: {_type}")
            _component_parameters_str = (
                "\n"
                + "\n".join(
                    [f"{self._INDENTATION}{_component_parameter}," for _component_parameter in _component_parameters]
                )
                + "\n"
            )
            return [
                self._IMPORT_MLDESIGNER_LINE + "\n\n",
                self._DECORATOR_LINE.replace("@@decorator_parameters@@", _decorator_parameters),
                self._COMPONENT_FUNC_DECLARATION_LINE.replace(
                    "@@component_parameters@@", _component_parameters_str
                ).replace("@@return_type@@", f'"{_return_type}"'),
            ]

        lines, result_type = _generate_function_code_lines()
        self._result_type = result_type
        code = _generate_function_decorator_and_declaration_lines(result_type) + lines
        return "\n".join(code) + "\n"

    def _create_component(self) -> Any:
        def _generate_python_file(_folder: Path) -> None:
            _folder.mkdir()
            with open(_folder / "expression_component.py", "w", encoding=DefaultOpenEncoding.WRITE) as _f:
                _f.write(self._component_code)

        def _generate_yaml_file(_path: Path) -> None:
            _data_folder = Path(__file__).parent / "data"
            # update YAML content from template and dump
            with open(_data_folder / "expression_component_template.yml", "r", encoding=DefaultOpenEncoding.READ) as _f:
                _data = load_yaml(_f)
            _data["display_name"] = f"Expression: {self.expression}"
            _data["inputs"] = {}
            _data["outputs"]["output"]["type"] = self._result_type
            _command_inputs_items = []
            for _name in sorted(self._inputs):
                _type = self._inputs[_name].type
                _data["inputs"][_name] = {"type": _type}
                _command_inputs_items.append(_name + '="${{inputs.' + _name + '}}"')
            _command_inputs_string = " ".join(_command_inputs_items)
            _command_output_string = 'output="${{outputs.output}}"'
            _command = (
                "mldesigner execute --source expression_component.py --name expression_func"
                " --inputs " + _command_inputs_string + " --outputs " + _command_output_string
            )
            _data["command"] = _data["command"].format(command_placeholder=_command)
            dump_yaml_to_file(_path, _data)

        if self._created_component is None:
            tmp_folder = Path(tempfile.mkdtemp())
            code_folder = tmp_folder / "src"
            yaml_path = tmp_folder / "component_spec.yml"
            _generate_python_file(code_folder)
            _generate_yaml_file(yaml_path)

            from azure.ai.ml import load_component

            component_func = load_component(yaml_path)
            component_kwargs = {k: v.value for k, v in self._inputs.items()}
            self._created_component = component_func(**component_kwargs)
            if self._created_component is not None:
                self._created_component.environment_variables = {AZUREML_PRIVATE_FEATURES_ENV_VAR: "true"}
        return self._created_component
