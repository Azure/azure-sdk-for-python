from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Self, Tuple, TypedDict, Union, Unpack, overload, Optional, Any, Type
from typing_extensions import TypeVar

from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._parameters import GLOBAL_PARAMS
from ...._bicep.expressions import Expression, Output, Parameter, ResourceSymbol
from ...._setting import StoredPrioritizedSetting
from ...._resource import (
    ExtensionResources,
    ResourceReference,
    _ClientResource,
    _build_envs,
)

from .. import AIServices

if TYPE_CHECKING:
    from .types import DeploymentResource
    from azure.ai.inference import ChatCompletionsClient


class DeploymentKwargs(TypedDict, total=False):
    model: Union[str, Parameter[str]]
    """Deployment model name."""
    format: Union[str, Parameter[str]]
    """Deployment model format."""
    version: Union[str, Parameter[str]]
    """Deployment model version."""
    sku: Union[str, Parameter[str]]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    capacity: Union[int, Parameter[int]]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    rai_policy: Union[str, Parameter[str]]
    """The name of RAI policy."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict]]
    """Tags of the resource."""


_DEFAULT_DEPLOYMENT: 'DeploymentResource' = {'name': GLOBAL_PARAMS['defaultName']}
_DEFAULT_AI_DEPLOYMENT_EXTENSIONS: ExtensionResources = {
    'managed_identity_roles': [],
    'user_roles': []
}
AIDeploymentResourceType = TypeVar('AIDeploymentResourceType', default='DeploymentResource')


class AIDeployment(_ClientResource[AIDeploymentResourceType]):
    DEFAULTS: 'DeploymentResource' = _DEFAULT_DEPLOYMENT
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_DEPLOYMENT_EXTENSIONS
    resource: Literal["Microsoft.CognitiveServices/accounts/deployments"]
    properties: AIDeploymentResourceType
    parent: AIServices

    def __init__(
            self,
            properties: Optional['DeploymentResource'] = None,
            /,
            name: Optional[str] = None,
            account: Optional[Union[str, AIServices]] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = defaultdict(list)
        parent = account if isinstance(account, AIServices) else kwargs.pop('parent', AIServices(name=account))
        if not existing:
            properties = properties or {}
            if 'properties' not in properties:
                properties['properties'] = {}
            if name:
                properties['name'] = name
            if 'model' in kwargs:
                properties['properties']['model'] = properties['properties'].get('model', {})
                properties['properties']['model']['name'] = kwargs.pop('model')
            if 'format' in kwargs:
                properties['properties']['model'] = properties['properties'].get('model', {})
                properties['properties']['model']['format'] = kwargs.pop('format')
            if 'version' in kwargs:
                properties['properties']['model'] = properties['properties'].get('model', {})
                properties['properties']['model']['version'] = kwargs.pop('version')
            if 'sku' in kwargs:
                properties['sku'] = properties.get('sku', {})
                properties['sku']['name'] = kwargs.pop('sku')
            if 'capacity' in kwargs:
                properties['sku'] = properties.get('sku', {})
                properties['sku']['capacity'] = kwargs.pop('capacity')
            if 'rai_policy' in kwargs:
                properties['properties']['raiPolicyName'] = kwargs.pop('rai_policy')
            if 'tags' in kwargs:
                properties['tags'] = kwargs.pop('tags')
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="deployments",
            service_prefix=kwargs.pop('service_prefix', ["ai_deployment"]),
            identifier=kwargs.pop('identifier', ResourceIdentifiers.ai_deployment),
            **kwargs
        )
        self._properties_to_merge.append('sku')
        self._settings['model_name'] = StoredPrioritizedSetting(
            name='model_name',
            env_vars=_build_envs(self._prefixes, ['MODEL_NAME']),
            suffix=self._suffix
        )
        self._settings['model_version'] = StoredPrioritizedSetting(
            name='model_version',
            env_vars=_build_envs(self._prefixes, ['MODEL_VERSION']),
            suffix=self._suffix
        )


    @property
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from .types import RESOURCE
        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION
        self._version = VERSION
        return self._version

    @classmethod
    def reference(
            cls,
            *,
            name: Union[str, Parameter[str]],
            account: Union[str, Parameter[str], AIServices],
            resource_group: Optional[Union[str, Parameter[str], 'ResourceGroup']] = None,
    ) -> 'AIDeployment[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        if isinstance(account, (str, Parameter)):
            parent = AIServices.reference(
                name=account,
                resource_group=resource_group,
            )
        else:
            parent = account
        return super().reference(
            resource=resource,
            name=name,
            parent=parent
        )

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/deployments/{self._settings['name'](config_store=config_store)}"

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            resource_group: Union[str, ResourceSymbol],
            parents: Tuple[ResourceSymbol, ...],
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, **kwargs)
        outputs['model_name'] = Output(f"AZURE_AI_DEPLOYMENT_MODEL_NAME{self._suffix}", 'properties.model.name', symbol)
        outputs['model_version'] = Output(f"AZURE_AI_DEPLOYMENT_MODEL_VERSION{self._suffix}", 'properties.model.version', symbol)
        outputs['endpoint'] = Output(
            f"AZURE_AI_DEPLOYMENT_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parents[0]).format("{}openai/deployments/") + outputs['name'].format()
        )
        return outputs


_DEFAULT_AI_CHAT: 'DeploymentResource' = {
    'name': GLOBAL_PARAMS['defaultName'].format('{}-chat-deployment'),
    'properties': {
        'model': {
            'name': Parameter("aiChatModel", type=str, default='gpt-4o-mini'),
            'format': Parameter("aiChatModelFormat", type=str, default='OpenAI'),
            'version': Parameter("aiChatModelVersion", type=str, default='2024-07-18')
        }
    },
    'sku': {
        'name': Parameter("aiChatModelSku", type=str, default='Standard'),
        'capacity': Parameter("aiChatModelCapacity", type=int, default=30)
    }
}


ChatClientType = TypeVar("ChatClientType", default='ChatCompletionsClient')
class AIChat(AIDeployment[AIDeploymentResourceType]):
    DEFAULTS: 'DeploymentResource' = _DEFAULT_AI_CHAT

    def __init__(
            self,
            properties: Optional['DeploymentResource'] = None,
            /,
            account: Optional[Union[str, AIServices]] = None,
            *,
            deployment_name: Optional[Union[str, Parameter[str]]] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        super().__init__(
            properties,
            name=deployment_name or kwargs.get('model'),
            account=account,
            service_prefix=['ai_chat'],
            identifier=ResourceIdentifiers.ai_chat_deployment,
            **kwargs
        )
        # TODO: What to do about API version?
        self._settings['api_version'].set_value("2024-08-01-preview")

    @classmethod
    def reference(
            cls,
            *,
            name: Union[str, Parameter[str]],
            account: Union[str, Parameter[str], AIServices],
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
    ) -> 'AIChat[ResourceReference]':
        existing = super().reference(
            name=name,
            account=account,
            resource_group=resource_group
        )
        return existing

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/deployments/{self._settings['name'](config_store=config_store)}/chat/completions"

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = f"chat_" + symbol._value
        return symbol

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            resource_group: Union[str, ResourceSymbol],
            parents: Tuple[ResourceSymbol, ...],
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, parents=parents, **kwargs)
        outputs['model_name'] = Output(f"AZURE_AI_CHAT_MODEL_NAME{self._suffix}", 'properties.model.name', symbol)
        outputs['model_version'] = Output(f"AZURE_AI_CHAT_MODEL_VERSION{self._suffix}", 'properties.model.version', symbol)
        outputs['endpoint'] = Output(
            f"AZURE_AI_CHAT_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parents[0]).format("{}openai/deployments/") + outputs['name'].format() # + "/chat/completions"
        )
        return outputs

    # TODO: Add use_async and config_store
    def get_client(
            self,
            cls: Optional[Callable[..., ChatClientType]] = None,
            /,
            *,
            transport: Any = None,
            api_version: Optional[str] = None,
            audience: Optional[str] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
            **client_options,
    ) -> ChatClientType:
        if cls is None:
            from azure.ai.inference import ChatCompletionsClient
            cls = ChatCompletionsClient
        api_version = api_version or self._settings['api_version'](config_store=config_store)
        try:
            audience = audience or self._settings['audience'](config_store=config_store)
        except RuntimeError:
            audience = ["https://cognitiveservices.azure.com/.default"]# "https://cognitiveservices.azure.com"
        if cls.__name__ in ['AzureOpenAI', 'Chat', 'Completions']:
            from openai import AzureOpenAI
            from azure.identity import get_bearer_token_provider
            credential = self._build_credential(False, config_store=config_store)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            kwargs = {}
            kwargs.update(self._settings['client_options'](config_store=config_store))
            kwargs.update(client_options)
            client = AzureOpenAI(
                api_version=api_version,
                azure_endpoint=self._settings['endpoint'](config_store=config_store),
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings['name'](config_store=config_store),
                http_client=kwargs.pop('http_client', transport),
                **kwargs

            )
            if cls.__name__ == 'Chat':
                client = client.chat
            elif cls.__name__ == 'Completions':
                client = client.chat.completions
            client.__resource_settings__ = self
            return client
        if cls.__name__ in ['AsyncAzureOpenAI', 'AsyncChat', 'AsyncCompletions']:
            from openai import AsyncAzureOpenAI
            from azure.identity.aio import get_bearer_token_provider
            credential = self._build_credential(True, config_store=config_store)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            kwargs = {}
            kwargs.update(self._settings['client_options'](config_store=config_store))
            kwargs.update(client_options)
            client = AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=self._settings['endpoint'](config_store=config_store),
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings['name'](config_store=config_store),
                http_client=kwargs.pop('http_client', transport),
                **kwargs

            )
            if cls.__name__ == 'AsyncChat':
                client = client.chat
            elif cls.__name__ == 'AsyncCompletions':
                client = client.chat.completions
            client.__resource_settings__ = self
            return client

        return super().get_client(
            cls,
            transport=transport,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            env_name=env_name,
            **client_options
        )


_DEFAULT_AI_TEXT_EMBEDDINGS: 'DeploymentResource' = {
    'name': GLOBAL_PARAMS['defaultName'].format('{}-embeddings-deployment'),
    'properties': {
        'model': {
            'name': Parameter("aiEmbeddingsModel", type=str, default='text-embedding-ada-002'),
            'format': Parameter("aiEmbeddingsModelFormat", type=str, default='OpenAI'),
            'version': Parameter("aiEmbeddingsModelVersion", type=str, default='2')
        }
    },
    'sku': {
        'name': Parameter("aiEmbeddingsModelSku", type=str, default='Standard'),
        'capacity': Parameter("aiEmbeddingsModelCapacity", type=int, default=30)
    }
}

EmbeddingsClientType = TypeVar("EmbeddingsClientType", default='EmbeddingsClient')
class AIEmbeddings(AIDeployment[AIDeploymentResourceType]):
    DEFAULTS: 'DeploymentResource' = _DEFAULT_AI_TEXT_EMBEDDINGS

    def __init__(
            self,
            properties: Optional['DeploymentResource'] = None,
            /,
            account: Optional[Union[str, AIServices]] = None,
            *,
            deployment_name: Optional[Union[str, Parameter[str]]] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        super().__init__(
            properties,
            name=deployment_name or kwargs.get('model'),
            account=account,
            service_prefix=['ai_embeddings'],
            identifier=ResourceIdentifiers.ai_embeddings_deployment,
            **kwargs
        )
        self._settings['api_version'].set_value("2023-05-15")
        

    @classmethod
    def reference(
            cls,
            *,
            name: Union[str, Parameter[str]],
            account: Optional[Union[str, AIServices]] = None,
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
    ) -> 'AIEmbeddings[ResourceReference]':
        return super().reference(
            name=name,
            account=account,
            resource_group=resource_group
        )

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.openai.azure.com/openai/deployments/{self._settings['name'](config_store=config_store)}/embeddings"

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = f"embeddings_" + symbol._value
        return symbol

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            resource_group: Union[str, ResourceSymbol],
            parents: Tuple[ResourceSymbol, ...],
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, parents=parents, **kwargs)
        outputs['model_name'] = Output(f"AZURE_AI_EMBEDDINGS_MODEL_NAME{self._suffix}", 'properties.model.name', symbol)
        outputs['model_version'] = Output(f"AZURE_AI_EMBEDDINGS_MODEL_VERSION{self._suffix}", 'properties.model.version', symbol)
        outputs['endpoint'] = Output(
            f"AZURE_AI_EMBEDDINGS_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parents[0]).format("{}openai/deployments/") + outputs['name'].format() + "/embeddings"
        )
        return outputs

    # TODO: Add use_async and config_store
    def get_client(
            self,
            cls: Optional[Callable[..., EmbeddingsClientType]] = None,
            /,
            *,
            transport: Any = None,
            api_version: Optional[str] = None,
            audience: Optional[str] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
            **client_options,
    ) -> EmbeddingsClientType:
        if cls is None:
            from azure.ai.inference import EmbeddingsClient
            cls = EmbeddingsClient
        api_version = api_version or self._settings['api_version'](config_store=config_store)
        try:
            audience = audience or self._settings['audience'](config_store=config_store)
        except RuntimeError:
            audience = "https://cognitiveservices.azure.com"
        if cls.__name__ in ['AzureOpenAI', 'Embeddings']:
            from openai import AzureOpenAI
            from azure.identity import get_bearer_token_provider
            credential = self._build_credential(False, config_store=config_store)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            kwargs = {}
            kwargs.update(self._settings['client_options'](config_store=config_store))
            kwargs.update(client_options)
            client = AzureOpenAI(
                api_version=api_version,
                azure_endpoint=self._settings['endpoint'](config_store=config_store),
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings['name'](config_store=config_store),
                http_client=kwargs.pop('http_client', transport),
                **kwargs

            )
            if cls.__name__ == 'Embeddings':
                client = client.embeddings
            client.__resource_settings__ = self
            return client
        if cls.__name__ in ['AsyncAzureOpenAI', 'AsyncEmbeddings']:
            from openai import AsyncAzureOpenAI
            from azure.identity.aio import get_bearer_token_provider
            credential = self._build_credential(True, config_store=config_store)
            token_provider = get_bearer_token_provider(credential, f"{audience}/.default")
            kwargs = {}
            kwargs.update(self._settings['client_options'](config_store=config_store))
            kwargs.update(client_options)
            client = AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=self._settings['endpoint'](config_store=config_store),
                azure_ad_token_provider=token_provider,
                azure_deployment=self._settings['name'](config_store=config_store),
                http_client=kwargs.pop('http_client', transport),
                **kwargs

            )
            if cls.__name__ == 'AsyncEmbeddings':
                client = client.embeddings
            client.__resource_settings__ = self
            return client

        return super().get_client(
            cls,
            transport=transport,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            env_name=env_name,
            **client_options
        )