# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.policies._universal import HTTPRequestType

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
        # Add relevant enabled features to user agent for debugging
        if "global_endpoint_manager" in options_dict:
            global_endpoint_manager = options_dict.pop("global_endpoint_manager")
            user_agent_features = get_user_agent_features(global_endpoint_manager)
            if len(user_agent_features) > 0:
                user_agent = "{} {}".format(self._user_agent, user_agent_features)
                options_dict["user_agent"] = user_agent
                options_dict["user_agent_overwrite"] = True
        super().on_request(request)
