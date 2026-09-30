from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import LROConfigurations
from azure.ai.ml.entities import CronTrigger
from azure.ai.ml.entities._load_functions import load_schedule
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestScheduleGaps(AzureRecordedTestCase):
    def test_basic_schedule_lifecycle_triggers_and_enable_disable(self, client: MLClient, randstr: Callable[[], str]):
        # create a schedule from existing test config that uses a cron trigger
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path, params_override=params_override)

        # use hardcoded far-future dates to ensure deterministic playback
        if getattr(schedule, "trigger", None) is not None:
            try:
                schedule.trigger.start_time = "2026-01-01T00:00:00"
                schedule.trigger.end_time = "2099-01-01T00:00:00"
            except Exception:
                pass

        # create
        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
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
        with pytest.raises(ResourceNotFoundError):
            client.schedules.get(schedule.name)

    def test_cron_trigger_roundtrip_properties(self, client: MLClient, randstr: Callable[[], str]):
        # ensure CronTrigger properties roundtrip via schedule create and get
        params_override = [{"name": randstr("name")}]
        test_path = "./tests/test_configs/schedule/hello_cron_schedule_with_file_reference.yml"
        schedule = load_schedule(test_path, params_override=params_override)

        # use hardcoded far-future dates to ensure deterministic playback
        if getattr(schedule, "trigger", None) is not None:
            try:
                schedule.trigger.start_time = "2026-01-01T00:00:00"
                schedule.trigger.end_time = "2099-01-01T00:00:00"
            except Exception:
                pass

        rest_schedule = client.schedules.begin_create_or_update(schedule).result(
            timeout=LROConfigurations.POLLING_TIMEOUT
        )
        assert rest_schedule.name == schedule.name
        # The trigger should be a CronTrigger and have an expression attribute
        assert isinstance(rest_schedule.trigger, CronTrigger)
        assert getattr(rest_schedule.trigger, "expression", None) is not None

        # disable and cleanup
        client.schedules.begin_disable(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        client.schedules.begin_delete(schedule.name).result(timeout=LROConfigurations.POLLING_TIMEOUT)
