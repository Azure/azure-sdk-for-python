from datetime import datetime

import pytest
from dateutil.tz import tz

from azure.ai.ml._ml_exceptions import ValidationException
from azure.ai.ml.constants import TimeZone
from azure.ai.ml.entities import JobSchedule, PipelineJob, CronTrigger, RecurrenceTrigger
from azure.ai.ml.entities._load_functions import load_schedule, load_job

from .._util import _SCHEDULE_TIMEOUT_SECOND


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_SCHEDULE_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestScheduleEntity:
    def test_load_cron_schedule_with_file_reference(self):
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path)
        assert type(schedule) == JobSchedule
        assert type(schedule.create_job) == PipelineJob
        assert type(schedule.trigger) == CronTrigger
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

    def test_create_schedule_entity(self):
        test_job_path = "./tests/test_configs/pipeline_jobs/hello-pipeline-abc.yml"
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        job = load_job(test_job_path)
        start_time = datetime(year=2022, month=3, day=10, hour=10, minute=15)
        end_time = datetime(year=2022, month=6, day=10, hour=10, minute=15, tzinfo=tz.gettz("China Standard Time"))
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

    def test_create_recurrence_trigger_no_pattern(self):
        start_time = datetime(year=2022, month=3, day=10, hour=10, minute=15)
        end_time = datetime(year=2022, month=6, day=10, hour=10, minute=15, tzinfo=tz.gettz("China Standard Time"))
        trigger = ScheduleRecurrenceTrigger(frequency="day", interval=1, start_time=start_time, end_time=end_time)
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
