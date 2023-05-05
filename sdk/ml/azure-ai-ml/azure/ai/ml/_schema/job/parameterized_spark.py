# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument,no-self-use

import re
from typing import Any, Dict, List

from marshmallow import INCLUDE, ValidationError, fields, post_dump, post_load, pre_dump, pre_load, validate, validates

from azure.ai.ml._schema.core.fields import CodeField, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._common import AzureMLResourceType

from ..assets.environment import AnonymousEnvironmentSchema
from ..core.fields import ArmVersionedStr, RegistryStr, UnionField

re_memory_pattern = re.compile("^\\d+[kKmMgGtTpP]$")


class SparkEntryFileSchema(metaclass=PatchedSchemaMeta):
    file = fields.Str(required=True)
    # add spark_job_entry_type and make it dump only to align with model definition,
    # this will make us get expected value when call spark._from_rest_object()
    spark_job_entry_type = fields.Str(dump_only=True)

    @pre_dump
    def to_dict(self, data, **kwargs):
        return {"file": data.entry}


class SparkEntryClassSchema(metaclass=PatchedSchemaMeta):
    class_name = fields.Str(required=True)
    # add spark_job_entry_type and make it dump only to align with model definition,
    # this will make us get expected value when call spark._from_rest_object()
    spark_job_entry_type = fields.Str(dump_only=True)

    @pre_dump
    def to_dict(self, data, **kwargs):
        return {"class_name": data.entry}


CONF_KEY_MAP = {
    "driver_cores": "spark.driver.cores",
    "driver_memory": "spark.driver.memory",
    "executor_cores": "spark.executor.cores",
    "executor_memory": "spark.executor.memory",
    "executor_instances": "spark.executor.instances",
    "dynamic_allocation_enabled": "spark.dynamicAllocation.enabled",
    "dynamic_allocation_min_executors": "spark.dynamicAllocation.minExecutors",
    "dynamic_allocation_max_executors": "spark.dynamicAllocation.maxExecutors",
}


class SparkConfSchema(metaclass=PatchedSchemaMeta):
    driver_cores = fields.Int()
    driver_memory = fields.Str(validate=validate.Regexp(re_memory_pattern))
    executor_cores = fields.Int()
    executor_memory = fields.Str(validate=validate.Regexp(re_memory_pattern))
    executor_instances = fields.Int()
    dynamic_allocation_enabled = fields.Bool()
    dynamic_allocation_min_executors = fields.Int()
    dynamic_allocation_max_executors = fields.Int()

    @pre_load
    def deserialize_field_names(self, data, **kwargs):
        for field_key, dict_key in CONF_KEY_MAP.items():
            value = data.get(dict_key, None)
            if dict_key in data and value is not None:
                del data[dict_key]
                data[field_key] = value
        return data

    @post_dump(pass_original=True)
    def serialize_field_names(self, data: Dict[str, Any], original_data: Dict[str, Any], **kwargs):
        # pass original data here to dump conf fields which are not defined in SparkConfSchema
        for field_name, _ in original_data.items():
            if field_name not in data:
                data[field_name] = original_data[field_name]
        for field_name, dict_name in CONF_KEY_MAP.items():
            val = data.get(field_name, None)
            if field_name in data and val is not None:
                del data[field_name]
                data[dict_name] = val
        return data


def no_duplicates(name: str, value: List):
    if len(value) != len(set(value)):
        raise ValidationError(f"{name} must not contain duplicate entries.")


class ParameterizedSparkSchema(PathAwareSchema):
    code = CodeField()
    entry = UnionField(
        [NestedField(SparkEntryFileSchema), NestedField(SparkEntryClassSchema)],
        required=True,
        metadata={"description": "Entry."},
    )
    py_files = fields.List(fields.Str(required=True))
    jars = fields.List(fields.Str(required=True))
    files = fields.List(fields.Str(required=True))
    archives = fields.List(fields.Str(required=True))
    conf = NestedField(SparkConfSchema, unknown=INCLUDE)
    properties = fields.Dict(keys=fields.Str(), values=fields.Raw())
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
        allow_none=True,
    )
    args = fields.Str(metadata={"description": "Command Line arguments."})

    @validates("py_files")
    def no_duplicate_py_files(self, value):
        no_duplicates("py_files", value)

    @validates("jars")
    def no_duplicate_jars(self, value):
        no_duplicates("jars", value)

    @validates("files")
    def no_duplicate_files(self, value):
        no_duplicates("files", value)

    @validates("archives")
    def no_duplicate_archives(self, value):
        no_duplicates("archives", value)

    @post_load
    def demote_conf_fields(self, data, **kwargs):
        conf = data["conf"] if "conf" in data else None
        if conf is not None:
            for field_name, _ in CONF_KEY_MAP.items():
                value = conf.get(field_name, None)
                if field_name in conf and value is not None:
                    del conf[field_name]
                    data[field_name] = value
        return data

    @pre_dump
    def promote_conf_fields(self, data: object, **kwargs):
        # copy fields from root object into the 'conf'
        conf = data.conf or {}
        for field_name, _ in CONF_KEY_MAP.items():
            value = data.__getattribute__(field_name)
            if value is not None:
                conf[field_name] = value
        data.__setattr__("conf", conf)
        return data
