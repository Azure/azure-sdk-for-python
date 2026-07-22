from datetime import datetime

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml._restclient.arm_ml_service.models import JobBaseProperties as RestJobBaseProperties
from azure.ai.ml.constants import TimeZone
from azure.ai.ml.entities import CronTrigger, JobSchedule, PipelineJob, RecurrencePattern, RecurrenceTrigger
from azure.ai.ml.entities._load_functions import load_job, load_schedule
from azure.ai.ml.exceptions import ValidationException

from .._util import _SCHEDULE_TIMEOUT_SECOND


@pytest.mark.timeout(_SCHEDULE_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestScheduleEntity:
    def test_load_cron_schedule_with_file_reference(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"

        def simple_schedule_validation(schedule):
            assert isinstance(schedule, JobSchedule)
            assert isinstance(schedule.create_job, PipelineJob)
            assert isinstance(schedule.trigger, CronTrigger)

        schedule = verify_entity_load_and_dump(load_schedule, simple_schedule_validation, test_path)[0]
        schedule.properties["test"] = "val"
        actual_dict = schedule._to_rest_object().as_dict()["properties"]
        # Skip job definition
        actual_dict["action"]["jobDefinition"] = {}
        expected_dict = {
            "description": "a weekly retrain schedule",
            "properties": {"test": "val"},
            "tags": {},
            "action": {"actionType": "CreateJob", "jobDefinition": {}},
            "displayName": "weekly retrain schedule",
            "trigger": {
                "endTime": "2022-06-10 10:15:00",
                "startTime": "2022-03-10 10:15:00",
                "timeZone": "Pacific Standard Time",
                "triggerType": "Cron",
                "expression": "15 10 * * 1",
            },
        }
        assert actual_dict == expected_dict
        schedule._validate(raise_error=True)

    def test_load_cron_schedule_with_job_reference(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_arm_id.yml"
        schedule_rest_object = load_schedule(test_path)._to_rest_object().as_dict()["properties"]
        assert schedule_rest_object == {
            "description": "a weekly retrain schedule",
            "properties": {},
            "tags": {},
            "action": {
                "actionType": "CreateJob",
                "jobDefinition": {
                    "experimentName": "",
                    "isArchived": False,
                    "jobType": "Pipeline",
                    "sourceJobId": "/subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/jobs/test_617704734544",
                },
            },
            "displayName": "weekly retrain schedule",
            "trigger": {"timeZone": "UTC", "triggerType": "Cron", "expression": "15 10 * * 1"},
        }

    def test_create_schedule_entity(self):
        test_job_path = "./tests/test_configs/pipeline_jobs/hello-pipeline-abc.yml"
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        job = load_job(test_job_path, params_override=[{"inputs.hello_string_top_level_input": "${{name}}"}])
        start_time = datetime(year=2022, month=3, day=10, hour=10, minute=15)
        end_time = datetime(year=2022, month=6, day=10, hour=10, minute=15)
        trigger = CronTrigger(
            expression="15 10 * * 1", start_time=start_time, end_time=end_time, time_zone=TimeZone.PACIFIC_STANDARD_TIME
        )
        schedule = JobSchedule(
            name="weekly_retrain_2022_cron_file",
            create_job=job,
            trigger=trigger,
            description="a weekly retrain schedule",
            display_name="weekly retrain schedule",
        )
        expected_dict_from_yaml = load_schedule(test_path)._to_rest_object().as_dict()
        assert schedule._to_rest_object().as_dict() == expected_dict_from_yaml
        schedule._validate(raise_error=True)

    def test_create_recurrence_trigger_no_pattern(self):
        start_time = datetime(year=2022, month=3, day=10, hour=10, minute=15)
        end_time = datetime(year=2022, month=6, day=10, hour=10, minute=15)
        trigger = RecurrenceTrigger(frequency="day", interval=1, start_time=start_time, end_time=end_time)
        assert trigger.schedule is not None
        assert trigger._to_rest_object().as_dict() == {
            "endTime": "2022-06-10 10:15:00",
            "startTime": "2022-03-10 10:15:00",
            "timeZone": "UTC",
            "triggerType": "Recurrence",
            "frequency": "day",
            "interval": 1,
            "schedule": {"hours": [], "minutes": []},
        }

    def test_create_recurrence_trigger_with_pattern(self):
        start_time = datetime(year=2022, month=3, day=10, hour=10, minute=15)
        end_time = datetime(year=2022, month=6, day=10, hour=10, minute=15)
        pattern = RecurrencePattern(hours=[1, 3, 4, 5], minutes=[0], week_days=["tuesday", "thursday"])
        trigger = RecurrenceTrigger(
            frequency="day", interval=1, start_time=start_time, end_time=end_time, schedule=pattern
        )
        assert trigger.schedule is not None
        assert trigger._to_rest_object().as_dict() == {
            "endTime": "2022-06-10 10:15:00",
            "frequency": "day",
            "interval": 1,
            "schedule": {"hours": [1, 3, 4, 5], "minutes": [0], "weekDays": ["tuesday", "thursday"]},
            "startTime": "2022-03-10 10:15:00",
            "timeZone": "UTC",
            "triggerType": "Recurrence",
        }

    @pytest.mark.usefixtures(
        "enable_pipeline_private_preview_features",
    )
    def test_schedule_with_command_job(self):
        # Test with local file job
        test_path = "./tests/test_configs/schedule/local_cron_command_job.yml"
        inner_job_path = "./tests/test_configs/command_job/command_job_test.yml"
        inner_job = load_job(inner_job_path)._to_job()
        schedule = load_schedule(test_path)
        rest_schedule_job_dict = schedule._to_rest_object().as_dict()["properties"]["action"]["jobDefinition"]
        # CommandJob and the schedule envelope both build the shared arm_ml_service hybrid (camelCase
        # as_dict), so the embedded job_definition matches the standalone job's properties directly.
        loaded_job_dict = inner_job._to_rest_object().as_dict()["properties"]
        assert rest_schedule_job_dict == loaded_job_dict
        # Test with local file + overwrites
        test_path = "./tests/test_configs/schedule/local_cron_command_job2.yml"
        schedule = load_schedule(test_path)
        rest_schedule_job_dict = schedule._to_rest_object().as_dict()["properties"]["action"]["jobDefinition"]
        # assert overwrite values
        assert rest_schedule_job_dict["environmentVariables"] == {"key": "val"}
        assert rest_schedule_job_dict["resources"] == {"properties": {}, "shmSize": "1g"}
        assert rest_schedule_job_dict["distribution"] == {
            "distributionType": "PyTorch",
            "processCountPerInstance": 1,
        }
        assert rest_schedule_job_dict["limits"] == {"jobLimitsType": "Command", "timeout": "PT50M"}

    @pytest.mark.usefixtures(
        "enable_pipeline_private_preview_features",
    )
    def test_schedule_entity_with_spark_job(self):
        # Test with local file job
        test_path = "./tests/test_configs/schedule/local_cron_spark_job.yml"
        inner_job_path = "./tests/test_configs/spark_job/spark_job_word_count_test.yml"
        inner_job = load_job(inner_job_path)._to_job()
        schedule = load_schedule(test_path)
        rest_schedule_job_dict = schedule._to_rest_object().as_dict()["properties"]["action"]["jobDefinition"]
        # SparkJob builds a v2023_04 msrest envelope; the schedule embeds it as its camelCase wire dict
        # (``.serialize()``), so compare against the standalone job serialized the same way.
        loaded_job_dict = inner_job._to_rest_object().properties.serialize()
        assert rest_schedule_job_dict == loaded_job_dict
        # Test with local file + overwrites
        test_path = "./tests/test_configs/schedule/local_cron_spark_job2.yml"
        schedule = load_schedule(test_path)
        rest_schedule_job_dict = schedule._to_rest_object().as_dict()["properties"]["action"]["jobDefinition"]
        # assert overwrite values
        assert rest_schedule_job_dict["conf"] == {
            "spark.driver.cores": "2",
            "spark.driver.memory": "2g",
            "spark.executor.cores": "2",
            "spark.executor.memory": "2g",
            "spark.executor.instances": "2",
        }
        assert "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04" in rest_schedule_job_dict["environmentId"]

    def test_invalid_date_string(self):
        pipeline_job = load_job(
            "./tests/test_configs/command_job/local_job.yaml",
        )
        trigger = RecurrenceTrigger(
            frequency="week",
            interval=4,
            schedule=RecurrencePattern(hours=10, minutes=15, week_days=["monday", "Tuesday"]),
            start_time="2022-03-10",
        )

        job_schedule = JobSchedule(name="simple_sdk_create_schedule", trigger=trigger, create_job=pipeline_job)
        with pytest.raises(Exception) as e:
            job_schedule._validate(raise_error=True)
        assert "Not a valid ISO8601-formatted datetime string" in str(e)

    def test_schedule_create_out_of_box_monitoring_job(self):
        test_path = "./tests/test_configs/schedule/out_of_box_monitoring.yaml"
        schedule = load_schedule(test_path)
        assert "genai_app_monitoring", schedule.name
