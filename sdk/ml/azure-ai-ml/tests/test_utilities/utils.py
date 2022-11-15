# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import os
import signal
import tempfile
import time
from typing import Dict, Callable
from zipfile import ZipFile
from io import StringIO

import pydash
import urllib3
from azure.core.exceptions import HttpResponseError
from devtools_testutils import is_live

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import Job, PipelineJob
from azure.ai.ml.operations._job_ops_helper import _wait_before_polling
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants, JobStatus
from azure.core.polling import LROPoller

_PYTEST_TIMEOUT_METHOD = "signal" if hasattr(signal, "SIGALRM") else "thread"  # use signal when os support SIGALRM
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
    pipeline_from_yaml = load_job(source=job_yaml)
    if in_rest:
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()  # pylint: disable=protected-access
        pipeline_job_dict = pipeline_from_yaml._to_rest_object().as_dict()  # pylint: disable=protected-access

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
        dsl_pipeline_job_dict = pipeline._to_dict()  # pylint: disable=protected-access
        pipeline_job_dict = pipeline_from_yaml._to_dict()  # pylint: disable=protected-access
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
        sleep_if_live(30)
        created_job = ml_client.jobs.get(created_job.name)
        print("Latest status : {0}".format(created_job.status))
    if created_job.status != expected_state:
        raise Exception(
            f"Job finished with unexpected status. Got {created_job.status!r} while expecting {expected_state!r}"
        )
    print(f"Job finished: {expected_state!r}")
    assert created_job.status == expected_state
    return created_job


def assert_final_job_status(
    job, client: MLClient, job_type: Job, expected_terminal_status: str, deadline: int = DEFAULT_TASK_TIMEOUT
) -> None:
    assert isinstance(job, job_type)

    poll_start_time = time.time()
    while job.status not in RunHistoryConstants.TERMINAL_STATUSES and time.time() < (poll_start_time + deadline):
        sleep_if_live(THREAD_WAIT_TIME_BEFORE_POLL)
        job = client.jobs.get(job.name)

    if job.status not in RunHistoryConstants.TERMINAL_STATUSES:
        cancel_poller = client.jobs.begin_cancel(job.name)
        assert isinstance(cancel_poller, LROPoller)
        assert cancel_poller.result() is None

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
    with ZipFile(data_file, "r") as _zip:
        print("extracting files...")
        _zip.extractall()
        print("done")
    # delete zip file
    os.remove(data_file)


# Given an entity's load function, load it using an open file input, a file path,
# and even a deprecated 'path=' path input then run the inputted
# entity validation function on all resulting entities.
# After validation, dump the loaded entity using all three input types
# and assert that the resulting dumped file is non-empty.
# Returns both path and pointer-loaded entities to allow for additional testing
# by the caller.
def verify_entity_load_and_dump(
    load_function,
    entity_validation_function,
    test_load_file_path: str,
    test_dump_file_path="dump-test.yaml",
    **load_kwargs,
):
    # test loading
    file_entity, stream_entity = None, None
    with open(test_load_file_path, "r") as f:
        file_entity = load_function(source=f, **load_kwargs)
    file_contents = ""
    with open(test_load_file_path, "r") as f:
        file_contents = f.read()
    with StringIO() as stream:
        stream.write(file_contents)
        stream.seek(0)
        stream_entity = load_function(source=stream, relative_origin=test_load_file_path, **load_kwargs)

    assert file_entity is not None
    assert stream_entity is not None

    first_input_entity = load_function(test_load_file_path, **load_kwargs)
    assert first_input_entity is not None

    old_path_entity = load_function(test_load_file_path, **load_kwargs)
    assert old_path_entity is not None

    # Run entity-specific validation on both loaded entities
    entity_validation_function(file_entity)
    entity_validation_function(stream_entity)
    entity_validation_function(first_input_entity)
    entity_validation_function(old_path_entity)

    # test dump
    # TODO once dump functionality audit is complete, this testing should be
    # made more robust, like comparing it to the inputted yaml or something.
    if test_dump_file_path is not None:

        # test file pointer-based dump
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpfilename = f"{tmpdirname}/{test_dump_file_path}"
            with open(tmpfilename, "w+") as f:
                file_entity.dump(f)
            assert get_file_contents(tmpfilename) != ""

        # test string stream dump
        with StringIO() as outputStream:
            stream_entity.dump(outputStream)
            assert outputStream.tell() > 0

        # test path-based dump
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpfilename = f"{tmpdirname}/{test_dump_file_path}"
            first_input_entity.dump(tmpfilename)
            assert get_file_contents(tmpfilename) != ""
            delete_file_if_exists(tmpfilename)

        # test path-based dump using deprecated input name
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpfilename = f"{tmpdirname}/{test_dump_file_path}"
            first_input_entity.dump(tmpfilename)
            assert get_file_contents(tmpfilename) != ""
            delete_file_if_exists(tmpfilename)

    return (old_path_entity, file_entity)


def get_file_contents(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return ""


def delete_file_if_exists(file_path: str):
    if file_path is not None and os.path.exists(file_path):
        os.remove(file_path)


def cancel_job(client: MLClient, job: Job) -> None:
    try:
        cancel_poller = client.jobs.begin_cancel(job.name)
        assert isinstance(cancel_poller, LROPoller)
        assert cancel_poller.result() is None
    except HttpResponseError:
        pass


def assert_job_cancel(
    job: Job,
    client: MLClient,
    *,
    experiment_name=None,
    check_before_cancelled: Callable[[Job], bool] = None,
) -> Job:
    created_job = client.jobs.create_or_update(job, experiment_name=experiment_name)
    if check_before_cancelled is not None:
        assert check_before_cancelled(created_job)
        cancel_job(client, created_job)
    return created_job


def wait_until_done(client: MLClient, job: Job, timeout: int = None) -> str:
    poll_start_time = time.time()
    while job.status not in RunHistoryConstants.TERMINAL_STATUSES:
        sleep_if_live(_wait_before_polling(time.time() - poll_start_time))
        job = client.jobs.get(job.name)
        if timeout is not None and time.time() - poll_start_time > timeout:
            # if timeout is passed in, execute job cancel if timeout and directly return CANCELED status
            cancel_job(client, job)
            return JobStatus.CANCELED
    return job.status


def sleep_if_live(seconds):
    """Sleeps for the given number of seconds if the test is live.
    In playback mode, this function does nothing.
    Please use this function instead of time.sleep() in tests if you want to wait for some remote operations.

    Not necessary actually when fixture skip_sleep_for_playback has not been disabled explicitly.
    Unify the behavior in case the fixture is disabled, like switch to skip_sleep_in_lro_polling.
    """
    if is_live():
        time.sleep(seconds)
