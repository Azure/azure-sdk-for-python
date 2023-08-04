# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ManagedIdentityAuthTypeWorkspaceConnectionProperties,
    NoneAuthTypeWorkspaceConnectionProperties,
    PATAuthTypeWorkspaceConnectionProperties,
    SASAuthTypeWorkspaceConnectionProperties,
    ServicePrincipalAuthTypeWorkspaceConnectionProperties,
    UsernamePasswordAuthTypeWorkspaceConnectionProperties,
)
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    WorkspaceConnectionPropertiesV2BasicResource as RestWorkspaceConnection,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ConnectionAuthType,
    AccessKeyAuthTypeWorkspaceConnectionProperties,
)
from azure.ai.ml._schema.workspace.connections.workspace_connection import WorkspaceConnectionSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import _snake_to_camel, camel_to_snake, dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._credentials import (
    ManagedIdentityConfiguration,
    PatTokenConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    UsernamePasswordConfiguration,
    AccessKeyConfiguration,
)
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict


@experimental
class WorkspaceConnection(Resource):
    """Azure ML workspace connection provides a secure way to store authentication and configuration information needed
    to connect and interact with the external resources.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: Union[
        ~azure.ai.ml.entities.PatTokenConfiguration, ~azure.ai.ml.entities.SasTokenConfiguration,
        ~azure.ai.ml.entities.UsernamePasswordConfiguration, ~azure.ai.ml.entities.ManagedIdentityConfiguration
        ~azure.ai.ml.entities.ServicePrincipalConfiguration, ~azure.ai.ml.entities.AccessKeyConfiguration
        ]
    :param type: The category of external resource for this connection.
    :type type: The type of workspace connection, possible values are: [
        "git", "python_feed", "container_registry", "feature_store", "s3", "snowflake",
         "azure_sql_db", "azure_synapse_analytics", "azure_my_sql_db", "azure_postgres_db"
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
        ],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.type = type
        self._target = target
        self._credentials = credentials
        self._metadata = json.loads(json.dumps(metadata))
        super().__init__(**kwargs)

    @property
    def type(self) -> str:
        """Type of the workspace connection, supported are 'git', 'python_feed' and 'container_registry'.

        :return: Type of the job.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, value: str):
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
    ]:
        """Credentials for workspace connection.

        :return: Credentials for workspace connection.
        :rtype: Union[
            PatTokenCredentialsConfiguration,
            SasTokenCredentialsConfiguration,
            UsernamePasswordCredentialsConfiguration,
            ManagedIdentityConfiguration,
            ServicePrincipalCredentialsConfiguration,
            AccessKeyCredentialsConfiguration,
        ]
        """
        return self._credentials

    @property
    def metadata(self) -> Dict[str, Any]:
        """Metadata for workspace connection.

        :return: Metadata for workspace connection.
        :rtype: Dict[str, Any]
        """
        return self._metadata

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
        loaded_data = load_from_dict(WorkspaceConnectionSchema, data, context, **kwargs)
        return loaded_data

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return WorkspaceConnectionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspaceConnection) -> "WorkspaceConnection":
        if not rest_obj:
            return None

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

        workspace_connection = WorkspaceConnection(
            id=rest_obj.id,
            name=rest_obj.name,
            target=properties.target,
            creation_context=SystemData._from_rest_object(rest_obj.system_data) if rest_obj.system_data else None,
            type=camel_to_snake(properties.category),
            credentials=credentials,
            metadata=properties.metadata if hasattr(properties, "metadata") else None,
        )

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
        elif auth_type is None:
            workspace_connection_properties_class = NoneAuthTypeWorkspaceConnectionProperties

        properties = workspace_connection_properties_class(
            target=self.target,
            credentials=self.credentials._to_workspace_connection_rest_object(),
            metadata=self.metadata,
            # auth_type=auth_type,
            category=_snake_to_camel(self.type),
        )

        return RestWorkspaceConnection(properties=properties)
