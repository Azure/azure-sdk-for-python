# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

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
from .component import Component


class SparkComponent(Component, ParameterizedSpark, SparkJobEntryMixin):  # pylint: disable=too-many-instance-attributes
    """Spark component version, used to define a spark component.

    :param code: The source code to run the job.
    :type code: Union[str, os.PathLike]
    :param entry: File or class entry point.
    :type entry: dict[str, str]
    :param py_files: List of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
    :type py_files: Optional[typing.List[str]]
    :param jars: List of jars to include on the driver and executor classpaths.
    :type jars: Optional[typing.List[str]]
    :param files: List of files to be placed in the working directory of each executor.
    :type files: Optional[typing.List[str]]
    :param archives: List of archives to be extracted into the working directory of each executor.
    :type archives: Optional[typing.List[str]]
    :param driver_cores: Number of cores to use for the driver process, only in cluster mode.
    :type driver_cores: int
    :param driver_memory: Amount of memory to use for the driver process.
    :type driver_memory: str
    :param executor_cores: The number of cores to use on each executor.
    :type executor_cores: int
    :param executor_memory: Amount of memory to use per executor process, in the same format as JVM memory strings with
        a size unit suffix ("k", "m", "g" or "t") (e.g. 512m, 2g).
    :type executor_memory: str
    :param executor_instances: Initial number of executors.
    :type executor_instances: int
    :param dynamic_allocation_enabled: Whether to use dynamic resource allocation, which scales the number of executors
        registered with this application up and down based on the workload.
    :type dynamic_allocation_enabled: bool
    :param dynamic_allocation_min_executors: Lower bound for the number of executors if dynamic allocation is enabled.
    :type dynamic_allocation_min_executors: int
    :param dynamic_allocation_max_executors: Upper bound for the number of executors if dynamic allocation is enabled.
    :type dynamic_allocation_max_executors: int
    :param conf: A dict with pre-defined spark configurations key and values.
    :type conf: dict
    :param environment: Azure ML environment to run the job in.
    :type environment: Union[str, azure.ai.ml.entities.Environment]
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    :param args: Arguments for the job.
    :type args: str
    """

    def __init__(
        self,
        *,
        code: Union[str, os.PathLike] = ".",
        entry: Union[Dict[str, str], SparkJobEntry, None] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        driver_cores: int = None,
        driver_memory: str = None,
        executor_cores: int = None,
        executor_memory: str = None,
        executor_instances: int = None,
        dynamic_allocation_enabled: bool = None,
        dynamic_allocation_min_executors: int = None,
        dynamic_allocation_max_executors: int = None,
        conf: Optional[Dict[str, str]] = None,
        environment: Union[str, Environment] = None,
        inputs: Dict = None,
        outputs: Dict = None,
        args: str = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.SPARK
        # Set default base path
        if "base_path" not in kwargs:
            kwargs["base_path"] = Path(".")

        super().__init__(
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

        self.code = code
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
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return SparkComponentSchema(context=context)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "environment": (str, Environment),
            "code": (str, os.PathLike),
        }

    def _to_dict(self) -> Dict:
        """Dump the spark component content into a dictionary."""
        return convert_ordered_dict_to_dict({**self._other_parameter, **super(SparkComponent, self)._to_dict()})

    def _get_environment_id(self) -> Union[str, None]:
        # Return environment id of environment
        # handle case when environment is defined inline
        if isinstance(self.environment, Environment):
            return self.environment.id
        return self.environment

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:  # pylint: disable=broad-except
            return super(SparkComponent, self).__str__()
