import copy
import pydash
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import Job, PipelineJob


def write_script(script_path: str, content: str) -> str:
    """
    Util for generating a python script, currently writes the file to disk.
    """
    with open(script_path, "w") as stream:
        stream.write(content)
    return script_path


def get_arm_id(ws_scope: OperationScope, entity_name: str, entity_version: str, entity_type) -> str:
    arm_id = (
        "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{"
        "}/{}/{}/versions/{}".format(
            ws_scope.subscription_id,
            ws_scope.resource_group_name,
            ws_scope.workspace_name,
            entity_type,
            entity_name,
            entity_version,
        )
    )

    return arm_id


def omit_single_with_wildcard(obj, omit_field: str):
    """
    Support .*. for pydash.omit
        omit_with_wildcard({"a": {"1": {"b": "v"}, "2": {"b": "v"}}}, "a.*.b")
        {"a": {"1": {}, "2": {}}}
    """
    obj = copy.deepcopy(obj)
    target_mark = ".*."
    if target_mark in omit_field:
        prefix, next_omit_field = omit_field.split(target_mark, 1)
        new_obj = pydash.get(obj, prefix)
        if new_obj:
            for key, value in new_obj.items():
                new_obj[key] = omit_single_with_wildcard(value, next_omit_field)
            pydash.set_(obj, prefix, new_obj)
        return obj
    else:
        return pydash.omit(obj, omit_field)


def omit_with_wildcard(obj, *properties: str):
    for omit_field in properties:
        obj = omit_single_with_wildcard(obj, omit_field)
    return obj


def prepare_dsl_curated(
    pipeline: PipelineJob, job_yaml, omit_fields=None, enable_default_omit_fields=True, in_rest=False
):
    """
    Prepare the dsl pipeline for curated test.
    Return objs instead of assert equal directly to enable difference viewer in PyCharm.
    """
    if omit_fields is None:
        omit_fields = []
    pipeline_from_yaml = Job.load(path=job_yaml)
    if in_rest:
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        pipeline_job_dict = pipeline_from_yaml._to_rest_object().as_dict()

        if enable_default_omit_fields:
            omit_fields.extend(
                [
                    "name",
                    "properties.jobs.*.componentId",
                    "properties.jobs.*._source",
                    "properties.jobs.*.trial.properties.componentSpec.name",
                    "properties.jobs.*.trial.properties.componentSpec.version",
                    "properties.jobs.*.trial.properties.componentSpec.$schema",
                    "properties.jobs.*.trial.properties.componentSpec.schema",
                    "properties.jobs.*.trial.properties.isAnonymous",
                ]
            )
    else:
        dsl_pipeline_job_dict = pipeline._to_dict()
        pipeline_job_dict = pipeline_from_yaml._to_dict()
        if enable_default_omit_fields:
            omit_fields.extend(
                [
                    "name",
                    "jobs.*.component.name",
                    "jobs.*.component.version",
                    "jobs.*.trial.name",
                    "jobs.*.trial.version",
                ]
            )

    dsl_pipeline_job_dict = omit_with_wildcard(dsl_pipeline_job_dict, *omit_fields)
    pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)

    return dsl_pipeline_job_dict, pipeline_job_dict
