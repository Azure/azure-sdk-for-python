import os
import copy
import time
import pydash
from typing import Dict
import urllib3
from zipfile import ZipFile

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml import load_job, MLClient
from azure.ai.ml.entities import Job, PipelineJob
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants


DEFAULT_TASK_TIMEOUT = 30 * 60  # 30mins
THREAD_WAIT_TIME_BEFORE_POLL = 60  # 1min


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
    pipeline_from_yaml = load_job(path=job_yaml)
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
                    "properties.jobs.*.trial.properties.componentSpec._source",
                    "properties.settings",
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


def submit_and_wait(ml_client, pipeline_job: PipelineJob, expected_state: str = "Completed") -> PipelineJob:
    created_job = ml_client.jobs.create_or_update(pipeline_job)
    terminal_states = ["Completed", "Failed", "Canceled", "NotResponding"]
    assert created_job is not None
    assert expected_state in terminal_states

    while created_job.status not in terminal_states:
        time.sleep(30)
        created_job = ml_client.jobs.get(created_job.name)
        print("Latest status : {0}".format(created_job.status))
    if created_job.status != expected_state:
        raise Exception(
            f"Job finished with unexpected status. Got {created_job.status!r} while expecting {expected_state!r}"
        )
    else:
        print(f"Job finished: {expected_state!r}")
    assert created_job.status == expected_state
    return created_job


def assert_final_job_status(
    job, client: MLClient, job_type: Job, expected_terminal_status: str, deadline: int = DEFAULT_TASK_TIMEOUT
) -> None:
    assert isinstance(job, job_type)

    poll_start_time = time.time()
    while job.status not in RunHistoryConstants.TERMINAL_STATUSES and time.time() < (poll_start_time + deadline):
        time.sleep(THREAD_WAIT_TIME_BEFORE_POLL)
        job = client.jobs.get(job.name)

    if job.status not in RunHistoryConstants.TERMINAL_STATUSES:
        client.jobs.cancel(job.name)

    assert job.status == expected_terminal_status, f"Job status mismatch. Job created: {job}"


def get_automl_job_properties() -> Dict:
    return {}


def download_dataset(download_url: str, data_file: str, retries=3) -> None:
    # download data
    http = urllib3.PoolManager()
    resp = http.request("GET", download_url, preload_content=False, retries=retries)
    with open(data_file, "wb") as f:
        for chunk in resp.stream(1024):
            f.write(chunk)
    resp.release_conn()

    # extract files
    with ZipFile(data_file, "r") as zip:
        print("extracting files...")
        zip.extractall()
        print("done")
    # delete zip file
    os.remove(data_file)
