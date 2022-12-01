# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Dict, Union, List

from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken, ManagedIdentity
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._job.parallel.run_function import RunFunction

from .command_func import _parse_input, _parse_inputs_outputs, _parse_output
from .parallel import Parallel


def parallel_run_function(
    *,
    name: str = None,
    description: str = None,
    tags: Dict = None,
    properties: Dict = None,
    display_name: str = None,
    experiment_name: str = None,
    compute: str = None,
    retry_settings: BatchRetrySettings = None,
    environment_variables: Dict = None,
    logging_level: str = None,
    max_concurrency_per_instance: int = None,
    error_threshold: int = None,
    mini_batch_error_threshold: int = None,
    task: RunFunction = None,
    mini_batch_size: str = None,
    partition_keys: List = None,
    input_data: str = None,
    inputs: Dict = None,
    outputs: Dict = None,
    instance_count: int = None,
    instance_type: str = None,
    docker_args: str = None,
    shm_size: str = None,
    identity: Union[ManagedIdentity, AmlToken] = None,
    is_deterministic: bool = True,
    **kwargs,
) -> Parallel:
    """Create a Parallel object which can be used inside dsl.pipeline as a
    function and can also be created as a standalone parallel job.

    For an example of using ParallelRunStep, see the notebook
    https://aka.ms/parallel-example-notebook

    .. remarks::

        To use parallel_run_function:

        * Create a :class:`azure.ai.ml.entities._builders.Parallel` object to specify how parallel run is performed,
          with parameters to control batch size,number of nodes per compute target, and a
          reference to your custom Python script.

        * Build pipeline with the parallel object as a function. defines inputs and
          outputs for the step.

        * Sumbit the pipeline to run.

    .. code:: python

        from azure.ai.ml import Input, Output, parallel

        parallel_run = parallel_run_function(
            name = 'batch_score_with_tabular_input',
            display_name = 'Batch Score with Tabular Dataset',
            description = 'parallel component for batch score',
            inputs = dict(
            job_data_path=Input(type=AssetTypes.MLTABLE, description='The data to be split and scored in parallel'),
            score_model=Input(type=AssetTypes.URI_FOLDER, description='The model for batch score.')
            ),
            outputs = dict(job_output_path=Output(type=AssetTypes.MLTABLE)),
            input_data = '${{inputs.job_data_path}}',
            max_concurrency_per_instance = 2,  # Optional, default is 1
            mini_batch_size = '100',      # optional
            mini_batch_error_threshold = 5,  # Optional, allowed failed count on mini batch items, default is -1
            logging_level = 'DEBUG',     # Optional, default is INFO
            error_threshold = 5,       # Optional, allowed failed count totally, default is -1
            retry_settings = dict(max_retries=2, timeout=60),  # Optional
            task = RunFunction(
                code = './src',
                entry_script = 'tabular_batch_inference.py',
                environment = Environment(
                    image= 'mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04',
                    conda_file='./src/environment_parallel.yml'
                ),
                program_arguments = '--model ${{inputs.score_model}}',
                append_row_to = '${{outputs.job_output_path}}',   # Optional, if not set, summary_only
            ),
        )

    :param name: Name of the parallel job or component created
    :type name: str
    :param description: a friendly description of the parallel
    :type description: str
    :param tags: Tags to be attached to this parallel
    :type tags: Dict
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param display_name: a friendly name
    :type display_name: str
    :param experiment_name: Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name. Will be ignored as a pipeline step.
    :type experiment_name: str
    :param compute: the name of the compute where the parallel job is executed(
        will not be used if the parallel is used as a component/function)
    :type compute: str
    :param retry_settings: parallel component run failed retry
    :type retry_settings: BatchRetrySettings
    :param environment_variables:  A dictionary of environment variables names and values.
        These environment variables are set on the process where user script is being executed.
    :type environment_variables: Dict[str, str]
    :param logging_level: A string of the logging level name, which is defined in 'logging'.
        Possible values are 'WARNING', 'INFO', and 'DEBUG'. (optional, default value is 'INFO'.)
        This value could be set through PipelineParameter.
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has.
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of record failures for Tabular Dataset
        and file failures for File Dataset that should be ignored during
        processing. If the error count goes above this value, then the job will be aborted. Error
        threshold is for the entire input rather than the individual mini-batch sent to run() method.
        The range is [-1, int.max]. -1 indicates ignore all failures during processing.
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored.
    :type mini_batch_error_threshold: int
    :param task: The parallel task.
    :type task: RunFunction
    :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.) This value could be set
        through PipelineParameter.
    :type mini_batch_size: str
    :param partition_keys: The keys used to partition dataset into mini-batches.
        If specified, the data with the same key will be partitioned into the same mini-batch.
        If both partition_keys and mini_batch_size are specified, the partition keys will take effect.
        The input(s) must be partitioned dataset(s),
        and the partition_keys must be a subset of the keys of every input dataset for this to work.
    :type partition_keys: List
    :param input_data: The input data.
    :type input_data: str
    :param inputs: a dict of inputs used by this parallel.
    :type inputs: Dict
    :param outputs: the outputs of this parallel
    :type outputs: Dict
    :param instance_count: Optional number of instances or nodes used by the compute target. Defaults to 1.
    :type instance_count: int
    :param instance_type: Optional type of VM used as supported by the compute target.
    :type instance_type: str
    :param docker_args: Extra arguments to pass to the Docker run command. This would override any
     parameters that have already been set by the system, or in this section. This parameter is only
     supported for Azure ML compute types.
    :type docker_args: str
    :param shm_size: Size of the docker container's shared memory block. This should be in the
     format of (number)(unit) where number as to be greater than 0 and the unit can be one of
     b(bytes), k(kilobytes), m(megabytes), or g(gigabytes).
    :type shm_size: str
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[ManagedIdentity, AmlToken]
    :param is_deterministic: Specify whether the parallel will return same output given same input.
        If a parallel (component) is deterministic, when use it as a node/step in a pipeline,
        it will reuse results from a previous submitted job in current workspace which has same inputs and settings.
        In this case, this step will not use any compute resource.
        Default to be True, specify is_deterministic=False if you would like to avoid such reuse behavior.
    :type is_deterministic: bool
    """
    # pylint: disable=too-many-locals
    inputs = inputs or {}
    outputs = outputs or {}
    component_inputs, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)

    component = kwargs.pop("component", None)

    if component is None:
        component = ParallelComponent(
            base_path=os.getcwd(),  # base path should be current folder
            name=name,
            tags=tags,
            code=task.code,
            display_name=display_name,
            description=description,
            inputs=component_inputs,
            outputs=component_outputs,
            retry_settings=retry_settings,
            logging_level=logging_level,
            max_concurrency_per_instance=max_concurrency_per_instance,
            error_threshold=error_threshold,
            mini_batch_error_threshold=mini_batch_error_threshold,
            task=task,
            mini_batch_size=mini_batch_size,
            partition_keys=partition_keys,
            input_data=input_data,
            _source=ComponentSource.BUILDER,
            is_deterministic=is_deterministic,
            **kwargs,
        )

    parallel_obj = Parallel(  # pylint: disable=abstract-class-instantiated
        component=component,
        name=name,
        description=description,
        tags=tags,
        properties=properties,
        display_name=display_name,
        experiment_name=experiment_name,
        compute=compute,
        inputs=job_inputs,
        outputs=job_outputs,
        identity=identity,
        environment_variables=environment_variables,
        retry_settings=retry_settings,
        logging_level=logging_level,
        max_concurrency_per_instance=max_concurrency_per_instance,
        error_threshold=error_threshold,
        mini_batch_error_threshold=mini_batch_error_threshold,
        task=task,
        mini_batch_size=mini_batch_size,
        partition_keys=partition_keys,
        input_data=input_data,
        **kwargs,
    )

    if instance_count is not None or instance_type is not None or docker_args is not None or shm_size is not None:
        parallel_obj.set_resources(
            instance_count=instance_count, instance_type=instance_type, docker_args=docker_args, shm_size=shm_size
        )

    return parallel_obj
