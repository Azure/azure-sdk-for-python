# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase  # , servicePreparer
import pytest

from azure.ai.projects.models import HostedAgentDefinition

# from devtools_testutils import recorded_by_proxy
# from azure.ai.projects.models import PromptAgentDefinition


@pytest.mark.skip(reason="Not yet implemented")
class TestHostedAgents(TestBase):

    # @servicePreparer()
    # @recorded_by_proxy
    def test_hosted_agent(self, **kwargs):
        # TODO: Add tests!
        pass


@pytest.mark.parametrize("enable_memory_snapshot", [True, False])
def test_hosted_agent_memory_snapshot_round_trip(enable_memory_snapshot):
    definition = HostedAgentDefinition(cpu="1", memory="2Gi", enable_memory_snapshot=enable_memory_snapshot)

    payload = definition.as_dict()
    assert payload["enable_memory_snapshot"] is enable_memory_snapshot
    assert HostedAgentDefinition(payload).enable_memory_snapshot is enable_memory_snapshot


def test_hosted_agent_memory_snapshot_is_optional():
    definition = HostedAgentDefinition(cpu="1", memory="2Gi")

    assert definition.enable_memory_snapshot is None
    assert "enable_memory_snapshot" not in definition.as_dict()
