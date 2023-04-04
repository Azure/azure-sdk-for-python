# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import TYPE_CHECKING, Any, Optional

from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    AsyncRetryPolicy,
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    UserAgentPolicy,
)
from azure.iot.deviceprovisioningservice._generated import VERSION
from azure.iot.deviceprovisioningservice._generated.aio import (
    ProvisioningServiceClient as GeneratedProvisioningServiceClient,
)
from azure.iot.deviceprovisioningservice.auth import SharedKeyCredentialPolicy

from ..util.connection_strings import parse_iot_dps_connection_string

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential


class ProvisioningServiceClient(
    object
):  # pylint: disable=client-accepts-api-version-keyword
    """
    API for connecting to, and conducting operations on a Device Provisioning Service instance

    :param str endpoint: The HTTP endpoint of the Device Provisioning Service instance
    :param credential: The credential type used to authenticate with the Device Provisioning Service instance
    """

    def __init__(
        self,
        endpoint: str,
        credential: Optional["AsyncTokenCredential"] = None,
        **kwargs: Any,
    ) -> None:
        # Validate endpoint
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Endpoint URL must be a string.")
        endpoint = endpoint.rstrip("/")

        if not credential:
            raise ValueError("Credential cannot be None")

        self._pipeline = self._create_pipeline(
            credential=credential, base_url=endpoint, **kwargs
        )

        # Generate protocol client
        self._runtime_client = GeneratedProvisioningServiceClient(
            credential=credential, endpoint=endpoint, pipeline=self._pipeline, **kwargs
        )

        self.individual_enrollment = self._runtime_client.individual_enrollment
        self.enrollment_group = self._runtime_client.enrollment_group
        self.device_registration_state = self._runtime_client.device_registration_state

    @classmethod
    def from_connection_string(
        cls, connection_string: str, **kwargs: Any
    ) -> "ProvisioningServiceClient":
        """
        Create a Provisioning Service Client from a connection string

        :param str connection_string: The connection string for the Device Provisioning Service instance
        :return: A new instance of :class:`ProvisioningServiceClient
         <azure.iot.deviceprovisioningservice.aio.ProvisioningServiceClient>`
        :rtype: :class:`ProvisioningServiceClient
         <azure.iot.deviceprovisioningservice.aio.ProvisioningServiceClient>`
        :raises: ValueError if connection string is invalid
        """
        cs_args = parse_iot_dps_connection_string(connection_string=connection_string)
        host_name, shared_access_key_name, shared_access_key = (
            cs_args["HostName"],
            cs_args["SharedAccessKeyName"],
            cs_args["SharedAccessKey"],
        )
        # Create credential from keys
        credential = SharedKeyCredentialPolicy(
            host_name, shared_access_key_name, shared_access_key
        )

        return cls(endpoint=host_name, credential=credential, **kwargs)  # type: ignore

    def _create_pipeline(
        self,
        credential: "AsyncTokenCredential",
        **kwargs: Any,
    ) -> AsyncPipeline:
        transport = kwargs.get("transport")
        user_agent_policy = kwargs.get("user_agent_policy") or UserAgentPolicy(
            sdk_moniker=f"az-iot-dps-python/{VERSION}", **kwargs
        )

        # Choose appropriate credential policy
        self._credential_policy = None  # type: ignore
        if hasattr(credential, "get_token"):
            self._credential_policy = AsyncBearerTokenCredentialPolicy(  # type: ignore
                credential, "https://azure-devices-provisioning.net/.default"
            )
        elif isinstance(credential, SharedKeyCredentialPolicy):
            self._credential_policy = credential  # type: ignore
        elif credential is not None:
            raise TypeError(f"Unsupported credential: {credential}")

        transport = kwargs.get("transport", None)
        if not transport:
            try:
                from azure.core.pipeline.transport import AioHttpTransport
            except ImportError:
                raise ImportError(
                    "Unable to create async transport. Please check aiohttp is installed."
                )
            transport = AioHttpTransport(**kwargs)

        policies = [
            user_agent_policy,
            self._credential_policy,  # type: ignore
            HeadersPolicy(**kwargs),
            UserAgentPolicy(**kwargs),
            ContentDecodePolicy(**kwargs),
            AsyncRetryPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
        ]
        # add additional policies from kwargs
        if kwargs.get("_additional_pipeline_policies"):
            policies.extend([kwargs.get("_additional_pipeline_policies")])

        return AsyncPipeline(transport, policies=policies)  # type: ignore
