# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

RESOURCE_GROUP_NAME = "teststomover"
STORAGE_MOVER_NAME = "testsm1"
AGENT_NAME = "testagent1"
MISSING_AGENT_NAME = AGENT_NAME + "111"
UPDATED_DESCRIPTION = "This is an updated agent"
UPLOAD_LIMIT_SCHEDULE = {
    "weeklyRecurrences": [
        {
            "startTime": {"hour": 1},
            "endTime": {"hour": 2},
            "days": ["Monday", "Tuesday"],
            "limitInMbps": 100,
        }
    ]
}


def _assert_agent_matches(expected, actual):
    assert actual.name == expected.name
    assert actual.id == expected.id
    assert actual.local_ip_address == expected.local_ip_address


def _assert_upload_limit_schedule(agent):
    recurrences = agent.upload_limit_schedule.weekly_recurrences
    assert len(recurrences) == 1
    recurrence = recurrences[0]
    assert recurrence.limit_in_mbps == 100
    assert recurrence.days[0] == "Monday"
    assert len(recurrence.days) == 2
    assert recurrence.start_time.hour == 1
    assert recurrence.start_time.minute == 0
    assert recurrence.end_time.hour == 2
    assert recurrence.end_time.minute == 0


class TestStorageMoverMgmtAgentsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient)

    @recorded_by_proxy
    def test_agents_get_list_update(self):
        agent = self.client.agents.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            storage_mover_name=STORAGE_MOVER_NAME,
            agent_name=AGENT_NAME,
        )
        agent_again = self.client.agents.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            storage_mover_name=STORAGE_MOVER_NAME,
            agent_name=AGENT_NAME,
        )
        _assert_agent_matches(agent, agent_again)

        agents = list(
            self.client.agents.list(
                resource_group_name=RESOURCE_GROUP_NAME,
                storage_mover_name=STORAGE_MOVER_NAME,
            )
        )
        assert len(agents) >= 1

        updated_agent = self.client.agents.update(
            resource_group_name=RESOURCE_GROUP_NAME,
            storage_mover_name=STORAGE_MOVER_NAME,
            agent_name=AGENT_NAME,
            agent={
                "properties": {
                    "description": UPDATED_DESCRIPTION,
                    "uploadLimitSchedule": UPLOAD_LIMIT_SCHEDULE,
                }
            },
        )
        assert updated_agent.description == UPDATED_DESCRIPTION
        _assert_upload_limit_schedule(updated_agent)

        fetched_agent = self.client.agents.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            storage_mover_name=STORAGE_MOVER_NAME,
            agent_name=AGENT_NAME,
        )
        assert fetched_agent.description == UPDATED_DESCRIPTION
        _assert_upload_limit_schedule(fetched_agent)

        with pytest.raises(ResourceNotFoundError):
            self.client.agents.get(
                resource_group_name=RESOURCE_GROUP_NAME,
                storage_mover_name=STORAGE_MOVER_NAME,
                agent_name=MISSING_AGENT_NAME,
            )
