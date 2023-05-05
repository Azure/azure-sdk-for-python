# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, too-many-instance-attributes

import copy
import logging
from pathlib import Path
from typing import Dict, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJob as RestSparkJob
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml._schema.job.parameterized_spark import CONF_KEY_MAP, SparkConfSchema
from azure.ai.ml._schema.job.spark_job import SparkJobSchema
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._job.job import SparkConfKey
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    _BaseJobIdentityConfiguration,
)
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
    validate_inputs_for_args,
)
from azure.ai.ml.entities._job.parameterized_spark import ParameterizedSpark
from azure.ai.ml.entities._util import load_from_dict

from ..._schema import NestedField, UnionField
from .job import Job
from .job_io_mixin import JobIOMixin
from .spark_helpers import _validate_compute_or_resources, _validate_input_output_mode, _validate_spark_configurations
from .spark_job_entry import SparkJobEntry
from .spark_job_entry_mixin import SparkJobEntryMixin
from .spark_resource_configuration import SparkResourceConfiguration

module_logger = logging.getLogger(__name__)


class SparkJob(Job, ParameterizedSpark, JobIOMixin, SparkJobEntryMixin):
    """Create a standalone spark job.

    :param experiment_name:  Name of the experiment the job will be created under.
    :type experiment_name: str
    :param name: The name of the job.
    :type name: str
    :param display_name: Display name of the job.
    :type display_name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
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
    :param identity: Identity that spark job will use while running on compute.
    :type identity: Union[
        azure.ai.ml.ManagedIdentityConfiguration,
        azure.ai.ml.AmlTokenConfiguration,
        azure.ai.ml.UserIdentityConfiguration]
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
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param identity: Identity that spark job will use while running on compute.
    :type identity: Union[
        Dict,
        ManagedIdentityConfiguration,
        AmlTokenConfiguration,
        UserIdentityConfiguration]
    :param resources: Compute Resource configuration for the job.
    :type resources: Union[Dict, SparkResourceConfiguration]
    """

    def __init__(
        self,
        *,
        driver_cores: Optional[int] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[int] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[int] = None,
        dynamic_allocation_enabled: Optional[bool] = None,
        dynamic_allocation_min_executors: Optional[int] = None,
        dynamic_allocation_max_executors: Optional[int] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        compute: Optional[str] = None,
        identity: Optional[
            Union[Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        resources: Union[Dict, SparkResourceConfiguration, None] = None,
        **kwargs,
    ):
        kwargs[TYPE] = JobType.SPARK

        super().__init__(**kwargs)
        self.conf = self.conf or {}
        self.properties = self.properties or {}
        self.driver_cores = driver_cores
        self.driver_memory = driver_memory
        self.executor_cores = executor_cores
        self.executor_memory = executor_memory
        self.executor_instances = executor_instances
        self.dynamic_allocation_enabled = dynamic_allocation_enabled
        self.dynamic_allocation_min_executors = dynamic_allocation_min_executors
        self.dynamic_allocation_max_executors = dynamic_allocation_max_executors
        self.inputs = inputs
        self.outputs = outputs
        self.compute = compute
        self.resources = resources
        self.identity = identity
        if self.executor_instances is None and str(self.dynamic_allocation_enabled).lower() == "true":
            self.executor_instances = self.dynamic_allocation_min_executors

    @property
    def resources(self) -> Optional[SparkResourceConfiguration]:
        return self._resources

    @resources.setter
    def resources(self, value: Union[Dict[str, str], SparkResourceConfiguration, None]):
        if isinstance(value, dict):
            value = SparkResourceConfiguration(**value)
        self._resources = value

    @property
    def identity(
        self,
    ) -> Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]:
        return self._identity

    @identity.setter
    def identity(
        self,
        value: Union[
            Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, None
        ],
    ):
        if isinstance(value, dict):
            identify_schema = UnionField(
                [
                    NestedField(ManagedIdentitySchema, unknown=INCLUDE),
                    NestedField(AMLTokenIdentitySchema, unknown=INCLUDE),
                    NestedField(UserIdentitySchema, unknown=INCLUDE),
                ]
            )
            value = identify_schema._deserialize(value=value, attr=None, data=None)
        self._identity = value

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return SparkJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def filter_conf_fields(self):
        if self.conf is None:
            return {}
        data_conf = {}
        for conf_key, conf_val in self.conf.items():
            if not conf_key in CONF_KEY_MAP:
                data_conf[conf_key] = conf_val
        return data_conf

    def _to_rest_object(self) -> JobBase:
        self._validate()
        conf = {
            **(self.filter_conf_fields()),
            "spark.driver.cores": self.driver_cores,
            "spark.driver.memory": self.driver_memory,
            "spark.executor.cores": self.executor_cores,
            "spark.executor.memory": self.executor_memory,
        }
        if self.dynamic_allocation_enabled in ["True", "true", True]:
            conf["spark.dynamicAllocation.enabled"] = True
            conf["spark.dynamicAllocation.minExecutors"] = self.dynamic_allocation_min_executors
            conf["spark.dynamicAllocation.maxExecutors"] = self.dynamic_allocation_max_executors
        if self.executor_instances is not None:
            conf["spark.executor.instances"] = self.executor_instances

        properties = RestSparkJob(
            experiment_name=self.experiment_name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            code_id=self.code,
            entry=self.entry._to_rest_object() if self.entry else None,
            py_files=self.py_files,
            jars=self.jars,
            files=self.files,
            archives=self.archives,
            identity=self.identity._to_job_rest_object() if self.identity else None,
            conf=conf,
            properties=self.properties,
            environment_id=self.environment,
            inputs=to_rest_dataset_literal_inputs(self.inputs, job_type=self.type),
            outputs=to_rest_data_outputs(self.outputs),
            args=self.args,
            compute_id=self.compute,
            resources=self.resources._to_rest_object() if self.resources else None,
        )
        result = JobBase(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "SparkJob":
        loaded_data = load_from_dict(SparkJobSchema, data, context, additional_message, **kwargs)
        return SparkJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: JobBase) -> "SparkJob":
        rest_spark_job: RestSparkJob = obj.properties
        conf_schema = UnionField(
            [
                NestedField(SparkConfSchema, unknown=INCLUDE),
            ]
        )
        rest_spark_conf = copy.copy(rest_spark_job.conf) or {}
        rest_spark_conf = conf_schema._deserialize(value=rest_spark_conf, attr=None, data=None)
        spark_job = SparkJob(
            name=obj.name,
            entry=SparkJobEntry._from_rest_object(rest_spark_job.entry),
            experiment_name=rest_spark_job.experiment_name,
            id=obj.id,
            display_name=rest_spark_job.display_name,
            description=rest_spark_job.description,
            tags=rest_spark_job.tags,
            properties=rest_spark_job.properties,
            services=rest_spark_job.services,
            status=rest_spark_job.status,
            creation_context=obj.system_data,
            code=rest_spark_job.code_id,
            compute=rest_spark_job.compute_id,
            environment=rest_spark_job.environment_id,
            identity=_BaseJobIdentityConfiguration._from_rest_object(rest_spark_job.identity)
            if rest_spark_job.identity
            else None,
            args=rest_spark_job.args,
            conf=rest_spark_conf,
            driver_cores=rest_spark_conf.get(
                SparkConfKey.DRIVER_CORES, None
            ),  # copy fields from conf into the promote attribute in spark
            driver_memory=rest_spark_conf.get(SparkConfKey.DRIVER_MEMORY, None),
            executor_cores=rest_spark_conf.get(SparkConfKey.EXECUTOR_CORES, None),
            executor_memory=rest_spark_conf.get(SparkConfKey.EXECUTOR_MEMORY, None),
            executor_instances=rest_spark_conf.get(SparkConfKey.EXECUTOR_INSTANCES, None),
            dynamic_allocation_enabled=rest_spark_conf.get(SparkConfKey.DYNAMIC_ALLOCATION_ENABLED, None),
            dynamic_allocation_min_executors=rest_spark_conf.get(SparkConfKey.DYNAMIC_ALLOCATION_MIN_EXECUTORS, None),
            dynamic_allocation_max_executors=rest_spark_conf.get(SparkConfKey.DYNAMIC_ALLOCATION_MAX_EXECUTORS, None),
            resources=SparkResourceConfiguration._from_rest_object(rest_spark_job.resources),
            inputs=from_rest_inputs_to_dataset_literal(rest_spark_job.inputs),
            outputs=from_rest_data_outputs(rest_spark_job.outputs),
        )
        return spark_job

    def _to_component(self, context: Optional[Dict] = None, **kwargs):
        """Translate a spark job to component.

        :param context: Context of spark job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated spark component.
        """
        from azure.ai.ml.entities import SparkComponent

        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        context = context or {BASE_PATH_CONTEXT_KEY: Path("./")}

        # Create anonymous spark component with default version as 1
        return SparkComponent(
            tags=self.tags,
            is_anonymous=True,
            base_path=context[BASE_PATH_CONTEXT_KEY],
            description=self.description,
            code=self.code,
            entry=self.entry,
            py_files=self.py_files,
            jars=self.jars,
            files=self.files,
            archives=self.archives,
            driver_cores=self.driver_cores,
            driver_memory=self.driver_memory,
            executor_cores=self.executor_cores,
            executor_memory=self.executor_memory,
            executor_instances=self.executor_instances,
            dynamic_allocation_enabled=self.dynamic_allocation_enabled,
            dynamic_allocation_min_executors=self.dynamic_allocation_min_executors,
            dynamic_allocation_max_executors=self.dynamic_allocation_max_executors,
            conf=self.conf,
            properties=self.properties,
            environment=self.environment,
            inputs=self._to_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            args=self.args,
        )

    def _to_node(self, context: Optional[Dict] = None, **kwargs):
        """Translate a spark job to a pipeline node.

        :param context: Context of spark job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated spark component.
        """
        from azure.ai.ml.entities._builders import Spark

        component = self._to_component(context, **kwargs)

        return Spark(
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            # code, entry, py_files, jars, files, archives, environment and args are static and not allowed to be
            # overwritten. And we will always get them from component.
            component=component,
            identity=self.identity,
            driver_cores=self.driver_cores,
            driver_memory=self.driver_memory,
            executor_cores=self.executor_cores,
            executor_memory=self.executor_memory,
            executor_instances=self.executor_instances,
            dynamic_allocation_enabled=self.dynamic_allocation_enabled,
            dynamic_allocation_min_executors=self.dynamic_allocation_min_executors,
            dynamic_allocation_max_executors=self.dynamic_allocation_max_executors,
            conf=self.conf,
            inputs=self.inputs,
            outputs=self.outputs,
            compute=self.compute,
            resources=self.resources,
            properties=self.properties,
        )

    def _validate(self) -> None:
        _validate_compute_or_resources(self.compute, self.resources)
        _validate_input_output_mode(self.inputs, self.outputs)
        _validate_spark_configurations(self)
        self._validate_entry()

        if self.args:
            validate_inputs_for_args(self.args, self.inputs)
