# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, too-many-instance-attributes

import copy
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJob as RestSparkJob
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml._schema.job.parameterized_spark import CONF_KEY_MAP
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
from azure.ai.ml.entities._inputs_outputs import Input, Output
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

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities import SparkComponent
    from azure.ai.ml.entities._builders import Spark

module_logger = logging.getLogger(__name__)


class SparkJob(Job, ParameterizedSpark, JobIOMixin, SparkJobEntryMixin):
    """A standalone Spark job.

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
        executors registered with this application up and down based on the workload.
    :paramtype dynamic_allocation_enabled: Optional[bool]
    :keyword dynamic_allocation_min_executors: The lower bound for the number of executors if dynamic allocation is
        enabled.
    :paramtype dynamic_allocation_min_executors: Optional[int]
    :keyword dynamic_allocation_max_executors: The upper bound for the number of executors if dynamic allocation is
        enabled.
    :paramtype dynamic_allocation_max_executors: Optional[int]
    :keyword inputs: The mapping of input data bindings used in the job.
    :paramtype inputs: Optional[dict[str, ~azure.ai.ml.Input]]
    :keyword outputs: The mapping of output data bindings used in the job.
    :paramtype outputs: Optional[dict[str, ~azure.ai.ml.Output]]
    :keyword compute: The compute resource the job runs on.
    :paramtype compute: Optional[str]
    :keyword identity: The identity that the Spark job will use while running on compute.
    :paramtype identity: Optional[Union[dict[str, str], ~azure.ai.ml.ManagedIdentityConfiguration,
        ~azure.ai.ml.AmlTokenConfiguration, ~azure.ai.ml.UserIdentityConfiguration]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_job_configuration]
            :end-before: [END spark_job_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a SparkJob.
    """

    def __init__(
        self,
        *,
        driver_cores: Optional[Union[int, str]] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[Union[int, str]] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[Union[int, str]] = None,
        dynamic_allocation_enabled: Optional[Union[bool, str]] = None,
        dynamic_allocation_min_executors: Optional[Union[int, str]] = None,
        dynamic_allocation_max_executors: Optional[Union[int, str]] = None,
        inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = None,
        outputs: Optional[Dict[str, Output]] = None,
        compute: Optional[str] = None,
        identity: Optional[
            Union[Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        resources: Optional[Union[Dict, SparkResourceConfiguration]] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = JobType.SPARK

        super().__init__(**kwargs)
        self.conf: Dict = self.conf or {}
        self.properties_sparkJob = self.properties or {}
        self.driver_cores = driver_cores
        self.driver_memory = driver_memory
        self.executor_cores = executor_cores
        self.executor_memory = executor_memory
        self.executor_instances = executor_instances
        self.dynamic_allocation_enabled = dynamic_allocation_enabled
        self.dynamic_allocation_min_executors = dynamic_allocation_min_executors
        self.dynamic_allocation_max_executors = dynamic_allocation_max_executors
        self.inputs = inputs  # type: ignore[assignment]
        self.outputs = outputs  # type: ignore[assignment]
        self.compute = compute
        self.resources = resources
        self.identity = identity
        if self.executor_instances is None and str(self.dynamic_allocation_enabled).lower() == "true":
            self.executor_instances = self.dynamic_allocation_min_executors

    @property
    def resources(self) -> Optional[Union[Dict, SparkResourceConfiguration]]:
        """The compute resource configuration for the job.

        :return: The compute resource configuration for the job.
        :rtype: Optional[~azure.ai.ml.entities.SparkResourceConfiguration]
        """
        return self._resources

    @resources.setter
    def resources(self, value: Optional[Union[Dict[str, str], SparkResourceConfiguration]]) -> None:
        """Sets the compute resource configuration for the job.

        :param value: The compute resource configuration for the job.
        :type value: Optional[Union[dict[str, str], ~azure.ai.ml.entities.SparkResourceConfiguration]]
        """
        if isinstance(value, dict):
            value = SparkResourceConfiguration(**value)
        self._resources = value

    @property
    def identity(
        self,
    ) -> Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]:
        """The identity that the Spark job will use while running on compute.

        :return: The identity that the Spark job will use while running on compute.
        :rtype: Optional[Union[~azure.ai.ml.ManagedIdentityConfiguration, ~azure.ai.ml.AmlTokenConfiguration,
            ~azure.ai.ml.UserIdentityConfiguration]]
        """
        return self._identity

    @identity.setter
    def identity(
        self,
        value: Optional[
            Union[Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ],
    ) -> None:
        """Sets the identity that the Spark job will use while running on compute.

        :param value: The identity that the Spark job will use while running on compute.
        :type value: Optional[Union[dict[str, str], ~azure.ai.ml.ManagedIdentityConfiguration,
            ~azure.ai.ml.AmlTokenConfiguration, ~azure.ai.ml.UserIdentityConfiguration]]
        """
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
        res: dict = SparkJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    def filter_conf_fields(self) -> Dict[str, str]:
        """Filters out the fields of the conf attribute that are not among the Spark configuration fields
        listed in ~azure.ai.ml._schema.job.parameterized_spark.CONF_KEY_MAP and returns them in their own dictionary.

        :return: A dictionary of the conf fields that are not Spark configuration fields.
        :rtype: dict[str, str]
        """
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
            entry=self.entry._to_rest_object() if self.entry is not None and not isinstance(self.entry, dict) else None,
            py_files=self.py_files,
            jars=self.jars,
            files=self.files,
            archives=self.archives,
            identity=(
                self.identity._to_job_rest_object() if self.identity and not isinstance(self.identity, dict) else None
            ),
            conf=conf,
            properties=self.properties_sparkJob,
            environment_id=self.environment,
            inputs=to_rest_dataset_literal_inputs(self.inputs, job_type=self.type),
            outputs=to_rest_data_outputs(self.outputs),
            args=self.args,
            compute_id=self.compute,
            resources=(
                self.resources._to_rest_object() if self.resources and not isinstance(self.resources, Dict) else None
            ),
        )
        result = JobBase(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "SparkJob":
        loaded_data = load_from_dict(SparkJobSchema, data, context, additional_message, **kwargs)
        return SparkJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: JobBase) -> "SparkJob":
        rest_spark_job: RestSparkJob = obj.properties
        rest_spark_conf = copy.copy(rest_spark_job.conf) or {}
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
            identity=(
                _BaseJobIdentityConfiguration._from_rest_object(rest_spark_job.identity)
                if rest_spark_job.identity
                else None
            ),
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

    def _to_component(self, context: Optional[Dict] = None, **kwargs: Any) -> "SparkComponent":
        """Translate a spark job to component.

        :param context: Context of spark job YAML file.
        :type context: dict
        :return: Translated spark component.
        :rtype: SparkComponent
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
            properties=self.properties_sparkJob,
            environment=self.environment,
            inputs=self._to_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            args=self.args,
        )

    def _to_node(self, context: Optional[Dict] = None, **kwargs: Any) -> "Spark":
        """Translate a spark job to a pipeline node.

        :param context: Context of spark job YAML file.
        :type context: dict
        :return: Translated spark component.
        :rtype: Spark
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
            inputs=self.inputs,  # type: ignore[arg-type]
            outputs=self.outputs,  # type: ignore[arg-type]
            compute=self.compute,
            resources=self.resources,
            properties=self.properties_sparkJob,
        )

    def _validate(self) -> None:
        # TODO: make spark job schema validatable?
        if self.resources and not isinstance(self.resources, Dict):
            self.resources._validate()
        _validate_compute_or_resources(self.compute, self.resources)
        _validate_input_output_mode(self.inputs, self.outputs)
        _validate_spark_configurations(self)
        self._validate_entry()

        if self.args:
            validate_inputs_for_args(self.args, self.inputs)
