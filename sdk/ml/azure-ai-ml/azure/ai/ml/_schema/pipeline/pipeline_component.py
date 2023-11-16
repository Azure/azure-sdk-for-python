# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_load, pre_dump

from azure.ai.ml._schema._utils.utils import _resolve_group_inputs_for_component
from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.component.input_output import OutputPortSchema, PrimitiveOutputSchema
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    FileRefField,
    NestedField,
    PipelineNodeNameStr,
    RegistryStr,
    StringTransformedEnum,
    TypeSensitiveUnionField,
    UnionField,
)
from azure.ai.ml._schema.pipeline.automl_node import AutoMLNodeSchema
from azure.ai.ml._schema.pipeline.component_job import (
    BaseNodeSchema,
    CommandSchema,
    DataTransferCopySchema,
    DataTransferExportSchema,
    DataTransferImportSchema,
    ImportSchema,
    ParallelSchema,
    SparkSchema,
    SweepSchema,
    _resolve_inputs_outputs,
)
from azure.ai.ml._schema.pipeline.condition_node import ConditionNodeSchema
from azure.ai.ml._schema.pipeline.control_flow_job import DoWhileSchema, ParallelForSchema
from azure.ai.ml._schema.pipeline.pipeline_command_job import PipelineCommandJobSchema
from azure.ai.ml._schema.pipeline.pipeline_datatransfer_job import (
    PipelineDataTransferCopyJobSchema,
    PipelineDataTransferExportJobSchema,
    PipelineDataTransferImportJobSchema,
)
from azure.ai.ml._schema.pipeline.pipeline_import_job import PipelineImportJobSchema
from azure.ai.ml._schema.pipeline.pipeline_parallel_job import PipelineParallelJobSchema
from azure.ai.ml._schema.pipeline.pipeline_spark_job import PipelineSparkJobSchema
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureMLResourceType
from azure.ai.ml.constants._component import (
    CONTROL_FLOW_TYPES,
    ComponentSource,
    ControlFlowType,
    DataTransferTaskType,
    NodeType,
)


class NodeNameStr(PipelineNodeNameStr):
    def _get_field_name(self) -> str:
        return "Pipeline node"


def PipelineJobsField():
    pipeline_enable_job_type = {
        NodeType.COMMAND: [
            NestedField(CommandSchema, unknown=INCLUDE),
            NestedField(PipelineCommandJobSchema),
        ],
        NodeType.IMPORT: [
            NestedField(ImportSchema, unknown=INCLUDE),
            NestedField(PipelineImportJobSchema),
        ],
        NodeType.SWEEP: [NestedField(SweepSchema, unknown=INCLUDE)],
        NodeType.PARALLEL: [
            # ParallelSchema support parallel pipeline yml with "component"
            NestedField(ParallelSchema, unknown=INCLUDE),
            NestedField(PipelineParallelJobSchema, unknown=INCLUDE),
        ],
        NodeType.PIPELINE: [NestedField("PipelineSchema", unknown=INCLUDE)],
        NodeType.AUTOML: AutoMLNodeSchema(unknown=INCLUDE),
        NodeType.SPARK: [
            NestedField(SparkSchema, unknown=INCLUDE),
            NestedField(PipelineSparkJobSchema),
        ],
    }

    # Note: the private node types only available when private preview flag opened before init of pipeline job
    # schema class.
    if is_private_preview_enabled():
        pipeline_enable_job_type[ControlFlowType.DO_WHILE] = [NestedField(DoWhileSchema, unknown=INCLUDE)]
        pipeline_enable_job_type[ControlFlowType.IF_ELSE] = [NestedField(ConditionNodeSchema, unknown=INCLUDE)]
        pipeline_enable_job_type[ControlFlowType.PARALLEL_FOR] = [NestedField(ParallelForSchema, unknown=INCLUDE)]

    # Todo: Put data_transfer logic to the last to avoid error message conflict, open a item to track:
    #  https://msdata.visualstudio.com/Vienna/_workitems/edit/2244262/
    pipeline_enable_job_type[NodeType.DATA_TRANSFER] = [
        TypeSensitiveUnionField(
            {
                DataTransferTaskType.COPY_DATA: [
                    NestedField(DataTransferCopySchema, unknown=INCLUDE),
                    NestedField(PipelineDataTransferCopyJobSchema),
                ],
                DataTransferTaskType.IMPORT_DATA: [
                    NestedField(DataTransferImportSchema, unknown=INCLUDE),
                    NestedField(PipelineDataTransferImportJobSchema),
                ],
                DataTransferTaskType.EXPORT_DATA: [
                    NestedField(DataTransferExportSchema, unknown=INCLUDE),
                    NestedField(PipelineDataTransferExportJobSchema),
                ],
            },
            type_field_name="task",
            unknown=INCLUDE,
        )
    ]

    pipeline_job_field = fields.Dict(
        keys=NodeNameStr(),
        values=TypeSensitiveUnionField(pipeline_enable_job_type),
    )
    return pipeline_job_field


# pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
def _post_load_pipeline_jobs(context, data: dict) -> dict:
    """Silently convert Job in pipeline jobs to node."""
    from azure.ai.ml.entities._builders import parse_inputs_outputs
    from azure.ai.ml.entities._builders.condition_node import ConditionNode
    from azure.ai.ml.entities._builders.do_while import DoWhile
    from azure.ai.ml.entities._builders.parallel_for import ParallelFor
    from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
    from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin

    # parse inputs/outputs
    data = parse_inputs_outputs(data)
    # convert JobNode to Component here
    jobs = data.get("jobs", {})

    for key, job_instance in jobs.items():
        if isinstance(job_instance, dict):
            # convert AutoML job dict to instance
            if job_instance.get("type") == NodeType.AUTOML:
                job_instance = AutoMLJob._create_instance_from_schema_dict(
                    loaded_data=job_instance,
                )
            elif job_instance.get("type") in CONTROL_FLOW_TYPES:
                # Set source to yaml job for control flow node.
                job_instance["_source"] = ComponentSource.YAML_JOB

                job_type = job_instance.get("type")
                if job_type == ControlFlowType.IF_ELSE:
                    # Convert to if-else node.
                    job_instance = ConditionNode._create_instance_from_schema_dict(loaded_data=job_instance)
                elif job_instance.get("type") == ControlFlowType.DO_WHILE:
                    # Convert to do-while node.
                    job_instance = DoWhile._create_instance_from_schema_dict(
                        pipeline_jobs=jobs, loaded_data=job_instance
                    )
                elif job_instance.get("type") == ControlFlowType.PARALLEL_FOR:
                    # Convert to do-while node.
                    job_instance = ParallelFor._create_instance_from_schema_dict(
                        pipeline_jobs=jobs, loaded_data=job_instance
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
            if job_instance.type == NodeType.DATA_TRANSFER and job_instance.task != DataTransferTaskType.COPY_DATA:
                job_instance._source = ComponentSource.BUILTIN
            else:
                job_instance.component._source = ComponentSource.YAML_JOB
                job_instance._source = job_instance.component._source
            jobs[key] = job_instance
        # update job instance name to key
        job_instance.name = key
    return data


class PipelineComponentSchema(ComponentSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.PIPELINE])
    jobs = PipelineJobsField()

    # primitive output is only supported for command component & pipeline component
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(PrimitiveOutputSchema, unknown=INCLUDE),
                NestedField(OutputPortSchema),
            ]
        ),
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
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

        # pipeline jobs post process is required before init of pipeline component: it converts control node dict
        # to entity.
        # however @post_load invocation order is not guaranteed, so we need to call it explicitly here.
        _post_load_pipeline_jobs(self.context, data)

        return PipelineComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            **data,
        )


class PipelineComponentFileRefField(FileRefField):
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def _serialize(self, value, attr, obj, **kwargs):
        """FileRefField does not support serialize.

        Call AnonymousPipelineComponent schema to serialize. This
        function is overwrite because we need Pipeline can be dumped.
        """
        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        # pylint: disable=no-member
        value = _resolve_group_inputs_for_component(value)
        return _AnonymousPipelineComponentSchema(context=component_schema_context)._serialize(value, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        # pylint: disable=no-member
        component = _AnonymousPipelineComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component


# Note: PipelineSchema is defined here instead of component_job.py is to
# resolve circular import and support recursive schema.
class PipelineSchema(BaseNodeSchema):
    # pylint: disable=unused-argument
    # do not support inline define a pipeline node
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(azureml_type=AzureMLResourceType.COMPONENT),
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
        return Pipeline(**data)  # pylint: disable=abstract-class-instantiated

    @pre_dump
    def resolve_inputs_outputs(self, data, **kwargs):
        return _resolve_inputs_outputs(data)
