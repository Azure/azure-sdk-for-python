# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Informational-operations tests for ``Microsoft.FileShares``."""

from azure.mgmt.fileshares import models as fs_models

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    LOCATION,
    RESOURCE_GROUP,
    build_share_payload,
    make_client,
    safe_delete_share,
    var_share,
)


class TestFileSharesInformational(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_get_limits(self):
        response = self.client.informational_operations.get_limits(location=LOCATION)
        assert response is not None
        assert response.properties is not None

    @recorded_by_proxy
    def test_get_usage_data(self):
        response = self.client.informational_operations.get_usage_data(location=LOCATION)
        assert response is not None
        assert response.properties is not None

    @recorded_by_proxy
    def test_get_provisioning_recommendation(self):
        request = fs_models.FileShareProvisioningRecommendationRequest(
            properties=fs_models.FileShareProvisioningRecommendationInput(
                provisioned_storage_gi_b=1000,
            ),
        )
        response = self.client.informational_operations.get_provisioning_recommendation(
            location=LOCATION,
            body=request,
        )
        assert response is not None
        assert response.properties is not None
        assert response.properties.provisioned_io_per_sec > 0
        assert response.properties.provisioned_throughput_mi_b_per_sec > 0
        assert len(response.properties.available_redundancy_options) > 0

    @recorded_by_proxy
    def test_check_name_availability_for_unique_name(self, variables):
        name = var_share(variables, "share_name", "unique-never-created")
        request = fs_models.CheckNameAvailabilityRequest(
            name=name,
            type="Microsoft.FileShares/fileShares",
        )
        response = self.client.file_shares.check_name_availability(
            location=LOCATION,
            body=request,
        )
        assert response is not None
        assert response.name_available is True
        return variables

    @recorded_by_proxy
    def test_check_name_availability_for_taken_name(self, variables):
        """Create a share, then assert its name is reported as not available."""
        name = var_share(variables, "share_name", "taken")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()

            request = fs_models.CheckNameAvailabilityRequest(
                name=name,
                type="Microsoft.FileShares/fileShares",
            )
            response = self.client.file_shares.check_name_availability(
                location=LOCATION,
                body=request,
            )
            assert response is not None
            assert response.name_available is False
            assert response.reason is not None
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables
