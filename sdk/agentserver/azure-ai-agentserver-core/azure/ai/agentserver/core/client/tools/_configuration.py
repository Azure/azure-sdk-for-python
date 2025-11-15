# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Mapping, List, Optional, TYPE_CHECKING

from azure.core.pipeline import policies

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

from ._utils._model_base import ToolConfigurationParser, UserInfo, ToolDefinition

class AzureAIToolClientConfiguration:
	"""Configuration for Azure AI Tool Client.
	
	Manages authentication, endpoint configuration, and policy settings for the
	Azure AI Tool Client. This class is used internally by the client and should
	not typically be instantiated directly.
	
	:param str endpoint:
		Fully qualified endpoint for the Azure AI Agents service.
	:param credential:
		Azure TokenCredential for authentication.
	:type credential: ~azure.core.credentials.TokenCredential
	:keyword str api_version:
		API version to use. Default is the latest supported version.
	:keyword List[str] credential_scopes:
		OAuth2 scopes for token requests. Default is ["https://ai.azure.com/.default"].
	:keyword str agent_name:
		Name of the agent. Default is "$default".
	:keyword List[Mapping[str, Any]] tools:
		List of tool configurations.
	:keyword Mapping[str, Any] user:
		User information for tool invocations.
	"""

	def __init__(
		self,
		endpoint: str,
		credential: "TokenCredential",
		**kwargs: Any,
	) -> None:
		"""Initialize the configuration.
		
		:param str endpoint: The service endpoint URL.
		:param credential: Credentials for authenticating requests.
		:type credential: ~azure.core.credentials.TokenCredential
		:keyword kwargs: Additional configuration options.
		"""
		api_version: str = kwargs.pop("api_version", "2025-05-15-preview")

		self.endpoint = endpoint
		self.credential = credential
		self.api_version = api_version
		self.credential_scopes = kwargs.pop("credential_scopes", ["https://ai.azure.com/.default"])
		

		# Tool configuration
		self.agent_name: str = kwargs.pop("agent_name", "$default")
		self.tools: Optional[List[ToolDefinition]] = kwargs.pop("tools", None)
		self.user: Optional[UserInfo] = kwargs.pop("user", None)	
		
		# Initialize tool configuration parser
		
		self.tool_config = ToolConfigurationParser(self.tools)
		
		self._configure(**kwargs)
		
				# Warn about unused kwargs
		if kwargs:
			import warnings
			warnings.warn(f"Unused configuration parameters: {list(kwargs.keys())}", UserWarning)

	def _configure(self, **kwargs: Any) -> None:
		self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
		self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
		self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
		self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
		self.http_logging_policy = kwargs.get("http_logging_policy") or policies.HttpLoggingPolicy(**kwargs)
		self.custom_hook_policy = kwargs.get("custom_hook_policy") or policies.CustomHookPolicy(**kwargs)
		self.redirect_policy = kwargs.get("redirect_policy") or policies.RedirectPolicy(**kwargs)
		self.retry_policy = kwargs.get("retry_policy") or policies.RetryPolicy(**kwargs)
		self.authentication_policy = kwargs.get("authentication_policy")
		if self.credential and not self.authentication_policy:
			self.authentication_policy = policies.BearerTokenCredentialPolicy(
				self.credential, *self.credential_scopes, **kwargs
			)