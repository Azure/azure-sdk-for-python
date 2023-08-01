# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import INCLUDE, fields, post_load, pre_dump

from ..._schema import ArmVersionedStr, NestedField, RegistryStr, UnionField
from ..._schema.core.fields import DumpableEnumField
from ..._schema.pipeline.component_job import BaseNodeSchema, _resolve_inputs_outputs
from ...constants._common import AzureMLResourceType
from .component import InternalComponentSchema, NodeType


class InternalBaseNodeSchema(BaseNodeSchema):
    class Meta:
        unknown = INCLUDE

    component = UnionField(
        [
            # for registry type assets
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # inline component or component file reference starting with FILE prefix
            NestedField(InternalComponentSchema, unknown=INCLUDE),
        ],
        required=True,
    )
    type = DumpableEnumField(
        allowed_values=NodeType.all_values(),
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        from ...entities._builders import parse_inputs_outputs

        # parse inputs/outputs
        data = parse_inputs_outputs(data)

        # dict to node object
        from ...entities._job.pipeline._load_component import pipeline_node_factory

        return pipeline_node_factory.load_from_dict(data=data)

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):  # pylint: disable=unused-argument
        return _resolve_inputs_outputs(job)


class ScopeSchema(InternalBaseNodeSchema):
    type = DumpableEnumField(allowed_values=[NodeType.SCOPE])
    adla_account_name = fields.Str(required=True)
    scope_param = fields.Str()
    custom_job_name_suffix = fields.Str()
    priority = fields.Int()
    auto_token = fields.Int()
    tokens = fields.Int()
    vcp = fields.Float()


class HDInsightSchema(InternalBaseNodeSchema):
    type = DumpableEnumField(allowed_values=[NodeType.HDI])

    compute_name = fields.Str()
    queue = fields.Str()
    driver_memory = fields.Str()
    driver_cores = fields.Int()
    executor_memory = fields.Str()
    executor_cores = fields.Int()
    number_executors = fields.Int()
    conf = UnionField(
        # dictionary or json string
        union_fields=[fields.Dict(keys=fields.Str()), fields.Str()],
    )
    hdinsight_spark_job_name = fields.Str()
