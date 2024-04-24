# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Callable, List, Mapping

from azure.ai.ml.dsl._dynamic import KwParameter, create_kw_function_from_parameters
from azure.ai.ml.entities import Component as ComponentEntity
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._component.datatransfer_component import DataTransferImportComponent


def get_dynamic_input_parameter(inputs: Mapping) -> List:
    """Return the dynamic parameter of the definition's input ports.

    :param inputs: The mapping of input names to input objects.
    :type inputs: Mapping
    :return: The list of dynamic parameters.
    :rtype: List[~azure.ai.ml.dsl._dynamic.KwParameter]
    """
    return [
        KwParameter(
            name=name,
            annotation=input._get_python_builtin_type_str(),
            default=None,
            _type=input._get_python_builtin_type_str(),
        )
        for name, input in inputs.items()
    ]


def get_dynamic_source_parameter(source: Any) -> List:
    """Return the dynamic parameter of the definition's source port.

    :param source: The source object.
    :type source: Any
    :return: The list of dynamic parameters.
    :rtype: List[~azure.ai.ml.dsl._dynamic.KwParameter]
    """
    return [
        KwParameter(
            name="source",
            annotation=source.type,
            default=None,
            _type=source.type,
        )
    ]


def to_component_func(entity: ComponentEntity, component_creation_func: Callable) -> Callable[..., Command]:
    """Convert a ComponentEntity to a callable component function.

    :param entity: The ComponentEntity to convert.
    :type entity: ~azure.ai.ml.entities.Component
    :param component_creation_func: The function for creating a component.
    :type component_creation_func: Callable
    :return: The callable component function.
    :rtype: Callable[..., ~azure.ai.ml.entities._builders.Command]
    """
    func_name = "[component] {}".format(entity.display_name)

    func_docstring_lines = []
    if entity.description is not None:
        func_docstring_lines.append(entity.description.strip())

    if isinstance(entity, DataTransferImportComponent):
        all_params = get_dynamic_source_parameter(entity.source)
    else:
        all_params = get_dynamic_input_parameter(entity.inputs)

    flattened_group_keys = []
    # Flatten all group parameters, for function parameter validation.
    from azure.ai.ml.entities._inputs_outputs import GroupInput

    for name, item in entity.inputs.items():
        if isinstance(item, GroupInput):
            flattened_group_keys.extend(list(item.flatten(group_parameter_name=name).keys()))

    doc_string = entity.description
    # Try add yaml to doc string
    try:
        yaml_str = entity._yaml_str if entity._yaml_str else entity._to_yaml()
        doc_string = "{0}\n\nComponent yaml:\n```yaml\n{1}\n```".format(doc_string, yaml_str)
    except Exception:  # pylint: disable=W0718
        pass

    params_assignment_str = ", ".join([f"{param.name}=xxx" for param in all_params])
    example = f"component_func({params_assignment_str})"

    dynamic_func = create_kw_function_from_parameters(
        component_creation_func,
        documentation=str(doc_string),
        parameters=all_params,
        func_name=func_name,
        flattened_group_keys=flattened_group_keys,
    )

    # Bug Item number: 2883188
    dynamic_func._func_calling_example = example  # type: ignore
    dynamic_func._has_parameters = bool(all_params)  # type: ignore
    return dynamic_func
