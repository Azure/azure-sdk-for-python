from typing import Callable
import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestScheduleOperationsGaps(AzureRecordedTestCase):
    def test_trigger_nonexistent_schedule_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Attempt to trigger a schedule that does not exist. Service is expected to return an error which
        # surfaces as an exception from the SDK. This exercises the trigger code path that constructs
        # a TriggerOnceRequest and calls the schedule_trigger_service_client.
        name = randstr("nonexistent-sched")
        with pytest.raises(Exception):
            client.schedules.trigger(name, schedule_time="2024-02-19T00:00:00")
