from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import LROConfigurations
from azure.ai.ml.entities._monitoring.schedule import MonitorSchedule
from azure.ai.ml.exceptions import ScheduleException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestScheduleOperationsGaps(AzureRecordedTestCase):
    def test_monitor_schedule_without_target_or_signals_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """
        Covers branches where MonitorSchedule.create_monitor.monitoring_target is falsy and
        monitoring_signals is None, which should raise a ScheduleException without making
        any network calls.
        Corresponds to markers around the early validation and raise in _resolve_monitor_schedule_arm_id.
        """
        # Create a minimal MonitorSchedule whose create_monitor has no monitoring_target and no monitoring_signals
        name = randstr("name")
        create_monitor = type("CM", (), {"monitoring_target": None, "monitoring_signals": None})()
        schedule = MonitorSchedule(name=name, create_monitor=create_monitor, trigger=None)  # type: ignore[arg-type]

        with pytest.raises(ScheduleException) as e:
            client.schedules.begin_create_or_update(schedule).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert "An ARM id for a deployment with data collector enabled for model inputs and outputs must be given" in str(e.value)

    def test_monitor_schedule_with_empty_signals_and_no_target_raises_same(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """
        Another coverage for the branch when monitoring_signals is falsy and there is no deployment target info.
        Repeats the validation path to ensure deterministic behavior in varied environments.
        """
        name = randstr("name")
        # create_monitor object with empty dict-like monitoring_signals (falsy) and no monitoring_target
        create_monitor = type("CM", (), {"monitoring_target": None, "monitoring_signals": {}})()
        # Force monitoring_signals to be falsy by setting to None after construction to hit the same branch
        create_monitor.monitoring_signals = None
        schedule = MonitorSchedule(name=name, create_monitor=create_monitor, trigger=None)  # type: ignore[arg-type]

        with pytest.raises(ScheduleException) as e:
            client.schedules.begin_create_or_update(schedule).result(timeout=LROConfigurations.POLLING_TIMEOUT)
        assert "An ARM id for a deployment with data collector enabled for model inputs and outputs must be given" in str(e.value)

    def test_trigger_with_nonexistent_schedule_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """
        Validate that triggering a schedule that does not exist surfaces an exception from the service.
        This exercises the Schedule.trigger code path where schedule_time is defaulted/used and the trigger
        request is sent to the service.
        """
        name = randstr("nonexistent")
        # Provide explicit schedule_time to ensure the TriggerOnceRequest path is taken inside trigger()
        with pytest.raises(Exception):
            client.schedules.trigger(name, schedule_time="2099-01-01T00:00:00")

    def test_trigger_nonexistent_schedule_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("nonexistingschedule")
        with pytest.raises(Exception) as e:
            client.schedules.trigger(name, schedule_time="2024-02-19T00:00:00")
        # service should report schedule not found or equivalent error
        assert e is not None
