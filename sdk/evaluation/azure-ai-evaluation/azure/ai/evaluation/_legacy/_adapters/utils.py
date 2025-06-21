# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Final, Optional
from typing_extensions import TypeAlias


try:
    from promptflow._utils.user_agent_utils import ClientUserAgentUtil
    from promptflow._utils.async_utils import async_run_allowing_running_loop
    from promptflow._cli._utils import get_workspace_triad_from_local
except ImportError:
    from azure.ai.evaluation._legacy._batch_engine._utils_deprecated import (
        async_run_allowing_running_loop,
    )
    from azure.ai.evaluation._evaluate._utils import AzureMLWorkspace

    class ClientUserAgentUtil:
        @staticmethod
        def append_user_agent(user_agent: Optional[str]):
            # TODO ralphe: implement?
            pass

    def get_workspace_triad_from_local() -> AzureMLWorkspace:
        return AzureMLWorkspace("", "", "")
