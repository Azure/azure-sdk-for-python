# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.monitorslis import MonitorSlisMgmtClient, models

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy


# Environment variables expected:
#   SERVICE_GROUP_NAME - name of the pre-existing Service Group
#   AMW_RESOURCE_ID - Azure Monitor Workspace resource ID (destination)
#   MANAGED_IDENTITY_RESOURCE_ID - User-Assigned Managed Identity resource ID
#   SOURCE_AMW_RESOURCE_ID - Source Azure Monitor Workspace resource ID
#   SOURCE_MANAGED_IDENTITY_RESOURCE_ID - Source Managed Identity resource ID
SERVICE_GROUP_NAME = os.environ.get("SERVICE_GROUP_NAME", "arm-sdk-tests-sg")
AMW_RESOURCE_ID = os.environ.get(
    "AMW_RESOURCE_ID",
    "/subscriptions/6820e35f-0fe6-4af3-aad2-27414fa82621/resourceGroups/mfrei/providers/microsoft.monitor/accounts/streaming-3p-slo-am2cbn-eastus2euap-1",
)
MANAGED_IDENTITY_RESOURCE_ID = os.environ.get(
    "MANAGED_IDENTITY_RESOURCE_ID",
    "/subscriptions/6820e35f-0fe6-4af3-aad2-27414fa82621/resourceGroups/mfrei/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mfrei-test-user-managed-identity",
)
SOURCE_AMW_RESOURCE_ID = os.environ.get("SOURCE_AMW_RESOURCE_ID", AMW_RESOURCE_ID)
SOURCE_MANAGED_IDENTITY_RESOURCE_ID = os.environ.get(
    "SOURCE_MANAGED_IDENTITY_RESOURCE_ID", MANAGED_IDENTITY_RESOURCE_ID
)

SLI_DESCRIPTION = "Live test SLI - measures latency of test API"


class TestSliCrudLive(AzureMgmtRecordedTestCase):
    """Live CRUD test for Microsoft.Monitor/slis resource."""

    def setup_method(self, method):
        self.client = self.create_mgmt_client(MonitorSlisMgmtClient)
        self.sli_name = self.get_resource_name("pysli")

    def _get_sli_body(self):
        """Return a valid SLI resource body for create/update."""
        return models.Sli(
            properties=models.SliResource(
                description=SLI_DESCRIPTION,
                category="Latency",
                evaluation_type="WindowBased",
                enable_alert=True,
                destination_amw_accounts=[
                    models.AmwAccount(
                        resource_id=AMW_RESOURCE_ID,
                        identity=MANAGED_IDENTITY_RESOURCE_ID,
                    )
                ],
                baseline_properties=models.BaselineProperties(
                    baseline=models.Baseline(
                        value=99,
                        evaluation_period_days=30,
                        evaluation_calculation_type="CalendarDays",
                    )
                ),
                sli_properties=models.SliProperties(
                    window_uptime_criteria=models.WindowUptimeCriteria(target=95, comparator="GreaterThanOrEqual"),
                    signals=models.Signal(
                        signal_sources=[
                            models.SignalSource(
                                signal_source_id="A",
                                source_amw_account_managed_identity=SOURCE_MANAGED_IDENTITY_RESOURCE_ID,
                                source_amw_account_resource_id=SOURCE_AMW_RESOURCE_ID,
                                metric_namespace="TestMetrics",
                                metric_name="TestLatency",
                                filters=[
                                    models.Condition(
                                        dimension_name="ApiName",
                                        operator="Equal",
                                        value="TestApi",
                                    )
                                ],
                                spatial_aggregation=models.SpatialAggregation(
                                    type="Average",
                                    dimensions=["Region"],
                                ),
                                temporal_aggregation=models.TemporalAggregation(
                                    type="Average",
                                    window_size_minutes=5,
                                ),
                            )
                        ],
                        signal_formula="A",
                    ),
                ),
            )
        )

    @recorded_by_proxy
    def test_sli_crud_lifecycle(self):
        """Test full CRUD lifecycle: Create → Get → Delete → Get (expect 404)."""
        # Step 1: Create SLI
        create_response = self.client.slis.create_or_update(
            service_group_name=SERVICE_GROUP_NAME,
            sli_name=self.sli_name,
            resource=self._get_sli_body(),
        )
        assert create_response is not None
        assert create_response.name == self.sli_name
        assert create_response.properties is not None
        assert create_response.properties.description == SLI_DESCRIPTION

        # Step 2: Get SLI - verify it exists
        get_response = self.client.slis.get(
            service_group_name=SERVICE_GROUP_NAME,
            sli_name=self.sli_name,
        )
        assert get_response is not None
        assert get_response.name == self.sli_name
        assert get_response.properties is not None
        assert get_response.properties.description == SLI_DESCRIPTION
        assert get_response.properties.sli_properties is not None
        assert get_response.properties.sli_properties.window_uptime_criteria is not None

        # Step 3: Delete SLI
        self.client.slis.delete(
            service_group_name=SERVICE_GROUP_NAME,
            sli_name=self.sli_name,
        )

        # Step 4: Get SLI - expect 404
        with pytest.raises(ResourceNotFoundError):
            self.client.slis.get(
                service_group_name=SERVICE_GROUP_NAME,
                sli_name=self.sli_name,
            )

