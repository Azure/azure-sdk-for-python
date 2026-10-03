# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from typing import TypeVar

import pytest

from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import LROPoller
from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.models import (
    CloudValidation,
    CloudValidationProperties,
    CloudValidationUpdate,
    CloudValidationUpdateProperties,
)
from azure.mgmt.resource.resources import ResourceManagementClient
from devtools_testutils import ResourceGroupPreparer, recorded_by_proxy

from _cloud_validation_testcase import (
    CloudValidationTestCase,
    OPERATION_TIMEOUT,
    PlatformValidationPreparer,
    wait_for_managed_group_deletion,
)

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")


def complete_operation(poller: LROPoller[_ResultT]) -> _ResultT:
    result = poller.result(timeout=OPERATION_TIMEOUT)
    assert poller.done(), "CloudValidation operation did not finish within the timeout."
    return result


class TestCloudValidations(CloudValidationTestCase):
    @PlatformValidationPreparer()
    @ResourceGroupPreparer(name_prefix="platformvalidation", random_name_enabled=True, location="eastus")
    @recorded_by_proxy
    def test_cloud_validation_lifecycle(self, resource_group, platformvalidation_location: str) -> None:
        group = resource_group.name
        location = platformvalidation_location
        name = self.get_resource_name("pysdkrec")
        tags = {"sdk-test": name, "phase": "created"}
        description = "Python SDK recorded CloudValidation"

        managed_group = f"{name}-mrg"
        with (
            self.create_mgmt_client(PlatformValidationMgmtClient) as client,
            self.create_mgmt_client(ResourceManagementClient) as resources,
        ):
            operations = client.cloud_validations
            # Refuse to overwrite a resource left behind by an earlier live run.
            with pytest.raises(ResourceNotFoundError) as missing:
                operations.get(group, name)
            assert missing.value.status_code == 404
            assert not resources.resource_groups.check_existence(
                managed_group
            ), "Managed resource group already exists."

            deleted = False
            try:
                created = complete_operation(
                    operations.begin_create_or_update(
                        group,
                        name,
                        CloudValidation(
                            location=location,
                            tags=tags,
                            properties=CloudValidationProperties(description=description),
                        ),
                    )
                )
                self.assert_resource(created, group, name, location, description, tags)
                self.assert_resource(operations.get(group, name), group, name, location, description, tags)
                self.assert_list_contains_resource(list(operations.list_by_resource_group(group)), group, name)
                self.assert_list_contains_resource(list(operations.list_by_subscription()), group, name)

                tags = {"sdk-test": name, "phase": "updated"}
                description = "Updated Python SDK recorded CloudValidation"
                updated = complete_operation(
                    operations.begin_update(
                        group,
                        name,
                        CloudValidationUpdate(
                            tags=tags, properties=CloudValidationUpdateProperties(description=description)
                        ),
                    )
                )
                self.assert_resource(updated, group, name, location, description, tags)
                self.assert_resource(operations.get(group, name), group, name, location, description, tags)

                self.delete_owned_resource(client, group, name)
                deleted = True
            finally:
                try:
                    if not deleted:
                        self.delete_owned_resource(client, group, name, allow_missing=True)
                finally:
                    wait_for_managed_group_deletion(resources, managed_group)

    def delete_owned_resource(
        self, client: PlatformValidationMgmtClient, group: str, name: str, *, allow_missing: bool = False
    ) -> None:
        try:
            resource = client.cloud_validations.get(group, name)
        except ResourceNotFoundError as error:
            if not allow_missing or error.status_code != 404:
                raise
            _LOGGER.warning(
                "Cleanup found no CloudValidation. If creation failed or timed out, check for late provisioning."
            )
            return
        self.assert_identity(resource, group, name)
        assert resource.tags and resource.tags.get("sdk-test") == name, "Refusing to delete an unowned resource."
        complete_operation(client.cloud_validations.begin_delete(group, name))
        with pytest.raises(ResourceNotFoundError) as missing:
            client.cloud_validations.get(group, name)
        assert missing.value.status_code == 404

    @PlatformValidationPreparer()
    @ResourceGroupPreparer(name_prefix="platformvalidation", random_name_enabled=True, location="eastus")
    @recorded_by_proxy
    def test_get_missing_cloud_validation_raises_not_found(self, resource_group) -> None:
        with self.create_mgmt_client(PlatformValidationMgmtClient) as client:
            with pytest.raises(ResourceNotFoundError) as missing:
                client.cloud_validations.get(resource_group.name, self.get_resource_name("pysdkmissing"))
            assert missing.value.status_code == 404
