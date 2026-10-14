# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Recordable service scenarios adapted from the Azure PowerShell EdgeAction tests."""

import base64
import io
import zipfile
from contextlib import contextmanager

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.edgeactions import EdgeActionsMgmtClient, models
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

from edgeactions_test_settings import RESOURCE_GROUP_OPTIONS

pytestmark = pytest.mark.usefixtures("add_sanitizers")

HANDLER = b"function handler(event) { return event; }"


def version_code(deployment_type):
    content = HANDLER
    if deployment_type == "zip":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            # Fixed ZIP metadata keeps the request identical during playback.
            archive.writestr(zipfile.ZipInfo("handler.js", date_time=(1980, 1, 1, 0, 0, 0)), HANDLER)
        content = buffer.getvalue()
    return base64.b64encode(content).decode()


def cleanup_edge_action(client, resource_group_name, name):
    try:
        client.edge_actions.get(resource_group_name, name)
    except ResourceNotFoundError:
        return
    filters = client.edge_action_execution_filters
    for item in filters.list_by_edge_action(resource_group_name, name):
        filters.begin_delete(resource_group_name, name, item.name).result()
    versions = list(client.edge_action_versions.list_by_edge_action(resource_group_name, name))
    assert all(version.properties.is_default_version in ("True", "False") for version in versions)
    assert sum(version.properties.is_default_version == "True" for version in versions) <= 1
    # A default version can be deleted only after the other versions.
    for version in sorted(versions, key=lambda item: item.properties.is_default_version == "True"):
        client.edge_action_versions.begin_delete(resource_group_name, name, version.name).result()
    client.edge_actions.begin_delete(resource_group_name, name).result()


class TestEdgeActionsLifecycle(AzureMgmtRecordedTestCase):
    @contextmanager
    def edge_action(self, resource_group_name):
        name = self.get_resource_name("eapython")
        with self.create_mgmt_client(EdgeActionsMgmtClient) as client:
            try:
                client.edge_actions.get(resource_group_name, name)
            except ResourceNotFoundError:
                pass
            else:
                pytest.fail(f"Refusing to overwrite existing EdgeAction {resource_group_name}/{name}")
            try:
                client.edge_actions.begin_create(
                    resource_group_name,
                    name,
                    models.EdgeAction(
                        location="global",
                        sku=models.SkuType(name="Standard", tier="Standard"),
                        tags={"purpose": "initial", "remove-me": "initial"},
                    ),
                ).result()
                yield client, name
            finally:
                cleanup_edge_action(client, resource_group_name, name)

    @RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    @recorded_by_proxy
    def test_edge_action_tag_updates(self, resource_group):
        rg = resource_group.name
        with self.edge_action(rg) as (client, name):
            before = client.edge_actions.get(rg, name)
            assert before.location == "global"
            assert before.tags == {"purpose": "initial", "remove-me": "initial"}
            assert name in [action.name for action in client.edge_actions.list_by_resource_group(rg)]

            with pytest.raises(HttpResponseError, match="PATCH request body must contain at least one property") as error:
                client.edge_actions.begin_update(rg, name, models.EdgeActionUpdate()).result()
            assert error.value.status_code == 400
            assert client.edge_actions.get(rg, name).tags == before.tags

            for tags in ({"purpose": "updated"}, {}):
                client.edge_actions.begin_update(rg, name, models.EdgeActionUpdate(tags=tags)).result()
                updated = client.edge_actions.get(rg, name)
                assert updated.tags == tags
                assert updated.location == before.location
                assert updated.sku == before.sku

            for invalid_update in (
                {"tags": None},
                {"sku": None},
                {"sku": {"name": before.sku.name, "tier": before.sku.tier}},
            ):
                with pytest.raises(HttpResponseError) as error:
                    client.edge_actions.begin_update(rg, name, invalid_update).result()
                assert error.value.status_code == 400
            assert client.edge_actions.get(rg, name).tags == {}

        with pytest.raises(ResourceNotFoundError):
            with self.create_mgmt_client(EdgeActionsMgmtClient) as client:
                client.edge_actions.get(rg, name)

    @RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    @recorded_by_proxy
    def test_file_versions_and_execution_filters(self, resource_group):
        self.versions_and_execution_filters(resource_group, "file")

    @RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    @recorded_by_proxy
    def test_zip_versions_and_execution_filters(self, resource_group):
        self.versions_and_execution_filters(resource_group, "zip")

    def versions_and_execution_filters(self, resource_group, deployment_type):
        rg = resource_group.name
        with self.edge_action(rg) as (client, name):
            versions = client.edge_action_versions
            for version in ("v1", "v2"):
                versions.begin_create(
                    rg,
                    name,
                    version,
                    models.EdgeActionVersion(
                        location="global",
                        properties=models.EdgeActionVersionProperties(
                            deployment_type=deployment_type, is_default_version="False"
                        ),
                    ),
                ).result()
                versions.begin_deploy_version_code(
                    rg, name, version, models.VersionCode(name=version, content=version_code(deployment_type))
                ).result()
                deployed = versions.get(rg, name, version)
                assert deployed.properties.provisioning_state == "Succeeded"
                assert deployed.properties.validation_status == "Succeeded"
                assert deployed.properties.deployment_type == deployment_type

            first = versions.get(rg, name, "v1")
            second = versions.get(rg, name, "v2")
            assert first.properties.is_default_version == "True"
            assert second.properties.is_default_version == "False"
            assert {version.name for version in versions.list_by_edge_action(rg, name)} == {"v1", "v2"}

            code = versions.begin_get_version_code(rg, name, "v1").result()
            decoded = base64.b64decode(code.content)
            # The service may return a ZIP package even for a file deployment.
            if zipfile.is_zipfile(io.BytesIO(decoded)):
                with zipfile.ZipFile(io.BytesIO(decoded)) as archive:
                    assert HANDLER in [archive.read(item) for item in archive.infolist() if not item.is_dir()]
            else:
                assert decoded == HANDLER

            versions.begin_update(rg, name, "v1", models.EdgeActionVersionUpdate(tags={"purpose": "updated"})).result()
            updated = versions.get(rg, name, "v1")
            assert updated.tags == {"purpose": "updated"}
            assert updated.properties.deployment_type == first.properties.deployment_type
            assert updated.properties.is_default_version == first.properties.is_default_version

            versions.begin_update(
                rg,
                name,
                "v1",
                models.EdgeActionVersionUpdate(
                    properties=models.EdgeActionVersionUpdateProperties(
                        deployment_type=deployment_type, is_default_version="True"
                    )
                ),
            ).result()
            for properties in (
                {"isDefaultVersion": "False"},
                {"deploymentType": "zip" if deployment_type == "file" else "file"},
            ):
                with pytest.raises(HttpResponseError) as error:
                    versions.begin_update(rg, name, "v1", {"properties": properties}).result()
                assert error.value.status_code == 400

            versions.begin_swap_default(rg, name, "v2").result()
            assert versions.get(rg, name, "v1").properties.is_default_version == "False"
            assert versions.get(rg, name, "v2").properties.is_default_version == "True"

            filters = client.edge_action_execution_filters
            filters.begin_create(
                rg,
                name,
                "sdkfilter",
                models.EdgeActionExecutionFilter(
                    location="global",
                    properties=models.EdgeActionExecutionFilterProperties(
                        version_id=first.id,
                        execution_filter_identifier_header_name="x-sdk-test",
                        execution_filter_identifier_header_value="initial",
                    ),
                ),
            ).result()
            initial_filter = filters.get(rg, name, "sdkfilter")
            assert initial_filter.properties.version_id.lower() == first.id.lower()
            assert {item.name for item in filters.list_by_edge_action(rg, name)} == {"sdkfilter"}

            filters.begin_update(
                rg,
                name,
                "sdkfilter",
                models.EdgeActionExecutionFilterUpdate(
                    tags={"purpose": "updated"},
                    properties=models.EdgeActionExecutionFilterUpdateProperties(
                        version_id=second.id,
                        execution_filter_identifier_header_name="x-sdk-test-updated",
                        execution_filter_identifier_header_value="updated",
                    ),
                ),
            ).result()
            updated_filter = filters.get(rg, name, "sdkfilter")
            assert updated_filter.tags == {"purpose": "updated"}
            assert updated_filter.properties.version_id.lower() == second.id.lower()
            assert updated_filter.properties.execution_filter_identifier_header_name == "x-sdk-test-updated"
            assert updated_filter.properties.execution_filter_identifier_header_value == "updated"

            filters.begin_delete(rg, name, "sdkfilter").result()
            assert list(filters.list_by_edge_action(rg, name)) == []
            for version in ("v1", "v2"):
                versions.begin_delete(rg, name, version).result()
            assert list(versions.list_by_edge_action(rg, name)) == []
