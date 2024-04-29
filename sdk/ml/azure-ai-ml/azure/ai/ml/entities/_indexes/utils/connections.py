# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex auth connection utilities."""

import contextlib
import json
import os
import re
from typing import Callable, Optional, Union

from azure.ai.ml.entities._indexes.utils.logging import get_logger, packages_versions_for_compatibility
from azure.ai.ml.entities._indexes.utils.requests import create_session_with_retry, send_post_request

from azure.ai.ml.entities import WorkspaceConnection

with contextlib.suppress(Exception):
    from azure.core.credentials import TokenCredential

logger = get_logger("connections")


def get_connection_credential(
    config, credential: Optional[Union[TokenCredential, object]] = None, data_plane: bool = True
):
    """Get a credential for a connection. by default for data plane operations."""
    try:
        from azure.core.credentials import AzureKeyCredential
    except ImportError as e:
        raise ValueError(
            "Could not import azure-core python package. Please install it with `pip install azure-core`."
        ) from e
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as e:
        raise ValueError(
            "Could not import azure-identity python package. Please install it with `pip install azure-identity`."
        ) from e

    if config.get("connection_type", None) == "workspace_keyvault":
        from azureml.core import Run, Workspace

        run = Run.get_context()
        if hasattr(run, "experiment"):
            ws = run.experiment.workspace
        else:
            try:
                ws = Workspace(
                    subscription_id=config.get("connection", {}).get("subscription"),
                    resource_group=config.get("connection", {}).get("resource_group"),
                    workspace_name=config.get("connection", {}).get("workspace"),
                )
            except Exception as e:
                logger.warning(f"Could not get workspace '{config.get('connection', {}).get('workspace')}': {e}")
                # Fall back to looking for key in environment.
                import os

                key = os.environ.get(config.get("connection", {}).get("key"))
                if key is None:
                    raise ValueError(
                        f"Could not get workspace '{config.get('connection', {}).get('workspace')}' and no key named '{config.get('connection', {}).get('key')}' in environment"
                    ) from e
                return AzureKeyCredential(key)

        keyvault = ws.get_default_keyvault()
        connection_credential = AzureKeyCredential(keyvault.get_secret(config.get("connection", {}).get("key")))
    elif config.get("connection_type", None) == "workspace_connection":
        connection_id = config.get("connection", {}).get("id")
        connection = get_connection_by_id_v2(connection_id, credential=credential)
        connection_credential = connection_to_credential(connection, data_plane=data_plane)
    elif config.get("connection_type", None) == "environment":
        import os

        key = os.environ.get(config.get("connection", {}).get("key", "OPENAI_API_KEY"))
        connection_credential = (
            (credential if credential is not None else DefaultAzureCredential(process_timeout=60))
            if key is None
            else AzureKeyCredential(key)
        )
    else:
        connection_credential = credential if credential is not None else DefaultAzureCredential(process_timeout=60)

    return connection_credential


def workspace_connection_to_credential(connection: Union[dict, WorkspaceConnection]):
    """Get a credential for a workspace connection for control plane operations."""
    return connection_to_credential(connection, data_plane=False)


def connection_to_credential(connection: Union[dict, WorkspaceConnection], data_plane: bool = True):
    """Get a credential for a workspace connection for data plane operations by default."""
    if isinstance(connection, dict):
        props = connection["properties"]
        auth_type = props.get("authType", props.get("AuthType"))
        if auth_type == "ApiKey":
            from azure.core.credentials import AzureKeyCredential

            return AzureKeyCredential(props["credentials"]["key"])
        elif auth_type == "PAT":
            from azure.core.credentials import AccessToken

            return AccessToken(props["credentials"]["pat"], props.get("expiresOn", None))
        elif auth_type == "AAD":
            return _token_provider_for_AAD_connection(data_plane)

        elif auth_type == "CustomKeys":
            # OpenAI connections are made with CustomKeys auth, so we can try to access the key using known structure
            from azure.core.credentials import AzureKeyCredential

            if (
                connection.get("metadata", {})
                .get("azureml.flow.connection_type", connection.get("ApiType", connection.get("apiType", "")))
                .lower()
                == "openai"
            ):
                # Try to get the the key with api_key, if fail, default to regular CustomKeys handling
                try:
                    key = props["credentials"]["keys"]["api_key"]
                    return AzureKeyCredential(key)
                except Exception as e:
                    logger.warning(f"Could not get key using api_key, using default handling: {e}")
            key_dict = props["credentials"]["keys"]
            if len(key_dict.keys()) != 1:
                raise ValueError(
                    f"Only connections with a single key can be used. Number of keys present: {len(key_dict.keys())}"
                )
            return AzureKeyCredential(props["credentials"]["keys"][list(key_dict.keys())[0]])
        else:
            raise ValueError(f"Unknown auth type '{auth_type}'")
    elif isinstance(connection, WorkspaceConnection):
        if not connection.credentials:
            if connection.properties.get("authType", connection.properties.get("AuthType", "")).lower() == "aad":
                logger.info(f"The connection '{connection.name}' is a {type(connection)} with AAD auth type.")
                return _token_provider_for_AAD_connection(data_plane)
            raise ValueError(
                f"Unknown auth type '{connection.properties.get('authType', 'None')}' for connection '{connection.name}'"
            )
        elif connection.credentials.type.lower() == "api_key":
            from azure.core.credentials import AzureKeyCredential

            return AzureKeyCredential(connection.credentials.key)
        elif connection.credentials.type.lower() == "pat":
            from azure.core.credentials import AccessToken

            return AccessToken(connection.credentials.pat, 0)
        elif connection.credentials.type.lower() == "custom_keys":
            if connection._metadata.get("azureml.flow.connection_type", "").lower() == "openai":
                from azure.core.credentials import AzureKeyCredential

                try:
                    key = connection.credentials.keys.api_key
                    return AzureKeyCredential(key)
                except Exception as e:
                    logger.warning(f"Could not get key using api_key, using default handling: {e}")
            key_dict = connection.credentials.keys
            if len(key_dict.keys()) != 1:
                raise ValueError(
                    f"Only connections with a single key can be used. Number of keys present: {len(key_dict.keys())}"
                )
            return AzureKeyCredential(connection.credentials.keys[list(key_dict.keys())[0]])
        else:
            raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")
    else:
        if connection.credentials.type.lower() == "api_key":
            from azure.core.credentials import AzureKeyCredential

            return AzureKeyCredential(connection.credentials.key)
        else:
            raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")


def _token_provider_for_AAD_connection(data_plane: bool = True) -> Callable[[], str]:
    """Get a credential for a workspace connection for data plane operations by default."""
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError as e:
        raise ValueError(
            "Please install azure-identity with `pip install azure-identity --upgrade`."
        ) from e

    if data_plane:
        logger.info("Getting the token provider for data plane access.")
        return get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    else:
        logger.info("Getting DefaultAzureCredential for control plane access.")
        return get_bearer_token_provider(DefaultAzureCredential(), "https://management.azure.com/.default")


def snake_case_to_camel_case(s):
    """Convert snake case to camel case."""
    first = True
    final = ""
    for word in s.split("_"):
        if first:
            first = False
            final += word
        else:
            final += word.title()
    return final


def recursive_dict_keys_snake_to_camel(d: dict, skip_keys=[]) -> dict:
    """Convert snake case to camel case in dict keys."""
    new_dict = {}
    for k, v in d.items():
        if k not in skip_keys:
            if isinstance(v, dict):
                v = recursive_dict_keys_snake_to_camel(v, skip_keys=skip_keys)
            if isinstance(k, str):
                new_key = snake_case_to_camel_case(k)
                new_dict[new_key] = v
        else:
            new_dict[k] = v
    return new_dict


def get_connection_by_id_v2(
    connection_id: str, credential: TokenCredential = None, client: str = "sdk"
) -> Union[dict, WorkspaceConnection]:
    """
    Get a connection by id using azure.ai.ml.

    If an AOAI or ACS connection uses AAD auth
        - azure.ai.ml >= v 1.14.0, set connection.properties["authType"] to "AAD"
        - azure.ai.ml <= v 1.13.0, set connection["properties"]["authType"] to "AAD"
    """
    uri_match = re.match(
        r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)",
        connection_id,
        flags=re.IGNORECASE,
    )

    if uri_match is None:
        logger.error(f"Invalid connection_id {connection_id}, expecting Azure Machine Learning resource ID")
        raise ValueError(f"Invalid connection id {connection_id}")

    logger.info(f"Getting workspace connection: {uri_match.group(4)}")

    if credential is None:
        from azure.identity import DefaultAzureCredential

        if os.environ.get("AZUREML_RUN_ID", None) is not None:
            from azureml.dataprep.api._aml_auth._azureml_token_authentication import AzureMLTokenAuthentication

            credential = AzureMLTokenAuthentication._initialize_aml_token_auth()
        else:
            credential = DefaultAzureCredential(process_timeout=60)

    logger.info(f"Using auth: {type(credential)}")

    from azure.ai.ml import MLClient
    if client == "sdk" and MLClient is not None:
        logger.info("Getting workspace connection via MLClient")
        ml_client = MLClient(
            credential=credential,
            subscription_id=uri_match.group(1),
            resource_group_name=uri_match.group(2),
            workspace_name=uri_match.group(3),
        )

        if os.environ.get("AZUREML_RUN_ID", None) is not None:
            # In AzureML Run context, we need to use workspaces internal endpoint that will accept AzureMLToken auth.
            old_base_url = ml_client.connections._operation._client._base_url
            ml_client.connections._operation._client._base_url = (
                f"{os.environ.get('AZUREML_SERVICE_ENDPOINT')}/rp/workspaces"
            )

        logger.info(f"Using ml_client base_url: {ml_client.connections._operation._client._base_url}")

        list_secrets_response = ml_client.connections._operation.list_secrets(
            connection_name=uri_match.group(4),
            resource_group_name=ml_client.resource_group_name,
            workspace_name=ml_client.workspace_name,
        )

        try:
            connection = WorkspaceConnection._from_rest_object(list_secrets_response)
            logger.info(f"Parsed Connection: {connection.id}")

            if connection.credentials is None:
                if connection.type == "custom":
                    from azure.core.credentials import AzureKeyCredential

                    connection.credentials = AzureKeyCredential(
                        list_secrets_response.properties.credentials.keys["api_key"]
                    )
                elif connection.type == "azure_open_ai":
                    # When the connection's AuthType is AAD, with azure-ai-ml >= 1.14.0,
                    # WorkspaceConnection._from_rest_object returns connection with credentials as None
                    from azure.ai.ml.entities import AzureOpenAIWorkspaceConnection

                    if isinstance(connection, AzureOpenAIWorkspaceConnection):
                        connection.properties["authType"] = "AAD"
                elif connection.type == "cognitive_search":
                    from azure.ai.ml.entities import AzureAISearchWorkspaceConnection

                    if isinstance(connection, AzureAISearchWorkspaceConnection):
                        connection.properties["authType"] = "AAD"
                else:
                    raise Exception(f"Could not parse connection credentials for connection: {connection.id}")
        except Exception as e:
            logger.warning(f"Failed to parse connection into azure-ai-ml sdk object, returning response as is: {e}")
            connection = recursive_dict_keys_snake_to_camel(
                list_secrets_response.as_dict(), skip_keys=["credentials", "metadata"]
            )
            # When the connection's AuthType is AAD, with azure-ai-ml <= 1.13.0, WorkspaceConnection._from_rest_object
            # will throw an UnboundLocalError, the authType is None in the list_secrets_response.
            if isinstance(e, UnboundLocalError) and list_secrets_response.properties.auth_type is None:
                connection["properties"] = list_secrets_response.properties.as_dict()
                connection["properties"]["authType"] = "AAD"

        if os.environ.get("AZUREML_RUN_ID", None) is not None:
            ml_client.connections._operation._client._base_url = old_base_url
    else:
        logger.info("Getting workspace connection via REST as fallback")
        return get_connection_by_id_v1(connection_id, credential)

    return connection


def get_id_from_connection(connection: Union[dict, WorkspaceConnection]) -> str:
    """Get a connection id from a connection."""
    if isinstance(connection, dict):
        return connection["id"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.id
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_target_from_connection(connection: Union[dict, WorkspaceConnection]) -> str:
    """Get a connection target from a connection."""
    if isinstance(connection, dict):
        return connection["properties"]["target"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.target
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_metadata_from_connection(connection: Union[dict, WorkspaceConnection]) -> dict:
    """Get a connection metadata from a connection."""
    if isinstance(connection, dict):
        return connection["properties"]["metadata"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.tags
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_connection_by_name_v2(
    workspace, name: str, credential: Optional[Union[TokenCredential, object]] = None
) -> dict:
    """Get a connection from a workspace."""
    try:
        bearer_token = None
        if credential:
            bearer_token = credential.get_token("https://management.azure.com/.default").token
        if not bearer_token:
            if hasattr(workspace._auth, "get_token"):
                bearer_token = workspace._auth.get_token("https://management.azure.com/.default").token
            else:
                bearer_token = workspace._auth.token
    except Exception as e:
        raise ValueError("Fail to get bearer token.") from e

    endpoint = workspace.service_context._get_endpoint("api")
    url = f"{endpoint}/rp/workspaces/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}/listsecrets?api-version=2023-02-01-preview"
    resp = send_post_request(url, {"Authorization": f"Bearer {bearer_token}", "content-type": "application/json"}, {})

    return resp.json()


def get_connection_by_id_v1(connection_id: str, credential: Optional[TokenCredential] = None) -> dict:
    """Get a connection from a workspace."""
    uri_match = re.match(
        r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)",
        connection_id,
    )

    if uri_match is None:
        logger.error(f"Invalid connection_id {connection_id}, expecting Azure Machine Learning resource ID")
        raise ValueError(f"Invalid connection id {connection_id}")

    from azureml.core import Run, Workspace

    run = Run.get_context()
    if hasattr(run, "experiment"):
        ws = run.experiment.workspace
    else:
        try:
            ws = Workspace(
                subscription_id=uri_match.group(1), resource_group=uri_match.group(2), workspace_name=uri_match.group(3)
            )
        except Exception as e:
            logger.warning(f"Could not get workspace '{uri_match.group(3)}': {e}")
            raise ValueError(f"Could not get workspace '{uri_match.group(3)}'") from e

    return get_connection_by_name_v2(ws, uri_match.group(4))


def send_put_request(url, headers, payload):
    """Send a PUT request."""
    with create_session_with_retry() as session:
        response = session.put(url, data=json.dumps(payload), headers=headers)
        # Raise an exception if the response contains an HTTP error status code
        response.raise_for_status()

    return response.json()


def create_connection_v2(workspace, name, category: str, target: str, auth_type: str, credentials: dict, metadata: str):
    """Create a connection in a workspace."""
    url = f"https://management.azure.com/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}?api-version=2023-04-01-preview"

    resp = send_put_request(
        url,
        {
            "Authorization": f"Bearer {workspace._auth.get_token('https://management.azure.com/.default').token}",
            "content-type": "application/json",
        },
        {
            "properties": {
                "category": category,
                "target": target,
                "authType": auth_type,
                "credentials": credentials,
                "metadata": metadata,
            }
        },
    )

    return resp
