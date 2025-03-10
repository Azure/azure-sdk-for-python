# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Literal,
    Mapping,
    Tuple,
    Type,
    Union,
    Optional,
    Any,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._parameters import GLOBAL_PARAMS
from ...._bicep.expressions import Output, Parameter, ResourceSymbol
from ...._setting import StoredPrioritizedSetting
from ...._resource import (
    ExtensionResources,
    ResourceReference,
    _ClientResource,
    _build_envs,
    _load_dev_environment,
)

from .. import AIServices

if TYPE_CHECKING:
    from .types import DeploymentResource
    from azure.ai.inference import ChatCompletionsClient


class DeploymentKwargs(TypedDict, total=False):
    model: Union[str, Parameter]
    """Deployment model name."""
    format: Union[str, Parameter]
    """Deployment model format."""
    version: Union[str, Parameter]
    """Deployment model version."""
    sku: Union[str, Parameter]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    capacity: Union[int, Parameter]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible
    for the resource this may be omitted.
    """
    rai_policy: Union[str, Parameter]
    """The name of RAI policy."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""


_DEFAULT_DEPLOYMENT: "DeploymentResource" = {"name": GLOBAL_PARAMS["defaultName"]}
_DEFAULT_AI_DEPLOYMENT_EXTENSIONS: ExtensionResources = {"managed_identity_roles": [], "user_roles": []}
AIDeploymentResourceType = TypeVar("AIDeploymentResourceType", bound=Mapping[str, Any], default="DeploymentResource")


class AIDeployment(_ClientResource[AIDeploymentResourceType]):
    DEFAULTS: "DeploymentResource" = _DEFAULT_DEPLOYMENT
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_DEPLOYMENT_EXTENSIONS
    properties: AIDeploymentResourceType
    parent: AIServices

    def __init__(
        self,
        properties: Optional["DeploymentResource"] = None,
        /,
        name: Optional[str] = None,
        account: Optional[Union[str, AIServices]] = None,
        **kwargs: Unpack["DeploymentKwargs"],
    ) -> None:
        existing = kwargs.pop("existing", False)
        extensions: ExtensionResources = defaultdict(list)
        parent = account if isinstance(account, AIServices) else kwargs.pop("parent", AIServices(name=account))
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "model" in kwargs:
                properties["properties"]["model"] = properties["properties"].get("model", {})
                properties["properties"]["model"]["name"] = kwargs.pop("model")
            if "format" in kwargs:
                properties["properties"]["model"] = properties["properties"].get("model", {})
                properties["properties"]["model"]["format"] = kwargs.pop("format")
            if "version" in kwargs:
                properties["properties"]["model"] = properties["properties"].get("model", {})
                properties["properties"]["model"]["version"] = kwargs.pop("version")
            if "sku" in kwargs:
                properties["sku"] = properties.get("sku", {})
                properties["sku"]["name"] = kwargs.pop("sku")
            if "capacity" in kwargs:
                properties["sku"] = properties.get("sku", {})
                properties["sku"]["capacity"] = kwargs.pop("capacity")
            if "rai_policy" in kwargs:
                properties["properties"]["raiPolicyName"] = kwargs.pop("rai_policy")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="deployments",
            service_prefix=kwargs.pop("service_prefix", ["ai_deployment"]),
            identifier=kwargs.pop("identifier", ResourceIdentifiers.ai_deployment),
            **kwargs,
        )
        self._properties_to_merge.append("sku")
        self._settings["model_name"] = StoredPrioritizedSetting(
            name="model_name", env_vars=_build_envs(self._prefixes, ["MODEL_NAME"]), suffix=self._suffix
        )
        self._settings["model_version"] = StoredPrioritizedSetting(
            name="model_version", env_vars=_build_envs(self._prefixes, ["MODEL_VERSION"]), suffix=self._suffix
        )

    @property
    def resource(self) -> Literal["Microsoft.CognitiveServices/accounts/deployments"]:
        return "Microsoft.CognitiveServices/accounts/deployments"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter],
        account: Union[str, Parameter, AIServices],
        resource_group: Optional[Union[str, Parameter, "ResourceGroup"]] = None,
    ) -> "AIDeployment[ResourceReference]":
        if isinstance(account, (str, Parameter)):
            parent = AIServices.reference(
                name=account,
                resource_group=resource_group,
            )
        else:
            parent = account
        return super().reference(name=name, parent=parent)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return (
            f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/"  # pylint: disable=protected-access
            + f"deployments/{self._settings['name'](config_store=config_store)}"
        )

    def _outputs(
        self,
        *,
        symbol: ResourceSymbol,
        resource_group: Union[str, ResourceSymbol],
        parents: Tuple[ResourceSymbol, ...],
        **kwargs,
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, **kwargs)
        outputs["model_name"] = Output(f"AZURE_AI_DEPLOYMENT_MODEL_NAME{self._suffix}", "properties.model.name", symbol)
        outputs["model_version"] = Output(
            f"AZURE_AI_DEPLOYMENT_MODEL_VERSION{self._suffix}", "properties.model.version", symbol
        )
        outputs["endpoint"] = Output(
            f"AZURE_AI_DEPLOYMENT_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parents[0]).format("{}openai/deployments/") + outputs["name"].format(),
        )
        return outputs


_DEFAULT_AI_CHAT: "DeploymentResource" = {
    "name": GLOBAL_PARAMS["defaultName"].format("{}-chat-deployment"),
    "properties": {
        "model": {
            "name": Parameter("aiChatModel", default="gpt-4o-mini"),
            "format": Parameter("aiChatModelFormat", default="OpenAI"),
            "version": Parameter("aiChatModelVersion", default="2024-07-18"),
        }
    },
    "sku": {
        "name": Parameter("aiChatModelSku", default="Standard"),
        "capacity": Parameter("aiChatModelCapacity", default=30),
    },
}


ChatClientType = TypeVar("ChatClientType", default="ChatCompletionsClient")


class AIChat(AIDeployment[AIDeploymentResourceType]):
    DEFAULTS: "DeploymentResource" = _DEFAULT_AI_CHAT

    def __init__(
        self,
        properties: Optional["DeploymentResource"] = None,
        /,
        account: Optional[Union[str, AIServices]] = None,
        *,
        deployment_name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack["DeploymentKwargs"],
    ) -> None:
        super().__init__(
            properties,
            name=deployment_name or kwargs.get("model"),
            account=account,
            service_prefix=["ai_chat"],
            identifier=ResourceIdentifiers.ai_chat_deployment,
            **kwargs,
        )
        # TODO: What to do about API version?
        self._settings["api_version"].set_value("2024-08-01-preview")

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter],
        account: Union[str, Parameter, AIServices],
        resource_group: Optional[Union[str, "ResourceGroup"]] = None,
    ) -> "AIChat[ResourceReference]":
        existing = super().reference(name=name, account=account, resource_group=resource_group)
        return existing

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return (
            f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/"  # pylint: disable=protected-access
            + f"deployments/{self._settings['name'](config_store=config_store)}"  # /chat/completions"
        )

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = "chat_" + symbol._value  # pylint: disable=protected-access
        return symbol

    def _outputs(
        self,
        *,
        symbol: ResourceSymbol,
        resource_group: Union[str, ResourceSymbol],
        parents: Tuple[ResourceSymbol, ...],
        **kwargs,
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, parents=parents, **kwargs)
        outputs["model_name"] = Output(f"AZURE_AI_CHAT_MODEL_NAME{self._suffix}", "properties.model.name", symbol)
        outputs["model_version"] = Output(
            f"AZURE_AI_CHAT_MODEL_VERSION{self._suffix}", "properties.model.version", symbol
        )
        outputs["endpoint"] = Output(
            f"AZURE_AI_CHAT_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parents[0]).format("{}openai/deployments/")
            + outputs["name"].format(),  # + "/chat/completions"
        )
        return outputs

    def get_client(  # pylint: disable=too-many-statements
        self,
        cls: Optional[Type[ChatClientType]] = None,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        **client_options,
    ) -> ChatClientType:
        if cls is self.__class__:
            return self
        if config_store is None:
            config_store = _load_dev_environment()

        endpoint: str = self._settings["endpoint"](config_store=config_store)
        # TODO: AI endpoints!!!
        endpoint = endpoint.replace("cognitiveservices.azure.com", "openai.azure.com")
        client_kwargs = {}
        client_kwargs.update(client_options)
        try:
            client_kwargs["api_version"] = self._settings["api_version"](api_version, config_store=config_store)
        except RuntimeError:
            pass
        try:
            audience = self._settings["audience"](audience, config_store=config_store)
        except RuntimeError:
            audience = "https://cognitiveservices.azure.com"

        # This is the default ChatCompletions inference client.
        if cls is None:
            if use_async:
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient

                cls = AsyncChatCompletionsClient
            else:
                from azure.ai.inference import ChatCompletionsClient as SyncChatCompletionsClient

                cls = SyncChatCompletionsClient
                use_async = False

        # These are the synchronous OpenAI clients.
        # TODO: Find a better way to identify them than just the class name.
        if cls.__name__ in ["AzureOpenAI", "Chat", "Completions"]:
            from openai import AzureOpenAI
            from azure.identity import get_bearer_token_provider

            credential = self._build_credential(cls, use_async=False, credential=credential)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings["name"](config_store=config_store),
                http_client=client_kwargs.pop("http_client", transport),
                **client_kwargs,
            )
            if cls.__name__ == "Chat":
                client = client.chat
            elif cls.__name__ == "Completions":
                client = client.chat.completions
            client.__resource_settings__ = self
            return client

        # These are the asynchronous OpenAI clients.
        if cls.__name__ in ["AsyncAzureOpenAI", "AsyncChat", "AsyncCompletions"]:
            from openai import AsyncAzureOpenAI
            from azure.identity.aio import get_bearer_token_provider

            credential = self._build_credential(cls, use_async=True, credential=credential)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings["name"](config_store=config_store),
                http_client=client_kwargs.pop("http_client", transport),
                **client_kwargs,
            )
            if cls.__name__ == "AsyncChat":
                client = client.chat
            elif cls.__name__ == "AsyncCompletions":
                client = client.chat.completions
            client.__resource_settings__ = self
            return client

        if cls.__name__ == "ChatCompletionsClient":
            # TODO: Remove this once the inference constructor has been fixed to use 'audience'.
            client_kwargs["credential_scopes"] = [f"{audience}/.default"]
        else:
            client_kwargs["audience"] = audience
        client_kwargs["credential"] = self._build_credential(cls, use_async=use_async, credential=credential)
        if transport is not None:
            client_kwargs["transport"] = transport
        client = cls(endpoint, **client_kwargs)
        client.__resource_settings__ = self
        # TODO: Store kwargs and credential?
        return client


_DEFAULT_AI_TEXT_EMBEDDINGS: "DeploymentResource" = {
    "name": GLOBAL_PARAMS["defaultName"].format("{}-embeddings-deployment"),
    "properties": {
        "model": {
            "name": Parameter("aiEmbeddingsModel", default="text-embedding-ada-002"),
            "format": Parameter("aiEmbeddingsModelFormat", default="OpenAI"),
            "version": Parameter("aiEmbeddingsModelVersion", default="2"),
        }
    },
    "sku": {
        "name": Parameter("aiEmbeddingsModelSku", default="Standard"),
        "capacity": Parameter("aiEmbeddingsModelCapacity", default=30),
    },
}

EmbeddingsClientType = TypeVar("EmbeddingsClientType", default="EmbeddingsClient")


class AIEmbeddings(AIDeployment[AIDeploymentResourceType]):
    DEFAULTS: "DeploymentResource" = _DEFAULT_AI_TEXT_EMBEDDINGS

    def __init__(
        self,
        properties: Optional["DeploymentResource"] = None,
        /,
        account: Optional[Union[str, AIServices]] = None,
        *,
        deployment_name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack["DeploymentKwargs"],
    ) -> None:
        super().__init__(
            properties,
            name=deployment_name or kwargs.get("model"),
            account=account,
            service_prefix=["ai_embeddings"],
            identifier=ResourceIdentifiers.ai_embeddings_deployment,
            **kwargs,
        )
        self._settings["api_version"].set_value("2023-05-15")

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter],
        account: Optional[Union[str, AIServices]] = None,
        resource_group: Optional[Union[str, "ResourceGroup"]] = None,
    ) -> "AIEmbeddings[ResourceReference]":
        return super().reference(name=name, account=account, resource_group=resource_group)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return (
            f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/"  # pylint: disable=protected-access
            + f"deployments/{self._settings['name'](config_store=config_store)}"  # /embeddings"
        )

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = "embeddings_" + symbol._value  # pylint: disable=protected-access
        return symbol

    def _outputs(
        self,
        *,
        symbol: ResourceSymbol,
        resource_group: Union[str, ResourceSymbol],
        parents: Tuple[ResourceSymbol, ...],
        **kwargs,
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, parents=parents, **kwargs)
        outputs["model_name"] = Output(f"AZURE_AI_EMBEDDINGS_MODEL_NAME{self._suffix}", "properties.model.name", symbol)
        outputs["model_version"] = Output(
            f"AZURE_AI_EMBEDDINGS_MODEL_VERSION{self._suffix}", "properties.model.version", symbol
        )
        outputs["endpoint"] = Output(
            f"AZURE_AI_EMBEDDINGS_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parents[0]).format("{}openai/deployments/") + outputs["name"].format(),
            # + "/embeddings",
        )
        return outputs

    def get_client(
        self,
        cls: Optional[Type[EmbeddingsClientType]] = None,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        **client_options,
    ) -> EmbeddingsClientType:
        if cls is self.__class__:
            return self
        if config_store is None:
            config_store = _load_dev_environment()

        endpoint: str = self._settings["endpoint"](config_store=config_store)
        # TODO: AI endpoints!!!
        endpoint = endpoint.replace("cognitiveservices.azure.com", "openai.azure.com")
        client_kwargs = {}
        client_kwargs.update(client_options)
        try:
            client_kwargs["api_version"] = self._settings["api_version"](api_version, config_store=config_store)
        except RuntimeError:
            pass
        try:
            audience = self._settings["audience"](audience, config_store=config_store)
        except RuntimeError:
            audience = "https://cognitiveservices.azure.com"

        # This is the default EmbeddingsClient inference client.
        if cls is None:
            if use_async:
                from azure.ai.inference.aio import EmbeddingsClient as AsyncEmbeddingsClient

                cls = AsyncEmbeddingsClient
            else:
                from azure.ai.inference import EmbeddingsClient as SyncEmbeddingsClient

                cls = SyncEmbeddingsClient
                use_async = False

        # These are the synchronous OpenAI clients.
        # TODO: Find a better way to identify them than just the class name.
        if cls.__name__ in ["AzureOpenAI", "Embeddings"]:
            from openai import AzureOpenAI
            from azure.identity import get_bearer_token_provider

            credential = self._build_credential(cls, use_async=False, credential=credential)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings["name"](config_store=config_store),
                http_client=client_kwargs.pop("http_client", transport),
                **client_kwargs,
            )
            if cls.__name__ == "Embeddings":
                client = client.embeddings
            client.__resource_settings__ = self
            return client

        # These are the asynchronous OpenAI clients.
        if cls.__name__ in ["AsyncAzureOpenAI", "AsyncEmbeddings"]:
            from openai import AsyncAzureOpenAI
            from azure.identity.aio import get_bearer_token_provider

            credential = self._build_credential(cls, use_async=True, credential=credential)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings["name"](config_store=config_store),
                http_client=client_kwargs.pop("http_client", transport),
                **client_kwargs,
            )
            if cls.__name__ == "AsyncEmbeddings":
                client = client.embeddings
            client.__resource_settings__ = self
            return client

        if cls.__name__ == "EmbeddingsClient":
            # TODO: Remove this once the inference constructor has been fixed to use 'audience'.
            client_kwargs["credential_scopes"] = [f"{audience}/.default"]
        else:
            client_kwargs["audience"] = audience
        client_kwargs["credential"] = self._build_credential(cls, use_async=use_async, credential=credential)
        if transport is not None:
            client_kwargs["transport"] = transport
        client = cls(endpoint, **client_kwargs)
        client.__resource_settings__ = self
        # TODO: Store kwargs and credential?
        return client
