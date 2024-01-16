# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Optional

from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.entities._component.import_component import ImportComponent
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._job.import_job import ImportSource

from .command_func import _parse_input, _parse_inputs_outputs, _parse_output
from .import_node import Import


def import_job(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    source: Optional[ImportSource] = None,
    output: Optional[Output] = None,
    is_deterministic: bool = True,
    **kwargs: Any,
) -> Import:
    """Create an Import object which can be used inside dsl.pipeline as a function
    and can also be created as a standalone import job.

    :keyword name: Name of the import job or component created.
    :paramtype name: str
    :keyword description: A friendly description of the import.
    :paramtype description: str
    :keyword tags: Tags to be attached to this import.
    :paramtype tags: Dict
    :keyword display_name: A friendly name.
    :paramtype display_name: str
    :keyword experiment_name: Name of the experiment the job will be created under.
        If None is provided, the default will be set to the current directory name.
        Will be ignored as a pipeline step.
    :paramtype experiment_name: str
    :keyword source: Input source parameters used by this import.
    :paramtype source: ~azure.ai.ml.entities._job.import_job.ImportSource
    :keyword output: The output of this import.
    :paramtype output: ~azure.ai.ml.entities.Output
    :keyword is_deterministic: Specify whether the command will return the same output given the same input.
        If a command (component) is deterministic, when used as a node/step in a pipeline,
        it will reuse results from a previously submitted job in the current workspace
        which has the same inputs and settings.
        In this case, this step will not use any compute resource.
        Defaults to True.
    :paramtype is_deterministic: bool
    :returns: The Import object.
    :rtype: ~azure.ai.ml.entities._builders.import_node.Import
    """
    inputs = source._to_job_inputs() if source else kwargs.pop("inputs")
    outputs = {"output": output} if output else kwargs.pop("outputs")
    component_inputs, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)

    component = kwargs.pop("component", None)

    if component is None:
        component = ImportComponent(
            name=name,
            tags=tags,
            display_name=display_name,
            description=description,
            source=component_inputs,
            output=component_outputs["output"],
            _source=ComponentSource.BUILDER,
            is_deterministic=is_deterministic,
            **kwargs,
        )

    import_obj = Import(
        component=component,
        name=name,
        description=description,
        tags=tags,
        display_name=display_name,
        experiment_name=experiment_name,
        inputs=job_inputs,
        outputs=job_outputs,
        **kwargs,
    )

    return import_obj
