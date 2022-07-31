import os
import time
import urllib.request as urllib
from zipfile import ZipFile

from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.operations._job_ops_helper import _wait_before_polling
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants
from azure.ai.ml import MLClient


def assert_final_job_status(job, client: MLClient, job_type: AutoMLJob, expected_terminal_status: str):
    assert isinstance(job, job_type)
    assert job.status == "NotStarted"

    poll_start_time = time.time()
    while job.status not in RunHistoryConstants.TERMINAL_STATUSES:
        time.sleep(_wait_before_polling(time.time() - poll_start_time))
        job = client.jobs.get(job.name)

    assert job.status == expected_terminal_status, f"Job status mismatch. Job created: {job}"


def assert_created_job(job, client: MLClient, job_type: AutoMLJob):
    assert isinstance(job, job_type)
    assert job.status == "NotStarted"
    # After checking the job is created successfully, we don't need job running anymore;
    # try canceling the job
    try:
        client.jobs.cancel(job.name)
    except Exception:
        print(f"Canceling {job.name} failed")


def get_properties():
    properties = {
        "_automl_internal_enable_mltable_quick_profile": True,
        "_automl_internal_label": "latest",
        "_automl_internal_save_mlflow": True,
    }
    return properties


def download_dataset(download_url: str, data_file: str):

    # download data
    urllib.urlretrieve(download_url, filename=data_file)

    # extract files
    with ZipFile(data_file, "r") as zip:
        print("extracting files...")
        zip.extractall()
        print("done")
    # delete zip file
    os.remove(data_file)
