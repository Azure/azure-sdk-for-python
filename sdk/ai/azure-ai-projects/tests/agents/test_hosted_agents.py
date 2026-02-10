# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase  # , servicePreparer

# from devtools_testutils import recorded_by_proxy
# from azure.ai.projects.models import AgentReference, PromptAgentDefinition


class TestHostedAgents(TestBase):

    # @servicePreparer()
    # @recorded_by_proxy
    def test_hosted_agent(self, **kwargs):
        """
        Test Hosted Agents and all container operations.

        Routes used in this test:

        Action REST API Route                                                              Client Method
        ------+---------------------------------------------------------------------------+-----------------------------------

        # Setup:

        # Test focus:
        GET    /agents/{agent_name}/operations                                              list_container_operations
        GET    /agents/{agent_name}/operations/{operation_id}                               retrieve_container_operation
        GET    /agents/{agent_name}/versions/{agent_version}/containers/default             retrieve_container
        GET    /agents/{agent_name}/versions/{agent_version}/containers/default/operations  list_version_container_operations
        POST   /agents/{agent_name}/versions/{agent_version}/containers/default:start       start_container
        POST   /agents/{agent_name}/versions/{agent_version}/containers/default:stop        stop_container
        POST   /agents/{agent_name}/versions/{agent_version}/containers/default:update      update_container
        POST   /agents/{agent_name}/versions/{agent_version}/containers/default:delete      delete_container

        # Teardown:

        """

        # TODO: Add tests!
        pass
