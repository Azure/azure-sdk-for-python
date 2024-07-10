# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex auth connection utilities."""
import json
import os
import re
from typing import Optional, Union

from azure.ai.resources._index._utils.logging import get_logger
from azure.ai.resources._index._utils.requests import create_session_with_retry, send_post_request

try:
    from azure.ai.resources.entities import BaseConnection
except Exception:
    BaseConnection = None  # type: ignore[misc,assignment]
try:
    from azure.ai.ml import MLClient
    from azure.ai.ml.entities import WorkspaceConnection
except Exception:
    MLClient = None
    WorkspaceConnection = None
try:
    from azure.core.credentials import TokenCredential
except Exception:
    TokenCredential = object  # type: ignore[misc,assignment]

logger = get_logger("connections")

def get_pinecone_environment(config, credential: Optional[TokenCredential] = None):
    """Get the Pinecone project environment from a connection."""
    connection_type = config.get("connection_type", None)
    if connection_type != "workspace_connection":
        raise ValueError(f"Unsupported connection type for Pinecone index: {connection_type}")

    connection_id = config.get("connection", {}).get("id")
    connection = get_connection_by_id_v2(connection_id, credential=credential)
    return get_metadata_from_connection(connection)["environment"]


def get_connection_credential(config, credential: Optional[TokenCredential] = None):
    """Get a credential for a connection."""

    connection_credential: Union[TokenCredential, AzureKeyCredential]

    try:
        from azure.core.credentials import AzureKeyCredential
    except ImportError as e:
        raise ValueError(
            "Could not import azure-core python package. "
            "Please install it with `pip install azure-core`."
        ) from e
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as e:
        raise ValueError(
            "Could not import azure-identity python package. "
            "Please install it with `pip install azure-identity`."
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
                    workspace_name=config.get("connection", {}).get("workspace")
                )
            except Exception as e:
                logger.warning(f"Could not get workspace '{config.get('connection', {}).get('workspace')}': {e}")
                # Fall back to looking for key in environment.
                import os
                key = os.environ.get(config.get("connection", {}).get("key"))
                if key is None:
                    raise ValueError(f"Could not get workspace '{config.get('connection', {}).get('workspace')}' and no key named '{config.get('connection', {}).get('key')}' in environment")
                return AzureKeyCredential(key)

        keyvault = ws.get_default_keyvault()
        connection_credential = AzureKeyCredential(keyvault.get_secret(config.get("connection", {}).get("key")))
    elif config.get("connection_type", None) == "workspace_connection":
        connection_id = config.get("connection", {}).get("id")
        connection = get_connection_by_id_v2(connection_id, credential=credential)
        connection_credential = connection_to_credential(connection)
    elif config.get("connection_type", None) == "environment":
        import os
        key = os.environ.get(config.get("connection", {}).get("key", "OPENAI_API_KEY"))
        if key:
            connection_credential = AzureKeyCredential(key)
        else:
            connection_credential = credential if credential is not None else DefaultAzureCredential(process_timeout=60)
    else:
        connection_credential = credential if credential is not None else DefaultAzureCredential(process_timeout=60)

    return connection_credential


def workspace_connection_to_credential(connection: Union[dict, BaseConnection, WorkspaceConnection]):
    """Get a credential for a workspace connection."""
    return connection_to_credential(connection)


def connection_to_credential(connection: Union[dict, BaseConnection, WorkspaceConnection]):
    """Get a credential for a workspace connection."""
    if isinstance(connection, dict):
        props = connection["properties"]
        auth_type = props.get("authType", props.get("AuthType"))
        if auth_type == "ApiKey":
            from azure.core.credentials import AzureKeyCredential
            return AzureKeyCredential(props["credentials"]["key"])
        elif auth_type == "PAT":
            from azure.core.credentials import AccessToken
            return AccessToken(props["credentials"]["pat"], props.get("expiresOn", None))
        elif auth_type == "CustomKeys":
            # OpenAI connections are made with CustomKeys auth, so we can try to access the key using known structure
            from azure.core.credentials import AzureKeyCredential
            if connection.get("metadata", {}).get("azureml.flow.connection_type", None) == "OpenAI":
                # Try to get the the key with api_key, if fail, default to regular CustomKeys handling
                try:
                    key = props["credentials"]["keys"]["api_key"]
                    return AzureKeyCredential(key)
                except Exception as e:
                    logger.warning(f"Could not get key using api_key, using default handling: {e}")
            key_dict = props["credentials"]["keys"]
            if len(key_dict.keys()) != 1:
                raise ValueError(f"Only connections with a single key can be used. Number of keys present: {len(key_dict.keys())}")
            return AzureKeyCredential(props["credentials"]["keys"][list(key_dict.keys())[0]])
        else:
            raise ValueError(f"Unknown auth type '{auth_type}'")
    elif isinstance(connection, WorkspaceConnection):
        if connection.credentials.type.lower() == "api_key":
            from azure.core.credentials import AzureKeyCredential
            return AzureKeyCredential(connection.credentials.key)
        elif connection.credentials.type.lower() == "pat":
            from azure.core.credentials import AccessToken
            return AccessToken(connection.credentials.pat, connection.credentials.expires_on)
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
                raise ValueError(f"Only connections with a single key can be used. Number of keys present: {len(key_dict.keys())}")
            return AzureKeyCredential(connection.credentials.keys[list(key_dict.keys())[0]])
        else:
            raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")
    else:
        if connection.credentials.type.lower() == "api_key":
            from azure.core.credentials import AzureKeyCredential
            return AzureKeyCredential(connection.credentials.key)
        else:
            raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")


def get_connection_by_id_v2(connection_id: str, credential: Optional[TokenCredential] = None, client: str = "sdk") -> Union[dict, WorkspaceConnection, BaseConnection]:
    """
    Get a connection by id using azure.ai.ml or azure.ai.resources.

    If azure.ai.ml is installed, use that, otherwise use azure.ai.resources.
    """
    uri_match = re.match(r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)", connection_id, flags=re.IGNORECASE)

    if uri_match is None:
        logger.error(f"Invalid connection_id {connection_id}, expecting Azure Machine Learning resource ID")
        raise ValueError(f"Invalid connection id {connection_id}")

    logger.info(f"Getting workspace connection: {uri_match.group(4)}")

    from azureml.dataprep.api._aml_auth._azureml_token_authentication import AzureMLTokenAuthentication

    if credential is None:
        from azure.identity import DefaultAzureCredential

        if os.environ.get("AZUREML_RUN_ID", None) is not None:
            credential = AzureMLTokenAuthentication._initialize_aml_token_auth()
        else:
            credential = credential if credential is not None else DefaultAzureCredential(process_timeout=60)

    logger.info(f"Using auth: {type(credential)}")

    if client == "sdk" and MLClient is not None:
        logger.info("Getting workspace connection via MLClient")
        ml_client = MLClient(
            credential=credential,
            subscription_id=uri_match.group(1),
            resource_group_name=uri_match.group(2),
            workspace_name=uri_match.group(3)
        )

        if os.environ.get("AZUREML_RUN_ID", None) is not None:
            # In AzureML Run context, we need to use workspaces internal endpoint that will accept AzureMLToken auth.
            old_base_url = ml_client.connections._operation._client._base_url
            ml_client.connections._operation._client._base_url = f"{os.environ.get('AZUREML_SERVICE_ENDPOINT')}/rp/workspaces"

        logger.info(f"Using ml_client base_url: {ml_client.connections._operation._client._base_url}")

        list_secrets_response = ml_client.connections._operation.list_secrets(
            connection_name=uri_match.group(4),
            resource_group_name=ml_client.resource_group_name,
            workspace_name=ml_client.workspace_name,
        )
        connection = WorkspaceConnection._from_rest_object(list_secrets_response)
        logger.info(f"Got Connection: {connection.id}")

        if os.environ.get("AZUREML_RUN_ID", None) is not None:
            ml_client.connections._operation._client._base_url = old_base_url
    else:
        logger.info("Getting workspace connection via REST as fallback")
        return get_connection_by_id_v1(connection_id, credential)

    return connection


def get_id_from_connection(connection: Union[dict, WorkspaceConnection, BaseConnection]) -> Optional[str]:
    """Get a connection id from a connection."""
    if isinstance(connection, dict):
        return connection["id"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.id
    elif isinstance(connection, BaseConnection):
        return connection.id
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_target_from_connection(connection: Union[dict, WorkspaceConnection, BaseConnection]) -> str:
    """Get a connection target from a connection."""
    if isinstance(connection, dict):
        return connection["properties"]["target"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.target
    elif isinstance(connection, BaseConnection):
        return connection.target
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_metadata_from_connection(connection: Union[dict, WorkspaceConnection, BaseConnection]) -> dict:
    """Get a connection metadata from a connection."""
    if isinstance(connection, dict):
        return connection["properties"]["metadata"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.metadata
    elif isinstance(connection, BaseConnection):
        return connection.metadata
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_connection_by_name_v2(workspace, name: str) -> dict:
    """Get a connection from a workspace."""
    if hasattr(workspace._auth, "get_token"):
        bearer_token = workspace._auth.get_token("https://management.azure.com/.default").token
    else:
        bearer_token = workspace._auth.token

    endpoint = workspace.service_context._get_endpoint("api")
    url = f"{endpoint}/rp/workspaces/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}/listsecrets?api-version=2023-02-01-preview"
    resp = send_post_request(url, {
        "Authorization": f"Bearer {bearer_token}",
        "content-type": "application/json"
    }, {})

    return resp.json()


def get_connection_by_id_v1(connection_id: str, credential: Optional[TokenCredential] = None) -> dict:
    """Get a connection from a workspace."""
    uri_match = re.match(r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)", connection_id)

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
                subscription_id=uri_match.group(1),
                resource_group=uri_match.group(2),
                workspace_name=uri_match.group(3)
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

    resp = send_put_request(url, {
        "Authorization": f"Bearer {workspace._auth.get_token('https://management.azure.com/.default').token}",
        "content-type": "application/json"
    }, {
        "properties": {
            "category": category,
            "target": target,
            "authType": auth_type,
            "credentials": credentials,
            "metadata": metadata
        }
    })

    return resp
