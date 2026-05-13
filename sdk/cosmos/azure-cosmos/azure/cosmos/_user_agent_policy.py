# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.policies._universal import HTTPRequestType

from azure.cosmos._backend.constants import REQUEST_OPTION_BACKEND_KEY
from azure.cosmos._utils import get_user_agent_features


class CosmosUserAgentPolicy(UserAgentPolicy):
    """Custom user agent policy for Cosmos DB that appends feature flags to the user agent string.

    This policy extends the standard UserAgentPolicy to include Cosmos-specific feature flags
    (e.g., circuit breaker, per-partition automatic failover) in the user agent header for
    debugging and telemetry purposes.
    """

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Modifies the User-Agent header before the request is sent.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        options_dict = request.context.options
        # Compose any per-request user-agent suffixes. Two sources today:
        #   1. Cosmos feature flags derived from the global endpoint manager
        #      (existing behavior — circuit breaker, PPAF, etc.).
        #   2. The backend that handled this request ("core-python" or "rust"),
        #      stamped per-request from the dispatch site so server-side
        #      logs reflect the path the call actually took even when a
        #      Rust-default client falls back to core-python for a single call.
        suffix_parts = []
        if "global_endpoint_manager" in options_dict:
            global_endpoint_manager = options_dict["global_endpoint_manager"]
            user_agent_features = get_user_agent_features(global_endpoint_manager)
            if len(user_agent_features) > 0:
                suffix_parts.append(user_agent_features)
        backend_name = options_dict.get(REQUEST_OPTION_BACKEND_KEY)
        if backend_name:
            suffix_parts.append("backend={}".format(backend_name))
        if suffix_parts:
            user_agent = "{} {}".format(self._user_agent, " ".join(suffix_parts))
            options_dict["user_agent"] = user_agent
            options_dict["user_agent_overwrite"] = True
        super().on_request(request)
