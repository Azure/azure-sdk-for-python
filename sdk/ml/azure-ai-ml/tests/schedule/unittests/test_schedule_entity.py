from datetime import datetime

import pytest
from test_utilities.utils import verify_entity_load_and_dump

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
            assert type(schedule) == JobSchedule
            assert type(schedule.create_job) == PipelineJob
            assert type(schedule.trigger) == CronTrigger

        schedule = verify_entity_load_and_dump(load_schedule, simple_schedule_validation, test_path)[0]
        actual_dict = schedule._to_rest_object().as_dict()["properties"]
        # Skip job definition
        actual_dict["action"]["job_definition"] = {}
        expected_dict = {
            "description": "a weekly retrain schedule",
            "properties": {},
            "tags": {},
            "action": {"action_type": "CreateJob", "job_definition": {}},
            "display_name": "weekly retrain schedule",
            "trigger": {
                "end_time": "2022-06-10 10:15:00",
                "start_time": "2022-03-10 10:15:00",
                "time_zone": "Pacific Standard Time",
                "trigger_type": "Cron",
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
                "action_type": "CreateJob",
                "job_definition": {
                    "experiment_name": "Default",
                    "is_archived": False,
                    "job_type": "Pipeline",
                    "source_job_id": "/subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/jobs/test_617704734544",
                },
            },
            "display_name": "weekly retrain schedule",
            "trigger": {"time_zone": "UTC", "trigger_type": "Cron", "expression": "15 10 * * 1"},
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
            "end_time": "2022-06-10 10:15:00",
            "start_time": "2022-03-10 10:15:00",
            "time_zone": "UTC",
            "trigger_type": "Recurrence",
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
            "end_time": "2022-06-10 10:15:00",
            "frequency": "day",
            "interval": 1,
            "schedule": {"hours": [1, 3, 4, 5], "minutes": [0], "week_days": ["tuesday", "thursday"]},
            "start_time": "2022-03-10 10:15:00",
            "time_zone": "UTC",
            "trigger_type": "Recurrence",
        }

    def test_unsupported_job_type(self):
        test_path = "./tests/test_configs/schedule/invalid/hello_cron_schedule_with_unsupported_job.yml"
        schedule = load_schedule(test_path)
        with pytest.raises(ValidationException) as e:
            schedule._to_rest_object()
        assert "Unsupported job type 'Command'" in str(e)
        test_path = "./tests/test_configs/schedule/invalid/hello_cron_schedule_with_unsupported_job2.yml"
        schedule = load_schedule(test_path)
        with pytest.raises(ValidationException) as e:
            schedule._to_rest_object()
        assert "Unsupported job type 'Command'" in str(e)

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
