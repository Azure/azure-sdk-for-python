# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional, Union

from marshmallow import Schema

from ..._schema import PathAwareSchema
from ...constants._job.job import RestSparkConfKey
from ...entities import Environment, SparkJobEntry
from ...entities._job.parameterized_spark import DUMMY_IMAGE, ParameterizedSpark
from ...entities._job.spark_job_entry_mixin import SparkJobEntryMixin
from .._schema.component import InternalSparkComponentSchema
from ..entities import InternalComponent


class InternalSparkComponent(
    InternalComponent, ParameterizedSpark, SparkJobEntryMixin
):  # pylint: disable=too-many-instance-attributes
    """Internal Spark Component
    This class is used to handle internal spark component.
    It can be loaded from internal spark component yaml or from rest object of an internal spark component.
    But after loaded, its structure will be the same as spark component.
    """

    def __init__(
        self,
        entry: Union[Dict[str, str], SparkJobEntry, None] = None,
        py_files: Optional[List[str]] = None,
        jars: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        archives: Optional[List[str]] = None,
        driver_cores: Optional[int] = None,
        driver_memory: Optional[str] = None,
        executor_cores: Optional[int] = None,
        executor_memory: Optional[str] = None,
        executor_instances: Optional[int] = None,
        dynamic_allocation_enabled: Optional[bool] = None,
        dynamic_allocation_min_executors: Optional[int] = None,
        dynamic_allocation_max_executors: Optional[int] = None,
        conf: Optional[Dict[str, str]] = None,
        args: Optional[Dict] = None,
        **kwargs,
    ):
        SparkJobEntryMixin.__init__(self, entry=entry, **kwargs)
        # environment.setter has been overridden in ParameterizedSpark, so we need to pop it out here
        environment = kwargs.pop("environment", None)
        InternalComponent.__init__(self, **kwargs)
        # Pop it to avoid passing multiple values for code in ParameterizedSpark.__init__
        kwargs.pop("code", None)
        ParameterizedSpark.__init__(
            self,
            code=self.code,
            entry=entry,
            py_files=py_files,
            jars=jars,
            files=files,
            archives=archives,
            conf=conf,
            environment=environment,
            args=args,
            **kwargs,
        )
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

        self.conf = conf
        self.args = args

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return InternalSparkComponentSchema(context=context)

    @property
    def environment(self):
        if isinstance(self._environment, Environment) and self._environment.image is None:
            return Environment(conda_file=self._environment.conda_file, image=DUMMY_IMAGE)
        return self._environment

    @environment.setter
    def environment(self, value):
        if value is None or isinstance(value, (str, Environment)):
            self._environment = value
        elif isinstance(value, dict):
            self._environment = Environment(**value)
        else:
            raise ValueError(f"Unsupported environment type: {type(value)}")

    @property
    def jars(self):
        return self._jars

    @jars.setter
    def jars(self, value):
        if isinstance(value, str):
            value = [value]
        self._jars = value

    @property
    def py_files(self):
        return self._py_files

    @py_files.setter
    def py_files(self, value):
        if isinstance(value, str):
            value = [value]
        self._py_files = value

    def _to_dict(self) -> Dict:
        result = super()._to_dict()
        return result

    def _to_rest_object(self):
        result = super()._to_rest_object()
        if "pyFiles" in result.properties.component_spec:
            result.properties.component_spec["py_files"] = result.properties.component_spec.pop("pyFiles")
        return result

    @classmethod
    def _from_rest_object_to_init_params(cls, obj) -> Dict:
        if "py_files" in obj.properties.component_spec:
            obj.properties.component_spec["pyFiles"] = obj.properties.component_spec.pop("py_files")
        result = super()._from_rest_object_to_init_params(obj)
        return result
