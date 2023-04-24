# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from functools import singledispatch
from pathlib import Path

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase as JobBaseData
from azure.ai.ml.constants._common import DEFAULT_EXPERIMENT_NAME
from azure.ai.ml.entities._builders.command import Command
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._builders.spark import Spark
from azure.ai.ml.entities._builders.sweep import Sweep
from azure.ai.ml.entities._job.job_name_generator import generate_job_name

from .import_job import ImportJob
from .job import Job


def generate_defaults(job: Job, rest_job: JobBaseData) -> None:
    # Default name to a generated user friendly name.
    if not job.name:
        rest_job.name = generate_job_name()

    if not job.display_name:
        rest_job.properties.display_name = rest_job.name

    # Default experiment to current folder name or "Default"
    if not job.experiment_name:
        rest_job.properties.experiment_name = Path("./").resolve().stem.replace(" ", "") or DEFAULT_EXPERIMENT_NAME


@singledispatch
def to_rest_job_object(something) -> JobBaseData:
    raise NotImplementedError()


@to_rest_job_object.register(Job)
def _(job: Job) -> JobBaseData:
    rest_job = job._to_rest_object()
    generate_defaults(job, rest_job)
    return rest_job


@to_rest_job_object.register(Command)
def _(command: Command) -> JobBaseData:
    rest_job = command._to_job()._to_rest_object()
    generate_defaults(command, rest_job)
    return rest_job


@to_rest_job_object.register(Sweep)
def _(sweep: Sweep) -> JobBaseData:
    rest_job = sweep._to_job()._to_rest_object()
    generate_defaults(sweep, rest_job)
    return rest_job


@to_rest_job_object.register(Pipeline)
def _(pipeline: Pipeline) -> JobBaseData:
    rest_job = pipeline._to_job()._to_rest_object()
    generate_defaults(pipeline, rest_job)
    return rest_job


@to_rest_job_object.register(Spark)
def _(spark: Spark) -> JobBaseData:
    rest_job = spark._to_job()._to_rest_object()
    generate_defaults(spark, rest_job)
    return rest_job


@to_rest_job_object.register(ImportJob)
def _(importJob: ImportJob) -> JobBaseData:
    rest_job = importJob._to_rest_object()
    generate_defaults(importJob, rest_job)
    return rest_job
