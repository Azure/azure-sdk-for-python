# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Iterable, Optional, TypeVar

from azure.core.pipeline import policies as core_policies, Pipeline
from azure.core.pipeline.transport import HttpTransport


HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")


class CloudMachinePipelineConfig:
    """Provides the home for all of the configurable policies in the pipeline."""

    def __init__(self, **kwargs: Any) -> None:
        self.api_version: str = kwargs.get("api_version")
        self.authentication_policy = kwargs.get('authentication_policy')
        self.transport: Optional[HttpTransport[HTTPRequestType, HTTPResponseType]] = kwargs.get('transport')
        self.pipeline = self._build_pipeline(**kwargs)

    def _build_pipeline(
        self,
        *,
        transport: Optional[HttpTransport[HTTPRequestType, HTTPResponseType]] = None,
        policies=None,
        per_call_policies=None,
        per_retry_policies=None,
        **kwargs,
    ) -> Pipeline[HTTPRequestType, HTTPResponseType]:
        per_call_policies = per_call_policies or []
        per_retry_policies = per_retry_policies or []

        if policies is None:  # [] is a valid policy list
            policies = [
                core_policies.RequestIdPolicy(**kwargs),
                kwargs.get("headers_policy") or core_policies.HeadersPolicy(**kwargs),
                kwargs.get("user_agent_policy") or core_policies.UserAgentPolicy(**kwargs),
                kwargs.get("proxy_policy") or core_policies.ProxyPolicy(**kwargs),
                #core_policies.ContentDecodePolicy(**kwargs),
            ]
            if isinstance(per_call_policies, Iterable):
                policies.extend(per_call_policies)
            else:
                policies.append(per_call_policies)

            policies.extend(
                [
                    kwargs.get("retry_policy") or core_policies.RetryPolicy(**kwargs),
                    self.authentication_policy,
                    kwargs.get("custom_hook_policy") or core_policies.CustomHookPolicy(**kwargs),
                ]
            )
            if isinstance(per_retry_policies, Iterable):
                policies.extend(per_retry_policies)
            else:
                policies.append(per_retry_policies)

            policies.extend(
                [
                    kwargs.get("logging_policy") or core_policies.NetworkTraceLoggingPolicy(**kwargs),
                    core_policies.DistributedTracingPolicy(**kwargs),
                    kwargs.get("http_logging_policy") or core_policies.HttpLoggingPolicy(**kwargs),
                ]
            )
        else:
            if isinstance(per_call_policies, Iterable):
                per_call_policies_list = list(per_call_policies)
            else:
                per_call_policies_list = [per_call_policies]
            per_call_policies_list.extend(policies)
            policies = per_call_policies_list

            if isinstance(per_retry_policies, Iterable):
                per_retry_policies_list = list(per_retry_policies)
            else:
                per_retry_policies_list = [per_retry_policies]
            if len(per_retry_policies_list) > 0:
                index_of_retry = -1
                for index, policy in enumerate(policies):
                    if isinstance(policy, core_policies.RetryPolicy):
                        index_of_retry = index
                if index_of_retry == -1:
                    raise ValueError(
                        "Failed to add per_retry_policies; no RetryPolicy found in the supplied list of policies. "
                    )
                policies_1 = policies[: index_of_retry + 1]
                policies_2 = policies[index_of_retry + 1 :]
                policies_1.extend(per_retry_policies_list)
                policies_1.extend(policies_2)
                policies = policies_1
        if transport is None:
            # Use private import for better typing, mypy and pyright don't like PEP562
            from azure.core.pipeline.transport._requests_basic import RequestsTransport
            transport = RequestsTransport(**kwargs)
        return Pipeline(transport, policies)
