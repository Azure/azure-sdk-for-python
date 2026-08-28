# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils.aio import recorded_by_proxy_async

from azure.ai.projects.models import (
    ShellToolboxTool,
    ToolboxShellContainerAutoEnvironment,
    ToolboxShellNetworkPolicyDisabled,
    ToolboxToolType,
    WebIQPreviewToolboxTool,
)

from test_base import TestBase, servicePreparer


@pytest.mark.skip(reason="TODO(shell and WebIQ toolbox tools): enable after Test Proxy recordings are added.")
class TestToolboxesAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_shell_and_web_iq_tools_async(self, **kwargs) -> None:
        connection_id = kwargs.get("web_iq_project_connection_id")
        assert isinstance(connection_id, str)

        toolbox_name = "test-toolbox-shell-web-iq"
        created = None

        async with self.create_async_client(allow_preview=True, **kwargs) as project_client:
            try:
                try:
                    await project_client.toolboxes.delete(name=toolbox_name)
                except ResourceNotFoundError:
                    pass

                created = await project_client.toolboxes.create_version(
                    name=toolbox_name,
                    description="Toolbox containing shell and WebIQ tools.",
                    tools=[
                        ShellToolboxTool(
                            name="shell",
                            environment=ToolboxShellContainerAutoEnvironment(
                                memory_limit="4g",
                                network_policy=ToolboxShellNetworkPolicyDisabled(),
                            ),
                        ),
                        WebIQPreviewToolboxTool(
                            name="web_iq",
                            project_connection_id=connection_id,
                            server_label="web-iq",
                            require_approval="always",
                        ),
                    ],
                )
                assert created.name == toolbox_name
                assert created.version

                fetched = await project_client.toolboxes.get_version(name=toolbox_name, version=created.version)
                tool_types = {tool.type for tool in fetched.tools or []}
                assert ToolboxToolType.SHELL in tool_types
                assert ToolboxToolType.WEB_IQ_PREVIEW in tool_types
            finally:
                if created is not None:
                    await project_client.toolboxes.delete(name=toolbox_name)
