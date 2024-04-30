# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Any, Dict, List, Optional, Union

from marshmallow import Schema

from azure.ai.ml._schema.component.spark_component import SparkComponentSchema
from azure.ai.ml.constants._common import COMPONENT_TYPE
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.constants._job.job import RestSparkConfKey
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._job.parameterized_spark import ParameterizedSpark

from ..._schema import PathAwareSchema
from .._job.spark_job_entry_mixin import SparkJobEntry, SparkJobEntryMixin
from .._util import convert_ordered_dict_to_dict, validate_attribute_type
from .._validation import MutableValidationResult
from .code import ComponentCodeMixin
from .component import Component


class SparkComponent(
    Component, ParameterizedSpark, SparkJobEntryMixin, ComponentCodeMixin
):  # pylint: disable=too-many-instance-attributes
    """Spark component version, used to define a Spark Component or Job.

    :keyword code: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url pointing
        to a remote location. Defaults to ".", indicating the current directory.
    :type code: Union[str, os.PathLike]
    :keyword entry: The file or class entry point.
    :paramtype entry: Optional[Union[dict[str, str], ~azure.ai.ml.entities.SparkJobEntry]]
    :keyword py_files: The list of .zip, .egg or .py files to place on the PYTHONPATH for Python apps. Defaults to None.
    :paramtype py_files: Optional[List[str]]
    :keyword jars: The list of .JAR files to include on the driver and executor classpaths. Defaults to None.
    :paramtype jars: Optional[List[str]]
    :keyword files: The list of files to be placed in the working directory of each executor. Defaults to None.
    :paramtype files: Optional[List[str]]
    :keyword archives: The list of archives to be extracted into the working directory of each executor.
        Defaults to None.
    :paramtype archives: Optional[List[str]]
    :keyword driver_cores: The number of cores to use for the driver process, only in cluster mode.
    :paramtype driver_cores: Optional[int]
    :keyword driver_memory: The amount of memory to use for the driver process, formatted as strings with a size unit
        suffix ("k", "m", "g" or "t") (e.g. "512m", "2g").
    :paramtype driver_memory: Optional[str]
    :keyword executor_cores: The number of cores to use on each executor.
    :paramtype executor_cores: Optional[int]
    :keyword executor_memory: The amount of memory to use per executor process, formatted as strings with a size unit
        suffix ("k", "m", "g" or "t") (e.g. "512m", "2g").
    :paramtype executor_memory: Optional[str]
    :keyword executor_instances: The initial number of executors.
    :paramtype executor_instances: Optional[int]
    :keyword dynamic_allocation_enabled: Whether to use dynamic resource allocation, which scales the number of
        executors registered with this application up and down based on the workload. Defaults to False.
    :paramtype dynamic_allocation_enabled: Optional[bool]
    :keyword dynamic_allocation_min_executors: The lower bound for the number of executors if dynamic allocation is
        enabled.
    :paramtype dynamic_allocation_min_executors: Optional[int]
    :keyword dynamic_allocation_max_executors: The upper bound for the number of executors if dynamic allocation is
        enabled.
    :paramtype dynamic_allocation_max_executors: Optional[int]
    :keyword conf: A dictionary with pre-defined Spark configurations key and values. Defaults to None.
    :paramtype conf: Optional[dict[str, str]]
    :keyword environment: The Azure ML environment to run the job in.
    :paramtype environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword inputs: A mapping of input names to input data sources used in the job. Defaults to None.
    :paramtype inputs: Optional[dict[str, Union[
        ~azure.ai.ml.entities._job.pipeline._io.NodeOutput,
        ~azure.ai.ml.Input,
        str,
        bool,
        int,
        float,
        Enum,
        ]]]
    :keyword outputs: A mapping of output names to output data sources used in the job. Defaults to None.
    :paramtype outputs: Optional[dict[str, Union[str, ~azure.ai.ml.Output]]]
    :keyword args: The arguments for the job. Defaults to None.
    :paramtype args: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_component_definition]
            :end-before: [END spark_component_definition]
            :language: python
            :dedent: 8
            :caption: Creating SparkComponent.
    """

    def __init__(
        self,
        *,
        code: Optional[Union[str, os.PathLike]] = ".",
        entry: Optional[Union[Dict[str, str], SparkJobEntry]] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        driver_cores: Optional[Union[int, str]] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[Union[int, str]] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[Union[int, str]] = None,
        dynamic_allocation_enabled: Optional[Union[bool, str]] = None,
        dynamic_allocation_min_executors: Optional[Union[int, str]] = None,
        dynamic_allocation_max_executors: Optional[Union[int, str]] = None,
        conf: Optional[Dict[str, str]] = None,
        environment: Optional[Union[str, Environment]] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        args: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.SPARK

        super().__init__(
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

        self.code: Optional[Union[str, os.PathLike]] = code
        self.entry = entry
        self.py_files = py_files
        self.jars = jars
        self.files = files
        self.archives = archives
        self.conf = conf
        self.environment = environment
        self.args = args
        # For pipeline spark job, we also allow user to set driver_cores, driver_memory and so on by setting conf.
        # If root level fields are not set by user, we promote conf setting to root level to facilitate subsequent
        # verification. This usually happens when we use to_component(SparkJob) or builder function spark() as a node
        # in pipeline sdk
        conf = conf or {}
        self.driver_cores = driver_cores or conf.get(RestSparkConfKey.DRIVER_CORES, None)
        self.driver_memory = driver_memory or conf.get(RestSparkConfKey.DRIVER_MEMORY, None)
        self.executor_cores = executor_cores or conf.get(RestSparkConfKey.EXECUTOR_CORES, None)
        self.executor_memory = executor_memory or conf.get(RestSparkConfKey.EXECUTOR_MEMORY, None)
        self.executor_instances = executor_instances or conf.get(RestSparkConfKey.EXECUTOR_INSTANCES, None)
        self.dynamic_allocation_enabled = dynamic_allocation_enabled or conf.get(
            RestSparkConfKey.DYNAMIC_ALLOCATION_ENABLED, None
        )
        self.dynamic_allocation_min_executors = dynamic_allocation_min_executors or conf.get(
            RestSparkConfKey.DYNAMIC_ALLOCATION_MIN_EXECUTORS, None
        )
        self.dynamic_allocation_max_executors = dynamic_allocation_max_executors or conf.get(
            RestSparkConfKey.DYNAMIC_ALLOCATION_MAX_EXECUTORS, None
        )

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        return SparkComponentSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "environment": (str, Environment),
            "code": (str, os.PathLike),
        }

    def _customized_validate(self) -> MutableValidationResult:
        validation_result = super()._customized_validate()
        self._append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(validation_result)
        return validation_result

    def _to_dict(self) -> Dict:
        # TODO: Bug Item number: 2897665
        res: Dict = convert_ordered_dict_to_dict(  # type: ignore
            {**self._other_parameter, **super(SparkComponent, self)._to_dict()}
        )
        return res

    def _to_ordered_dict_for_yaml_dump(self) -> Dict:
        """Dump the component content into a sorted yaml string.

        :return: The ordered dict
        :rtype: Dict
        """

        obj: dict = super()._to_ordered_dict_for_yaml_dump()
        # dict dumped base on schema will transfer code to an absolute path, while we want to keep its original value
        if self.code and isinstance(self.code, str):
            obj["code"] = self.code
        return obj

    def _get_environment_id(self) -> Union[str, None]:
        # Return environment id of environment
        # handle case when environment is defined inline
        if isinstance(self.environment, Environment):
            res: Optional[str] = self.environment.id
            return res
        return self.environment

    def __str__(self) -> str:
        try:
            toYaml: str = self._to_yaml()
            return toYaml
        except BaseException:  # pylint: disable=W0718
            toStr: str = super(SparkComponent, self).__str__()
            return toStr
