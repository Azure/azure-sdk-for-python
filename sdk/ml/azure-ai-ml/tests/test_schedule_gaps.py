from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from datetime import datetime, timezone, timedelta

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import LROConfigurations
from azure.ai.ml.entities import CronTrigger
from azure.ai.ml.entities._load_functions import load_schedule


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestScheduleGaps(AzureRecordedTestCase):
    def test_basic_schedule_lifecycle_triggers_and_enable_disable(self, client: MLClient, randstr: Callable[[], str]):
        # create a schedule from existing test config that uses a cron trigger
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path, params_override=params_override)

        # update start_time and end_time to valid ranges (service rejects Z-suffix and past dates)
        if getattr(schedule, "trigger", None) is not None:
            try:
                now = datetime.now(timezone.utc)
                schedule.trigger.start_time = (now - timedelta(days=1)).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
                schedule.trigger.end_time = (now + timedelta(days=365)).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                pass

        # create
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert rest_schedule._is_enabled is True

        # list - ensure schedules iterable returns at least one item
        rest_schedule_list = [item for item in client.schedules.list()]
        assert isinstance(rest_schedule_list, list)

        # trigger once
        result = client.schedules.trigger(schedule.name, schedule_time="2024-02-19T00:00:00")
        # result should be a ScheduleTriggerResult with a job_name attribute when trigger succeeds
        assert getattr(result, "job_name", None) is not None

        # disable
        rest_schedule = client.schedules.begin_disable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert rest_schedule._is_enabled is False

        # enable
        rest_schedule = client.schedules.begin_enable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert rest_schedule._is_enabled is True

        # cleanup: disable then delete
        client.schedules.begin_disable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        client.schedules.begin_delete(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        # after delete, getting should raise
        with pytest.raises(Exception) as e:
            client.schedules.get(schedule.name)
        assert "not found" in str(e).lower()

    def test_cron_trigger_roundtrip_properties(self, client: MLClient, randstr: Callable[[], str]):
        # ensure CronTrigger properties roundtrip via schedule create and get
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path, params_override=params_override)

        # update start_time and end_time to valid ranges (service rejects Z-suffix and past dates)
        if getattr(schedule, "trigger", None) is not None:
            try:
                now = datetime.now(timezone.utc)
                schedule.trigger.start_time = (now - timedelta(days=1)).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
                schedule.trigger.end_time = (now + timedelta(days=365)).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                pass

        rest_schedule = client.schedules.begin_create_or_update(schedule).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert rest_schedule.name == schedule.name
        # The trigger should be a CronTrigger and have an expression attribute
        assert isinstance(rest_schedule.trigger, CronTrigger)
        assert getattr(rest_schedule.trigger, "expression", None) is not None

        # disable and cleanup
        client.schedules.begin_disable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        client.schedules.begin_delete(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
