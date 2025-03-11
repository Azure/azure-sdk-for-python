# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ, too-many-statements, too-many-return-statements, too-many-branches

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
    Mapping,
    Tuple,
    Type,
    Union,
    Optional,
    Any,
    cast,
    overload,
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
    SyncClient,
    AsyncClient,
)

from .. import AIServices

if TYPE_CHECKING:
    from .types import DeploymentResource

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.ai.inference import ChatCompletionsClient, EmbeddingsClient
    from azure.ai.inference.aio import (
        ChatCompletionsClient as AsyncChatCompletionsClient,
        EmbeddingsClient as AsyncEmbeddingsClient,
    )


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
    DEFAULTS: "DeploymentResource" = _DEFAULT_DEPLOYMENT  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_DEPLOYMENT_EXTENSIONS
    properties: AIDeploymentResourceType
    parent: AIServices  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["DeploymentResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        account: Optional[Union[str, Parameter, AIServices]] = None,
        **kwargs: Unpack["DeploymentKwargs"],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if isinstance(account, AIServices):
            parent = account
        else:
            # 'parent' is passed by the reference classmethod.
            parent = kwargs.pop("parent", AIServices(name=account))  # type: ignore[typeddict-item]
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "model" in kwargs:
                properties["properties"]["model"] = properties["properties"].get("model", {})
                if isinstance(properties["properties"]["model"], Parameter):
                    param_name = properties["properties"]["model"].name
                    raise ValueError(f"Cannot add keyword 'model' to Parameter '{param_name}'.")
                properties["properties"]["model"]["name"] = kwargs.pop("model")
            if "format" in kwargs:
                properties["properties"]["model"] = properties["properties"].get("model", {})
                if isinstance(properties["properties"]["model"], Parameter):
                    param_name = properties["properties"]["model"].name
                    raise ValueError(f"Cannot add keyword 'format' to Parameter '{param_name}'.")
                properties["properties"]["model"]["format"] = kwargs.pop("format")
            if "version" in kwargs:
                properties["properties"]["model"] = properties["properties"].get("model", {})
                if isinstance(properties["properties"]["model"], Parameter):
                    param_name = properties["properties"]["model"].name
                    raise ValueError(f"Cannot add keyword 'model' to Parameter '{param_name}'.")
                properties["properties"]["model"]["version"] = kwargs.pop("version")
            if "sku" in kwargs:
                properties["sku"] = properties.get("sku", {})
                if isinstance(properties["sku"], Parameter):
                    param_name = properties["sku"].name
                    raise ValueError(f"Cannot add keyword 'sku' to Parameter '{param_name}'.")
                properties["sku"]["name"] = kwargs.pop("sku")
            if "capacity" in kwargs:
                properties["sku"] = properties.get("sku", {})
                if isinstance(properties["sku"], Parameter):
                    param_name = properties["sku"].name
                    raise ValueError(f"Cannot add keyword 'capacity' to Parameter '{param_name}'.")
                properties["sku"]["capacity"] = kwargs.pop("capacity")
            if "rai_policy" in kwargs:
                properties["properties"]["raiPolicyName"] = kwargs.pop("rai_policy")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        # The kwargs service_prefix and identifier can be passed by child classes.
        super().__init__(
            cast(Dict[str, Any], properties),
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="deployments",
            service_prefix=kwargs.pop("service_prefix", ["ai_deployment"]),  # type: ignore[typeddict-item]
            identifier=kwargs.pop("identifier", ResourceIdentifiers.ai_deployment),  # type: ignore[typeddict-item]
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
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        account: Union[str, Parameter, AIServices[ResourceReference]],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AIDeployment[ResourceReference]":
        if isinstance(account, (str, Parameter)):
            parent = AIServices.reference(
                name=account,
                resource_group=resource_group,
            )
        else:
            parent = account
        existing = super().reference(name=name, parent=parent)
        return cast(AIDeployment[ResourceReference], existing)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return (
            f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/"  # pylint: disable=protected-access
            + f"deployments/{self._settings['name'](config_store=config_store)}"
        )

    def _outputs(  # type: ignore[override]  # Parameter subset
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


ChatClientType = TypeVar("ChatClientType", bound=Union[SyncClient, AsyncClient], default="ChatCompletionsClient")


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
            service_prefix=["ai_chat"],  # type: ignore[call-arg]
            identifier=ResourceIdentifiers.ai_chat_deployment,  # type: ignore[call-arg]
            **kwargs,
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        account: Union[str, Parameter, AIServices[ResourceReference]],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AIChat[ResourceReference]":
        existing = super().reference(name=name, account=account, resource_group=resource_group)
        return cast(AIChat[ResourceReference], existing)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return (
            f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/"  # pylint: disable=protected-access
            + f"deployments/{self._settings['name'](config_store=config_store)}"  # /chat/completions"
        )

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = "chat_" + symbol.value  # pylint: disable=protected-access
        return symbol

    def _outputs(  # type: ignore[override]  # Parameter subset
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

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "ChatCompletionsClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncChatCompletionsClient": ...
    @overload
    def get_client(
        self,
        cls: Type[ChatClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[False] = False,
        **client_options,
    ) -> ChatClientType: ...
    @overload
    def get_client(
        self,
        cls: Type[ChatClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[True],
        **client_options,
    ) -> Tuple[ChatClientType, Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]]: ...
    def get_client(
        self,
        cls=None,
        /,
        *,
        transport=None,
        credential=None,
        api_version=None,
        audience=None,
        config_store=None,
        use_async=None,
        return_credential=False,
        **client_options,
    ):
        if config_store is None:
            config_store = _load_dev_environment()

        endpoint = self._settings["endpoint"](config_store=config_store)
        # TODO: AI endpoints!!!
        endpoint = endpoint.replace("cognitiveservices.azure.com", "openai.azure.com")
        client_kwargs = {}
        client_kwargs.update(client_options)
        try:
            client_kwargs["api_version"] = self._settings["api_version"](api_version, config_store=config_store)
        except RuntimeError:
            # TODO: What to do about API version?
            client_kwargs["api_version"] = "2024-08-01-preview"
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
            # TODO: Better check than just class name?
            if cls.__name__ == "Chat":
                if return_credential:
                    return client.chat, credential
                return client.chat
            if cls.__name__ == "Completions":
                if return_credential:
                    return client.chat.completions, credential
                return client.chat.completions
            if return_credential:
                return client, credential
            return client

        # These are the asynchronous OpenAI clients.
        if cls.__name__ in ["AsyncAzureOpenAI", "AsyncChat", "AsyncCompletions"]:
            from openai import AsyncAzureOpenAI
            from azure.identity.aio import get_bearer_token_provider as async_get_bearer_token_provider

            credential = self._build_credential(cls, use_async=True, credential=credential)
            async_token_provider = async_get_bearer_token_provider(credential, f"{audience}/.default")
            async_client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=async_token_provider,
                azure_deployment=self._settings["name"](config_store=config_store),
                http_client=client_kwargs.pop("http_client", transport),
                **client_kwargs,
            )
            if cls.__name__ == "AsyncChat":
                if return_credential:
                    return async_client.chat, credential
                return async_client.chat
            if cls.__name__ == "AsyncCompletions":
                if return_credential:
                    return async_client.chat.completions, credential
                return async_client.chat.completions
            if return_credential:
                return async_client, credential
            return async_client

        if cls.__name__ == "ChatCompletionsClient":
            # TODO: Remove this once the inference constructor has been fixed to use 'audience'.
            client_kwargs["credential_scopes"] = [f"{audience}/.default"]
        else:
            client_kwargs["audience"] = audience
        credential = self._build_credential(cls, use_async=use_async, credential=credential)
        if transport is not None:
            client_kwargs["transport"] = transport
        client = cls(endpoint, credential=credential, **client_kwargs)
        if return_credential:
            return client, credential
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

EmbeddingsClientType = TypeVar("EmbeddingsClientType", bound=Union[SyncClient, AsyncClient], default="EmbeddingsClient")


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
            service_prefix=["ai_embeddings"],  # type: ignore[call-arg]
            identifier=ResourceIdentifiers.ai_embeddings_deployment,  # type: ignore[call-arg]
            **kwargs,
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        account: Union[str, Parameter, AIServices[ResourceReference]],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AIEmbeddings[ResourceReference]":
        existing = super().reference(name=name, account=account, resource_group=resource_group)
        return cast(AIEmbeddings[ResourceReference], existing)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return (
            f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/"  # pylint: disable=protected-access
            + f"deployments/{self._settings['name'](config_store=config_store)}"  # /embeddings"
        )

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = "embeddings_" + symbol.value  # pylint: disable=protected-access
        return symbol

    def _outputs(  # type: ignore[override]  # Parameter subset
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

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "EmbeddingsClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncEmbeddingsClient": ...
    @overload
    def get_client(
        self,
        cls: Type[EmbeddingsClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[False] = False,
        **client_options,
    ) -> EmbeddingsClientType: ...
    @overload
    def get_client(
        self,
        cls: Type[EmbeddingsClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[True],
        **client_options,
    ) -> Tuple[EmbeddingsClientType, Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]]: ...
    def get_client(
        self,
        cls=None,
        /,
        *,
        transport=None,
        credential=None,
        api_version=None,
        audience=None,
        config_store=None,
        use_async=None,
        return_credential=False,
        **client_options,
    ):
        if config_store is None:
            config_store = _load_dev_environment()

        endpoint = self._settings["endpoint"](config_store=config_store)
        # TODO: AI endpoints!!!
        endpoint = endpoint.replace("cognitiveservices.azure.com", "openai.azure.com")
        client_kwargs = {}
        client_kwargs.update(client_options)
        try:
            client_kwargs["api_version"] = self._settings["api_version"](api_version, config_store=config_store)
        except RuntimeError:
            client_kwargs["api_version"] = "2023-05-15"
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
                if return_credential:
                    return client.embeddings, credential
                return client.embeddings
            if return_credential:
                return client, credential
            return client

        # These are the asynchronous OpenAI clients.
        if cls.__name__ in ["AsyncAzureOpenAI", "AsyncEmbeddings"]:
            from openai import AsyncAzureOpenAI
            from azure.identity.aio import get_bearer_token_provider as async_get_bearer_token_provider

            credential = self._build_credential(cls, use_async=True, credential=credential)
            token_provider = async_get_bearer_token_provider(credential, f"{audience}/.default")
            client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings["name"](config_store=config_store),
                http_client=client_kwargs.pop("http_client", transport),
                **client_kwargs,
            )
            if cls.__name__ == "AsyncEmbeddings":
                if return_credential:
                    return client.embeddings, credential
                return client.embeddings
            if return_credential:
                return client, credential
            return client

        if cls.__name__ == "EmbeddingsClient":
            # TODO: Remove this once the inference constructor has been fixed to use 'audience'.
            client_kwargs["credential_scopes"] = [f"{audience}/.default"]
        else:
            client_kwargs["audience"] = audience
        credential = self._build_credential(cls, use_async=use_async, credential=credential)
        if transport is not None:
            client_kwargs["transport"] = transport
        client = cls(endpoint, credential=credential, **client_kwargs)
        if return_credential:
            return client, credential
        return client
