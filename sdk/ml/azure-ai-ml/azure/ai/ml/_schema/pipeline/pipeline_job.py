# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from marshmallow import INCLUDE

from azure.ai.ml.constants import JobType, NodeType
from azure.ai.ml._schema import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.pipeline import PipelineJobSettingsSchema
from azure.ai.ml._schema.pipeline.automl_node import AutoMLNodeSchema
from azure.ai.ml._schema.pipeline.component_job import (
    CommandSchema,
    SweepSchema,
    ParallelSchema,
    _resolve_inputs_outputs,
)
from marshmallow import fields, post_load, pre_dump
from azure.ai.ml._schema.core.fields import ComputeField, PipelineNodeNameStr, TypeSensitiveUnionField
from azure.ai.ml._schema.pipeline.pipeline_command_job import PipelineCommandJobSchema
from azure.ai.ml._schema.pipeline.pipeline_parallel_job import PipelineParallelJobSchema
from azure.ai.ml._schema.schedule.schedule import CronScheduleSchema, RecurrenceScheduleSchema


module_logger = logging.getLogger(__name__)


class NodeNameStr(PipelineNodeNameStr):
    def _get_field_name(self) -> str:
        return "Pipeline node"


class PipelineJobSchema(BaseJobSchema):
    type = StringTransformedEnum(allowed_values=[JobType.PIPELINE])
    jobs = fields.Dict(
        keys=NodeNameStr(),
        values=TypeSensitiveUnionField(
            {
                NodeType.COMMAND: [NestedField(CommandSchema, unknown=INCLUDE), NestedField(PipelineCommandJobSchema)],
                NodeType.SWEEP: [NestedField(SweepSchema, unknown=INCLUDE)],
                NodeType.PARALLEL: [
                    # ParallelSchema support parallel pipeline yml with "component"
                    NestedField(ParallelSchema, unknown=INCLUDE),
                    NestedField(PipelineParallelJobSchema, unknown=INCLUDE),
                ],
                NodeType.AUTOML: [AutoMLNodeSchema(unknown=INCLUDE)],
            }
        ),
    )
    compute = ComputeField()
    settings = NestedField(PipelineJobSettingsSchema, unknown=INCLUDE)
    inputs = InputsField()
    outputs = OutputsField()
    schedule = UnionField([NestedField(CronScheduleSchema()), NestedField(RecurrenceScheduleSchema())])

    @post_load
    def make(self, data: dict, **kwargs) -> dict:
        from azure.ai.ml.entities import CommandJob, ParallelJob
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.constants import ComponentSource

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        # convert CommandJob to CommandComponent here

        jobs = data.get("jobs", {})
        for key, job_instance in jobs.items():
            if isinstance(job_instance, (CommandJob, ParallelJob)):
                # Translate command component/job to command component
                job_instance = job_instance._to_node(
                    context=self.context,
                    _source=ComponentSource.BUILDER,
                    pipeline_job_dict=data,
                )
                jobs[key] = job_instance
            # update job instance name to key
            job_instance.name = key
        return data

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)
