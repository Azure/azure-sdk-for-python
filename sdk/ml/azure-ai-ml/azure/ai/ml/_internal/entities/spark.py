# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional, Union

from azure.ai.ml._internal._schema.component import InternalSparkComponentSchema
from azure.ai.ml._internal.entities import InternalComponent
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.entities import SparkJobEntry
from marshmallow import Schema


class InternalSparkComponent(InternalComponent):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        entry: Union[Dict[str, str], SparkJobEntry, None] = None,
        pyFiles: Optional[List[str]] = None,
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
        super().__init__(**kwargs)
        self.entry = entry
        self.pyFiles = pyFiles
        self.jars = jars
        self.files = files
        self.archives = archives
        self.driver_cores = driver_cores
        self.driver_memory = driver_memory
        self.executor_cores = executor_cores
        self.executor_memory = executor_memory
        self.executor_instances = executor_instances
        self.dynamic_allocation_enabled = dynamic_allocation_enabled
        self.dynamic_allocation_min_executors = dynamic_allocation_min_executors
        self.dynamic_allocation_max_executors = dynamic_allocation_max_executors
        self.conf = conf
        self.args = args

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return InternalSparkComponentSchema(context=context)
