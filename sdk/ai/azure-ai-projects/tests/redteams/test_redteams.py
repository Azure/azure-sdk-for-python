# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RedTeam,
    AzureOpenAIModelConfiguration,
    AttackStrategy,
    RiskCategory,
)
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy


class TestRedTeams(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_redteams.py::TestRedTeams::test_red_teams -s
    @servicePreparer()
    @recorded_by_proxy
    def test_red_teams(self, **kwargs):

        connection_name = self.test_redteams_params["connection_name"]
        model_deployment_name = self.test_redteams_params["model_deployment_name"]

        with self.create_client(**kwargs) as project_client:

            # [START red_team_sample]
            print("Creating a Red Team scan for direct model testing")

            # Create target configuration for testing an Azure OpenAI model
            target_config = AzureOpenAIModelConfiguration(
                model_deployment_name=f"{connection_name}/{model_deployment_name}"
            )

            # Create the Red Team configuration
            red_team = RedTeam(
                attack_strategies=[AttackStrategy.BASE64],
                risk_categories=[RiskCategory.VIOLENCE],
                display_name="redteamtest1",  # Use a simpler name
                target=target_config,
            )

            # Create and run the Red Team scan
            red_team_response = project_client.red_teams.create(red_team=red_team)
            print(f"Red Team scan created with scan name: {red_team_response.name}")
            TestBase.validate_red_team_response(
                red_team_response, expected_attack_strategies=1, expected_risk_categories=1
            )

            print("Getting Red Team scan details")
            # Use the name returned by the create operation for the get call
            get_red_team_response = project_client.red_teams.get(name=red_team_response.name)
            print(f"Red Team scan status: {get_red_team_response.status}")
            TestBase.validate_red_team_response(
                get_red_team_response, expected_attack_strategies=1, expected_risk_categories=1
            )

            print("Listing all Red Team scans")
            for scan in project_client.red_teams.list():
                print(f"Found scan: {scan.name}, Status: {scan.status}")
                TestBase.validate_red_team_response(scan)
