# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Union, List, Type

from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    AccessKeyAuthTypeWorkspaceConnectionProperties,
    ApiKeyAuthWorkspaceConnectionProperties,
    ConnectionAuthType,
    ManagedIdentityAuthTypeWorkspaceConnectionProperties,
    NoneAuthTypeWorkspaceConnectionProperties,
    PATAuthTypeWorkspaceConnectionProperties,
    SASAuthTypeWorkspaceConnectionProperties,
    ServicePrincipalAuthTypeWorkspaceConnectionProperties,
    UsernamePasswordAuthTypeWorkspaceConnectionProperties,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    WorkspaceConnectionPropertiesV2BasicResource as RestWorkspaceConnection,
    ConnectionCategory,
)
from azure.ai.ml._schema.workspace.connections.workspace_connection import WorkspaceConnectionSchema
from azure.ai.ml._schema.workspace.connections.workspace_connection_subtypes import (
    OpenAIWorkspaceConnectionSchema,
    AzureAISearchWorkspaceConnectionSchema,
    AzureAIServiceWorkspaceConnectionSchema,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import _snake_to_camel, camel_to_snake, dump_yaml_to_file
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_API_VERSION_KEY,
    CONNECTION_KIND_KEY,
)
from azure.ai.ml.entities._credentials import (
    AccessKeyConfiguration,
    ApiKeyConfiguration,
    ManagedIdentityConfiguration,
    PatTokenConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    UsernamePasswordConfiguration,
)
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict


# Dev note: The acceptables strings for the type field are all snake_cased versions of the string constants defined
# In the rest client ConnectionCategory. We avoid directly referencing it in the docs to avoid restclient references.
@experimental
class WorkspaceConnection(Resource):
    """Azure ML workspace connection provides a secure way to store authentication and configuration information needed
    to connect and interact with the external resources.

    Note: For connections to OpenAI, Cognitive Search, and Cognitive Services, use the respective subclasses
    (ex: ~azure.ai.ml.entities.OpenAIWorkspaceConnection) instead of instantiating this class directly.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param type: The category of external resource for this connection.
    :type type: The type of workspace connection, possible values are: "git", "python_feed", "container_registry",
        "feature_store", "s3", "snowflake", "azure_sql_db", "azure_synapse_analytics", "azure_my_sql_db",
        "azure_postgres_db"
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: Union[
        ~azure.ai.ml.entities.PatTokenConfiguration, ~azure.ai.ml.entities.SasTokenConfiguration,
        ~azure.ai.ml.entities.UsernamePasswordConfiguration, ~azure.ai.ml.entities.ManagedIdentityConfiguration
        ~azure.ai.ml.entities.ServicePrincipalConfiguration, ~azure.ai.ml.entities.AccessKeyConfiguration,
        ~azure.ai.ml.entities.ApiKeyConfiguration
        ]
    """

    def __init__(
        self,
        *,
        target: str,
        # TODO : Check if this is okay since it shadows builtin-type type
        type: str,  # pylint: disable=redefined-builtin
        credentials: Union[
            PatTokenConfiguration,
            SasTokenConfiguration,
            UsernamePasswordConfiguration,
            ManagedIdentityConfiguration,
            ServicePrincipalConfiguration,
            AccessKeyConfiguration,
            ApiKeyConfiguration,
        ],
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.type = type
        self._target = target
        self._credentials = credentials

    @property
    def type(self) -> str:
        """Type of the workspace connection, supported are 'git', 'python_feed' and 'container_registry'.

        :return: Type of the job.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, value: str):
        """Set the type of the workspace connection, supported are 'git', 'python_feed' and 'container_registry'.

        :param value: value for the type of workspace connection.
        :type: str
        """
        if not value:
            return
        self._type = camel_to_snake(value)

    @property
    def target(self) -> str:
        """Target url for the workspace connection.

        :return: Target of the workspace connection.
        :rtype: str
        """
        return self._target

    @property
    def credentials(
        self,
    ) -> Union[
        PatTokenConfiguration,
        SasTokenConfiguration,
        UsernamePasswordConfiguration,
        ManagedIdentityConfiguration,
        ServicePrincipalConfiguration,
        AccessKeyConfiguration,
        ApiKeyConfiguration,
    ]:
        """Credentials for workspace connection.

        :return: Credentials for workspace connection.
        :rtype: Union[
            ~azure.ai.ml.entities.PatTokenConfiguration, ~azure.ai.ml.entities.SasTokenConfiguration,
            ~azure.ai.ml.entities.UsernamePasswordConfiguration, ~azure.ai.ml.entities.ManagedIdentityConfiguration
            ~azure.ai.ml.entities.ServicePrincipalConfiguration, ~azure.ai.ml.entities.AccessKeyConfiguration,
            ~azure.ai.ml.entities.ApiKeyConfiguration
        ]
        """
        return self._credentials

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the workspace connection spec into a file in yaml format.

        :param dest: The destination to receive this workspace connection's spec.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "WorkspaceConnection":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cls._load_from_dict(data=data, context=context, **kwargs)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "WorkspaceConnection":
        conn_type = data["type"] if "type" in data else None
        schema_class = cls._get_schema_class_from_type(conn_type)
        loaded_data = load_from_dict(schema_class, data, context, **kwargs)
        return loaded_data

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        schema_class = WorkspaceConnection._get_schema_class_from_type(self.type)
        # Not sure what this pylint complaint was about, probably due to the polymorphic
        # tricks at play. Disabling since testing indicates no issue.
        # pylint: disable-next=missing-kwoa
        return schema_class(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspaceConnection) -> "WorkspaceConnection":
        from .workspace_connection_subtypes import (
            AzureOpenAIWorkspaceConnection,
            AzureAISearchWorkspaceConnection,
            AzureAIServiceWorkspaceConnection,
        )

        if not rest_obj:
            return None

        conn_cat = rest_obj.properties.category
        conn_class = cls._get_entity_class_from_type(conn_cat)

        popped_tags = []
        if conn_class == AzureOpenAIWorkspaceConnection:
            popped_tags = [CONNECTION_API_VERSION_KEY, CONNECTION_API_TYPE_KEY]
        elif conn_class == AzureAISearchWorkspaceConnection:
            popped_tags = [CONNECTION_API_VERSION_KEY]
        elif conn_class == AzureAIServiceWorkspaceConnection:
            popped_tags = [CONNECTION_API_VERSION_KEY, CONNECTION_KIND_KEY]

        rest_kwargs = cls._extract_kwargs_from_rest_obj(rest_obj=rest_obj, popped_tags=popped_tags)
        workspace_connection = conn_class(**rest_kwargs)
        return workspace_connection

    def _validate(self):
        return self.name

    def _to_rest_object(self) -> RestWorkspaceConnection:
        workspace_connection_properties_class = None
        auth_type = self.credentials.type if self._credentials else None

        if auth_type == camel_to_snake(ConnectionAuthType.PAT):
            workspace_connection_properties_class = PATAuthTypeWorkspaceConnectionProperties
        elif auth_type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY):
            workspace_connection_properties_class = ManagedIdentityAuthTypeWorkspaceConnectionProperties
        elif auth_type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD):
            workspace_connection_properties_class = UsernamePasswordAuthTypeWorkspaceConnectionProperties
        elif auth_type == camel_to_snake(ConnectionAuthType.ACCESS_KEY):
            workspace_connection_properties_class = AccessKeyAuthTypeWorkspaceConnectionProperties
        elif auth_type == camel_to_snake(ConnectionAuthType.SAS):
            workspace_connection_properties_class = SASAuthTypeWorkspaceConnectionProperties
        elif auth_type == camel_to_snake(ConnectionAuthType.SERVICE_PRINCIPAL):
            workspace_connection_properties_class = ServicePrincipalAuthTypeWorkspaceConnectionProperties
        elif auth_type == camel_to_snake(ConnectionAuthType.API_KEY):
            workspace_connection_properties_class = ApiKeyAuthWorkspaceConnectionProperties
        elif auth_type is None:
            workspace_connection_properties_class = NoneAuthTypeWorkspaceConnectionProperties

        properties = workspace_connection_properties_class(
            target=self.target,
            credentials=self.credentials._to_workspace_connection_rest_object(),
            metadata=self.tags,
            category=_snake_to_camel(self.type),
        )

        return RestWorkspaceConnection(properties=properties)

    @classmethod
    def _extract_kwargs_from_rest_obj(cls, rest_obj: RestWorkspaceConnection, popped_tags: List[str]) -> Dict[str, str]:
        """Internal helper function with extracts all the fields needed to initialize a workspace connection object
        from its associated restful object. Pulls extra fields based on the supplied popped_tags. Returns all the
        fields as a dictionary, which is expected to then be supplied to a workspace connection initializer as kwargs.

        :param rest_obj: The rest object representation of a workspace connection
        :type rest_obj: RestWorkspaceConnection
        :param popped_tags: Tags that should be pulled from the rest object's metadata and injected as top-level
            fields into the connection's initializer. Needed for subclasses that require extra inputs compared
            to the base WorkspaceConnection class.
        :type popped_tags: List[str]

        :return: A dictionary containing all kwargs needed to construct a workspace connection.
        :rtype: Dict[str, str]
        """
        properties = rest_obj.properties
        if properties.auth_type == ConnectionAuthType.PAT:
            credentials = PatTokenConfiguration._from_workspace_connection_rest_object(properties.credentials)
        if properties.auth_type == ConnectionAuthType.SAS:
            credentials = SasTokenConfiguration._from_workspace_connection_rest_object(properties.credentials)
        if properties.auth_type == ConnectionAuthType.MANAGED_IDENTITY:
            credentials = ManagedIdentityConfiguration._from_workspace_connection_rest_object(properties.credentials)
        if properties.auth_type == ConnectionAuthType.USERNAME_PASSWORD:
            credentials = UsernamePasswordConfiguration._from_workspace_connection_rest_object(properties.credentials)
        if properties.auth_type == ConnectionAuthType.ACCESS_KEY:
            credentials = AccessKeyConfiguration._from_workspace_connection_rest_object(properties.credentials)
        if properties.auth_type == ConnectionAuthType.SERVICE_PRINCIPAL:
            credentials = ServicePrincipalConfiguration._from_workspace_connection_rest_object(properties.credentials)
        if properties.auth_type == ConnectionAuthType.API_KEY:
            credentials = ApiKeyConfiguration._from_workspace_connection_rest_object(properties.credentials)

        tags = properties.metadata if hasattr(properties, "metadata") else None
        rest_kwargs = {
            "id": rest_obj.id,
            "name": rest_obj.name,
            "target": properties.target,
            "creation_context": SystemData._from_rest_object(rest_obj.system_data) if rest_obj.system_data else None,
            "type": camel_to_snake(properties.category),
            "credentials": credentials,
            "tags": tags,
        }

        for name in popped_tags:
            if name in tags:
                rest_kwargs[camel_to_snake(name)] = tags[name]
        return rest_kwargs

    @classmethod
    def _get_entity_class_from_type(cls, conn_type: str) -> Type:
        """Helper function that converts a rest client connection category into the associated
        workspace connection class or subclass. Accounts for potential snake/camel case and
        capitalization differences.

        :param conn_type: The connection type.
        :type conn_type: str

        :return: The workspace connection class the conn_type corresponds to.
        :rtype: Type
        """
        if conn_type is None:
            return WorkspaceConnection
        # done here to avoid circular imports on load
        from .workspace_connection_subtypes import (
            AzureOpenAIWorkspaceConnection,
            AzureAISearchWorkspaceConnection,
            AzureAIServiceWorkspaceConnection,
        )

        cat = camel_to_snake(conn_type).lower()
        conn_class = WorkspaceConnection
        if cat == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI).lower():
            conn_class = AzureOpenAIWorkspaceConnection
        elif cat == camel_to_snake(ConnectionCategory.COGNITIVE_SEARCH).lower():
            conn_class = AzureAISearchWorkspaceConnection
        elif cat == camel_to_snake(ConnectionCategory.COGNITIVE_SERVICE).lower():
            conn_class = AzureAIServiceWorkspaceConnection
        return conn_class

    @classmethod
    def _get_schema_class_from_type(cls, conn_type: str) -> Type:
        """Helper function that converts a rest client connection category into the associated
        workspace connection schema class or subclass. Accounts for potential snake/camel case and
        capitalization differences.

        :param conn_type: The connection type.
        :type conn_type: str

        :return: The workspace connection schema class the conn_type corresponds to.
        :rtype: Type
        """
        if conn_type is None:
            return WorkspaceConnection

        cat = camel_to_snake(conn_type).lower()
        conn_class = WorkspaceConnectionSchema
        if cat == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI).lower():
            conn_class = OpenAIWorkspaceConnectionSchema
        elif cat == camel_to_snake(ConnectionCategory.COGNITIVE_SEARCH).lower():
            conn_class = AzureAISearchWorkspaceConnectionSchema
        elif cat == camel_to_snake(ConnectionCategory.COGNITIVE_SERVICE).lower():
            conn_class = AzureAIServiceWorkspaceConnectionSchema

        return conn_class
