# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Optional

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
    **kwargs,
) -> Import:
    """Create a Import object which can be used inside dsl.pipeline as a
    function and can also be created as a standalone import job.

    :param name: Name of the import job or component created
    :type name: str
    :param description: a friendly description of the import
    :type description: str
    :param tags: Tags to be attached to this import
    :type tags: Dict
    :param display_name: a friendly name
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name. Will be ignored as a pipeline step.
    :type experiment_name: str
    :param source: input source parameters used by this import.
    :type source: ImportSource
    :param output: the output of this import
    :type output: Output
    :param is_deterministic: Specify whether the command will return same output given same input.
        If a command (component) is deterministic, when use it as a node/step in a pipeline,
        it will reuse results from a previous submitted job in current workspace which has same inputs and settings.
        In this case, this step will not use any compute resource.
        Default to be True, specify is_deterministic=False if you would like to avoid such reuse behavior.
    :type is_deterministic: bool
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
