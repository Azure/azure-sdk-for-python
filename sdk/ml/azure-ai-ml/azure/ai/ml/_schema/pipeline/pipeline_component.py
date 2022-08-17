# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    FileRefField,
    PipelineNodeNameStr,
    RegistryStr,
    TypeSensitiveUnionField,
)
from azure.ai.ml._schema.pipeline import CommandSchema, ParallelSchema
from azure.ai.ml._schema.pipeline.automl_node import AutoMLNodeSchema
from azure.ai.ml._schema.pipeline.component_job import BaseNodeSchema, SweepSchema, _resolve_inputs_outputs
from azure.ai.ml._schema.pipeline.pipeline_command_job import PipelineCommandJobSchema
from azure.ai.ml._schema.pipeline.pipeline_parallel_job import PipelineParallelJobSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType, ComponentSource, NodeType


class NodeNameStr(PipelineNodeNameStr):
    def _get_field_name(self) -> str:
        return "Pipeline node"


def PipelineJobsField():
    return fields.Dict(
        keys=NodeNameStr(),
        values=TypeSensitiveUnionField(
            {
                NodeType.COMMAND: [
                    NestedField(CommandSchema, unknown=INCLUDE),
                    NestedField(PipelineCommandJobSchema),
                ],
                NodeType.SWEEP: [NestedField(SweepSchema, unknown=INCLUDE)],
                NodeType.PARALLEL: [
                    # ParallelSchema support parallel pipeline yml with "component"
                    NestedField(ParallelSchema, unknown=INCLUDE),
                    NestedField(PipelineParallelJobSchema, unknown=INCLUDE),
                ],
                NodeType.PIPELINE: [NestedField("PipelineSchema", unknown=INCLUDE)],
                NodeType.AUTOML: AutoMLNodeSchema(unknown=INCLUDE),
            }
        ),
    )


def _post_load_pipeline_jobs(context, data: dict) -> dict:
    """Silently convert Job in pipeline jobs to node."""
    from azure.ai.ml.entities._builders import parse_inputs_outputs
    from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
    from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin

    # parse inputs/outputs
    data = parse_inputs_outputs(data)
    # convert JobNode to Component here
    jobs = data.get("jobs", {})

    # convert AutoML job dict to instance
    for key, job_instance in jobs.items():
        if isinstance(job_instance, dict) and job_instance.get("type") == NodeType.AUTOML:
            job_instance = AutoMLJob._create_instance_from_schema_dict(
                loaded_data=job_instance,
            )
            jobs[key] = job_instance

    for key, job_instance in jobs.items():
        # Translate job to node if translatable and overrides to_node.
        if isinstance(job_instance, ComponentTranslatableMixin) and "_to_node" in type(job_instance).__dict__:
            # set source as YAML
            job_instance = job_instance._to_node(
                context=context,
                pipeline_job_dict=data,
            )
            job_instance.component._source = ComponentSource.YAML_JOB
            jobs[key] = job_instance
        # update job instance name to key
        job_instance.name = key
    return data


class PipelineComponentSchema(ComponentSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.PIPELINE])
    jobs = PipelineJobsField()

    @post_load
    def make(self, data, **kwargs):
        return _post_load_pipeline_jobs(self.context, data)


class RestPipelineComponentSchema(PipelineComponentSchema):
    """When component load from rest, won't validate on name since there might
    be existing component with invalid name."""

    name = fields.Str(required=True)


class _AnonymousPipelineComponentSchema(AnonymousAssetSchema, PipelineComponentSchema):
    """Anonymous pipeline component schema.

    Note that do not support inline define anonymous pipeline component
    directly. Inheritance follows order: AnonymousAssetSchema,
    PipelineComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution
    order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._component.pipeline_component import PipelineComponent

        return PipelineComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            **data,
        )


class PipelineComponentFileRefField(FileRefField):
    def _serialize(self, value, attr, obj, **kwargs):
        """FileRefField does not support serialize.

        Call AnonymousPipelineComponent schema to serialize. This
        function is overwrite because we need Pipeline can be dumped.
        """
        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        return _AnonymousPipelineComponentSchema(context=component_schema_context)._serialize(value, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        component = _AnonymousPipelineComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component


# Note: PipelineSchema is defined here instead of component_job.py is to
# resolve circular import and support recursive schema.
class PipelineSchema(BaseNodeSchema):
    # do not support inline define a pipeline node
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # component file reference
            PipelineComponentFileRefField(),
        ],
        required=True,
    )
    type = StringTransformedEnum(allowed_values=[NodeType.PIPELINE])

    @post_load
    def make(self, data, **kwargs) -> "Pipeline":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.pipeline import Pipeline

        data = parse_inputs_outputs(data)
        return Pipeline(**data)

    @pre_dump
    def resolve_inputs_outputs(self, data, **kwargs):
        return _resolve_inputs_outputs(data)
