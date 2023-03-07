# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, TypeVar, Union

from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient
from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient
from azure.ai.ml._azure_environments import _get_storage_endpoint_from_metadata, _get_cloud_details
from azure.ai.ml._restclient.v2022_05_01.models import Workspace
from azure.ai.ml._restclient.v2022_10_01.models import DatastoreType
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils._arm_id_utils import (
    AMLNamedArmId,
    get_datastore_arm_id,
    get_resource_name_from_arm_id,
    is_ARM_id_for_resource,
    remove_aml_prefix,
)
from azure.ai.ml._utils._asset_utils import (
    IgnoreFile,
    _build_metadata_dict,
    _validate_path,
    get_ignore_file,
    get_object_hash,
    get_content_hash,
    get_content_hash_version,
)
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._storage_utils import (
    AzureMLDatastorePathUri,
    get_artifact_path_from_storage_url,
    get_storage_client,
)
from azure.ai.ml._utils.utils import is_mlflow_uri, is_url, retry, replace_between
from azure.ai.ml.constants._common import (
    SHORT_URI_FORMAT,
    STORAGE_ACCOUNT_URLS,
    MAX_ASSET_STORE_API_CALL_RETRIES,
    HTTPS_PREFIX,
)
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities._assets._artifacts.artifact import Artifact, ArtifactStorageInfo
from azure.ai.ml.entities._credentials import AccountKeyConfiguration
from azure.ai.ml.entities._datastore._constants import WORKSPACE_BLOB_STORE
from azure.ai.ml.exceptions import ErrorTarget, ValidationException
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.filedatalake import FileSasPermissions, generate_file_sas

module_logger = logging.getLogger(__name__)


def _get_datastore_name(*, datastore_name: Optional[str] = WORKSPACE_BLOB_STORE) -> str:
    datastore_name = WORKSPACE_BLOB_STORE if not datastore_name else datastore_name
    try:
        datastore_name = get_resource_name_from_arm_id(datastore_name)
    except (ValueError, AttributeError, ValidationException):
        module_logger.debug("datastore_name %s is not a full arm id. Proceed with a shortened name.\n", datastore_name)
    datastore_name = remove_aml_prefix(datastore_name)
    if is_ARM_id_for_resource(datastore_name):
        datastore_name = get_resource_name_from_arm_id(datastore_name)
    return datastore_name


def get_datastore_info(operations: DatastoreOperations, name: str) -> Dict[str, str]:
    """Get datastore account, type, and auth information."""
    datastore_info = {}
    if name:
        datastore = operations.get(name, include_secrets=True)
    else:
        datastore = operations.get_default(include_secrets=True)

    storage_endpoint = _get_storage_endpoint_from_metadata()
    credentials = datastore.credentials
    datastore_info["storage_type"] = datastore.type
    datastore_info["storage_account"] = datastore.account_name
    datastore_info["account_url"] = STORAGE_ACCOUNT_URLS[datastore.type].format(
        datastore.account_name, storage_endpoint
    )
    if isinstance(credentials, AccountKeyConfiguration):
        datastore_info["credential"] = credentials.account_key
    else:
        try:
            datastore_info["credential"] = credentials.sas_token
        except Exception as e:  # pylint: disable=broad-except
            if not hasattr(credentials, "sas_token"):
                datastore_info["credential"] = operations._credential
            else:
                raise e

    if datastore.type == DatastoreType.AZURE_BLOB:
        datastore_info["container_name"] = str(datastore.container_name)
    elif datastore.type == DatastoreType.AZURE_DATA_LAKE_GEN2:
        datastore_info["container_name"] = str(datastore.filesystem)
    else:
        raise Exception(
            f"Datastore type {datastore.type} is not supported for uploads. "
            f"Supported types are {DatastoreType.AZURE_BLOB} and {DatastoreType.AZURE_DATA_LAKE_GEN2}."
        )

    return datastore_info


def list_logs_in_datastore(ds_info: Dict[str, str], prefix: str, legacy_log_folder_name: str) -> Dict[str, str]:
    """Returns a dictionary of file name to blob or data lake uri with SAS token, matching the structure of
    RunDetails.logFiles.

    legacy_log_folder_name: the name of the folder in the datastore that contains the logs
        /azureml-logs/*.txt is the legacy log structure for commandJob and sweepJob
        /logs/azureml/*.txt is the legacy log structure for pipeline parent Job
    """
    if ds_info["storage_type"] not in [
        DatastoreType.AZURE_BLOB,
        DatastoreType.AZURE_DATA_LAKE_GEN2,
    ]:
        raise Exception("Only Blob and Azure DataLake Storage Gen2 datastores are supported.")

    storage_client = get_storage_client(
        credential=ds_info["credential"],
        container_name=ds_info["container_name"],
        storage_account=ds_info["storage_account"],
        storage_type=ds_info["storage_type"],
    )

    items = storage_client.list(starts_with=prefix + "/user_logs/")
    # Append legacy log files if present
    items.extend(storage_client.list(starts_with=prefix + legacy_log_folder_name))

    log_dict = {}
    for item_name in items:
        sub_name = item_name.split(prefix + "/")[1]
        if isinstance(storage_client, BlobStorageClient):
            token = generate_blob_sas(
                account_name=ds_info["storage_account"],
                container_name=ds_info["container_name"],
                blob_name=item_name,
                account_key=ds_info["credential"],
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(minutes=30),
            )
        elif isinstance(storage_client, Gen2StorageClient):
            token = generate_file_sas(  # pylint: disable=no-value-for-parameter
                account_name=ds_info["storage_account"],
                file_system_name=ds_info["container_name"],
                file_name=item_name,
                credential=ds_info["credential"],
                permission=FileSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(minutes=30),
            )

        log_dict[sub_name] = "{}/{}/{}?{}".format(ds_info["account_url"], ds_info["container_name"], item_name, token)
    return log_dict


def _get_default_datastore_info(datastore_operation):
    return get_datastore_info(datastore_operation, None)


def upload_artifact(
    local_path: str,
    datastore_operation: DatastoreOperations,
    operation_scope: OperationScope,
    datastore_name: Optional[str],
    asset_hash: Optional[str] = None,
    show_progress: bool = True,
    asset_name: Optional[str] = None,
    asset_version: Optional[str] = None,
    ignore_file: IgnoreFile = IgnoreFile(None),
    sas_uri=None,
) -> ArtifactStorageInfo:
    """Upload local file or directory to datastore."""
    if sas_uri:
        storage_client = get_storage_client(credential=None, storage_account=None, account_url=sas_uri)
    else:
        datastore_name = _get_datastore_name(datastore_name=datastore_name)
        datastore_info = get_datastore_info(datastore_operation, datastore_name)
        storage_client = get_storage_client(**datastore_info)

    artifact_info = storage_client.upload(
        local_path,
        asset_hash=asset_hash,
        show_progress=show_progress,
        name=asset_name,
        version=asset_version,
        ignore_file=ignore_file,
    )

    artifact = ArtifactStorageInfo(
        name=artifact_info["name"],
        version=artifact_info["version"],
        relative_path=artifact_info["remote path"],
        datastore_arm_id=get_datastore_arm_id(datastore_name, operation_scope) if not sas_uri else None,
        container_name=(
            storage_client.container if isinstance(storage_client, BlobStorageClient) else storage_client.file_system
        ),
        storage_account_url=datastore_info.get("account_url") if not sas_uri else sas_uri,
        indicator_file=artifact_info["indicator file"],
        is_file=Path(local_path).is_file(),
    )
    return artifact


def download_artifact(
    starts_with: Union[str, os.PathLike],
    destination: str,
    datastore_operation: DatastoreOperations,
    datastore_name: Optional[str],
    datastore_info: Optional[Dict] = None,
) -> str:
    """Download datastore path to local file or directory.

    :param Union[str, os.PathLike] starts_with: Prefix of blobs to download
    :param str destination: Path that files will be written to
    :param DatastoreOperations datastore_operation: Datastore operations
    :param Optional[str] datastore_name: name of datastore
    :param Dict datastore_info: the return value of invoking get_datastore_info
    :return str: Path that files were written to
    """
    starts_with = starts_with.as_posix() if isinstance(starts_with, Path) else starts_with
    datastore_name = _get_datastore_name(datastore_name=datastore_name)
    if datastore_info is None:
        datastore_info = get_datastore_info(datastore_operation, datastore_name)
    storage_client = get_storage_client(**datastore_info)
    storage_client.download(starts_with=starts_with, destination=destination)
    return destination


def download_artifact_from_storage_url(
    blob_url: str,
    destination: str,
    datastore_operation: DatastoreOperations,
    datastore_name: Optional[str],
) -> str:
    """Download datastore blob URL to local file or directory."""
    datastore_name = _get_datastore_name(datastore_name=datastore_name)
    datastore_info = get_datastore_info(datastore_operation, datastore_name)
    starts_with = get_artifact_path_from_storage_url(
        blob_url=str(blob_url), container_name=datastore_info.get("container_name")
    )
    return download_artifact(
        starts_with=starts_with,
        destination=destination,
        datastore_operation=datastore_operation,
        datastore_name=datastore_name,
        datastore_info=datastore_info,
    )


def download_artifact_from_aml_uri(uri: str, destination: str, datastore_operation: DatastoreOperations):
    """Downloads artifact pointed to by URI of the form `azureml://...` to destination.

    :param str uri: AzureML uri of artifact to download
    :param str destination: Path to download artifact to
    :param DatastoreOperations datastore_operation: datastore operations
    :return str: Path that files were downloaded to
    """
    parsed_uri = AzureMLDatastorePathUri(uri)
    return download_artifact(
        starts_with=parsed_uri.path,
        destination=destination,
        datastore_operation=datastore_operation,
        datastore_name=parsed_uri.datastore,
    )


def aml_datastore_path_exists(
    uri: str, datastore_operation: DatastoreOperations, datastore_info: Optional[dict] = None
):
    """Checks whether `uri` of the form "azureml://" points to either a directory or a file.

    :param str uri: azure ml datastore uri
    :param DatastoreOperations datastore_operation: Datastore operation
    :param dict datastore_info: return value of get_datastore_info
    """
    parsed_uri = AzureMLDatastorePathUri(uri)
    datastore_info = datastore_info or get_datastore_info(datastore_operation, parsed_uri.datastore)
    return get_storage_client(**datastore_info).exists(parsed_uri.path)


def _upload_to_datastore(
    operation_scope: OperationScope,
    datastore_operation: DatastoreOperations,
    path: Union[str, Path, os.PathLike],
    artifact_type: str,
    datastore_name: Optional[str] = None,
    show_progress: bool = True,
    asset_name: Optional[str] = None,
    asset_version: Optional[str] = None,
    asset_hash: Optional[str] = None,
    ignore_file: Optional[IgnoreFile] = None,
    sas_uri: Optional[str] = None,  # contains regstry sas url
) -> ArtifactStorageInfo:
    _validate_path(path, _type=artifact_type)
    if not ignore_file:
        ignore_file = get_ignore_file(path)
    if not asset_hash:
        asset_hash = get_object_hash(path, ignore_file)
    artifact = upload_artifact(
        str(path),
        datastore_operation,
        operation_scope,
        datastore_name,
        show_progress=show_progress,
        asset_hash=asset_hash,
        asset_name=asset_name,
        asset_version=asset_version,
        ignore_file=ignore_file,
        sas_uri=sas_uri,
    )
    return artifact


def _upload_and_generate_remote_uri(
    operation_scope: OperationScope,
    datastore_operation: DatastoreOperations,
    path: Union[str, Path, os.PathLike],
    artifact_type: str = ErrorTarget.ARTIFACT,
    datastore_name: str = WORKSPACE_BLOB_STORE,
    show_progress: bool = True,
) -> str:

    # Asset name is required for uploading to a datastore
    asset_name = str(uuid.uuid4())
    artifact_info = _upload_to_datastore(
        operation_scope=operation_scope,
        datastore_operation=datastore_operation,
        path=path,
        datastore_name=datastore_name,
        asset_name=asset_name,
        artifact_type=artifact_type,
        show_progress=show_progress,
    )

    path = artifact_info.relative_path
    datastore = AMLNamedArmId(artifact_info.datastore_arm_id).asset_name
    return SHORT_URI_FORMAT.format(datastore, path)


def _update_metadata(name, version, indicator_file, datastore_info) -> None:
    storage_client = get_storage_client(**datastore_info)

    if isinstance(storage_client, BlobStorageClient):
        _update_blob_metadata(name, version, indicator_file, storage_client)
    elif isinstance(storage_client, Gen2StorageClient):
        _update_gen2_metadata(name, version, indicator_file, storage_client)


def _update_blob_metadata(name, version, indicator_file, storage_client) -> None:
    container_client = storage_client.container_client
    if indicator_file.startswith(storage_client.container):
        indicator_file = indicator_file.split(storage_client.container)[1]
    blob = container_client.get_blob_client(blob=indicator_file)
    blob.set_blob_metadata(_build_metadata_dict(name=name, version=version))


def _update_gen2_metadata(name, version, indicator_file, storage_client) -> None:
    artifact_directory_client = storage_client.file_system_client.get_directory_client(indicator_file)
    artifact_directory_client.set_metadata(_build_metadata_dict(name=name, version=version))


def _generate_temporary_data_reference_id() -> str:
    """Generate a temporary data reference id."""
    return str(uuid.uuid4())


@retry(
    exceptions=HttpResponseError,
    failure_msg="Artifact upload exceeded maximum retries. Try again.",
    logger=module_logger,
    max_attempts=MAX_ASSET_STORE_API_CALL_RETRIES,
)
def _get_snapshot_temporary_data_reference(
    asset_name: str,
    asset_version: str,
    request_headers: Dict[str, str],
    workspace: Workspace,
    requests_pipeline: HttpPipeline,
) -> Tuple[str, str]:
    """
    Make a temporary data reference for an asset and return SAS uri and blob storage uri.
    :param asset_name: Name of the asset to be created
    :type asset_name: str
    :param asset_version: Version of the asset to be created
    :type asset_version: str
    :param request_headers: Request headers for API call
    :type request_headers: Dict[str, str]
    :param workspace: Workspace object
    :type workspace: azure.ai.ml._restclient.v2022_05_01.models.Workspace
    :param requests_pipeline: Proxy for sending HTTP requests
    :type requests_pipeline: azure.ai.ml._utils._http_utils.HttpPipeline
    :return: Existing asset's name and version, if found
    :rtype: Tuple[str, str]
    """

    # create temporary data reference
    temporary_data_reference_id = _generate_temporary_data_reference_id()

    # build and send request
    asset_id = (
        f"azureml://locations/{workspace.location}/workspaces/{workspace.workspace_id}/"
        f"codes/{asset_name}/versions/{asset_version}"
    )
    data = {
        "assetId": asset_id,
        "temporaryDataReferenceId": temporary_data_reference_id,
        "temporaryDataReferenceType": "TemporaryBlobReference",
    }
    data_encoded = json.dumps(data).encode("utf-8")
    serialized_data = json.loads(data_encoded)

    # make sure correct cloud endpoint is used
    location = workspace.location
    if location == "centraluseuap": # centraluseuap is master region and aliased with a special api url
        service_url = "https://master.api.azureml-test.ms/"
    else:
        cloud_endpoint = _get_cloud_details()["registry_discovery_endpoint"]
        service_url = replace_between(cloud_endpoint, HTTPS_PREFIX, ".", location)

    # send request
    request_url = f"{service_url}assetstore/v1.0/temporaryDataReference/createOrGet"
    response = requests_pipeline.post(request_url, json=serialized_data, headers=request_headers)

    if response.status_code != 200:
        raise HttpResponseError(response=response)

    response_json = json.loads(response.text())

    # get SAS uri for upload and blob uri for asset creation
    blob_uri = response_json["blobReferenceForConsumption"]["blobUri"]
    sas_uri = response_json["blobReferenceForConsumption"]["credential"]["sasUri"]

    return sas_uri, blob_uri


def _get_asset_by_hash(
    operations: "DatastoreOperations",
    hash_str: str,
    request_headers: Dict[str, str],
    workspace: Workspace,
    requests_pipeline: HttpPipeline,
) -> Dict[str, str]:
    """
    Check if an asset with the same hash already exists in the workspace. If so, return the asset name and version.
    :param operations: Datastore Operations object from MLClient
    :type operations: azure.ai.ml.operations._datastore_operations.DatastoreOperations
    :param hash_str: The hash of the specified local upload
    :type hash_str: str
    :param request_headers: Request headers for API call
    :type request_headers: Dict[str, str]
    :param workspace: Workspace object
    :type workspace: azure.ai.ml._restclient.v2022_05_01.models.Workspace
    :param requests_pipeline: Proxy for sending HTTP requests
    :type requests_pipeline: azure.ai.ml._utils._http_utils.HttpPipeline
    :return: Existing asset's name and version, if found
    :rtype: Optional[Dict[str, str]]
    """
    existing_asset = {}
    hash_version = get_content_hash_version()

    # get workspace credentials
    subscription_id = operations._subscription_id
    resource_group_name = operations._resource_group_name
    location = workspace.location

    # make sure correct cloud endpoint is used
    if location == "centraluseuap": # centraluseuap is master region and aliased with a special api url
        service_url = "https://master.api.azureml-test.ms/"
    else:
        cloud_endpoint = _get_cloud_details()["registry_discovery_endpoint"]
        service_url = replace_between(cloud_endpoint, HTTPS_PREFIX, ".", location)

    request_url = (
        f"{service_url}content/v2.0/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/"
        f"{workspace.name}/snapshots/getByHash?hash={hash_str}&hashVersion={hash_version}"
    )

    response = requests_pipeline.get(request_url, headers=request_headers)
    if response.status_code != 200:
        # If API is unresponsive, create new asset
        return None

    response_json = json.loads(response.text())
    existing_asset["name"] = response_json["name"]
    existing_asset["version"] = response_json["version"]

    return existing_asset


T = TypeVar("T", bound=Artifact)


def _check_and_upload_path(
    artifact: T,
    asset_operations: Union["DataOperations", "ModelOperations", "CodeOperations"],
    artifact_type: str,
    datastore_name: Optional[str] = None,
    sas_uri: Optional[str] = None,
    show_progress: bool = True,
) -> Tuple[T, str]:
    """Checks whether `artifact` is a path or a uri and uploads it to the datastore if necessary.

    param T artifact: artifact to check and upload param
    Union["DataOperations", "ModelOperations", "CodeOperations"]
    asset_operations:     the asset operations to use for uploading
    param str datastore_name: the name of the datastore to upload to
    param str sas_uri: the sas uri to use for uploading
    """

    datastore_name = artifact.datastore
    indicator_file = None
    if (
        hasattr(artifact, "local_path")
        and artifact.local_path is not None
        or (
            hasattr(artifact, "path")
            and artifact.path is not None
            and not (is_url(artifact.path) or is_mlflow_uri(artifact.path))
        )
    ):
        path = (
            Path(artifact.path)
            if hasattr(artifact, "path") and artifact.path is not None
            else Path(artifact.local_path)
        )
        if not path.is_absolute():
            path = Path(artifact.base_path, path).resolve()
        uploaded_artifact = _upload_to_datastore(
            asset_operations._operation_scope,
            asset_operations._datastore_operation,
            path,
            datastore_name=datastore_name,
            asset_name=artifact.name,
            asset_version=str(artifact.version),
            asset_hash=artifact._upload_hash if hasattr(artifact, "_upload_hash") else None,
            sas_uri=sas_uri,
            artifact_type=artifact_type,
            show_progress=show_progress,
            ignore_file=getattr(artifact, "_ignore_file", None),
        )
        indicator_file = uploaded_artifact.indicator_file  # reference to storage contents
        if artifact._is_anonymous:
            artifact.name, artifact.version = (
                uploaded_artifact.name,
                uploaded_artifact.version,
            )
        # Pass all of the upload information to the assets, and they will each construct the URLs that they support
        artifact._update_path(uploaded_artifact)
    return artifact, indicator_file


def _get_snapshot_path_info(artifact) -> Tuple[str, str, str]:
    """
    Validate an Artifact's local path and get its resolved path, ignore file, and hash
    :param artifact: Artifact object
    :type artifact: azure.ai.ml.entities._assets._artifacts.artifact.Artifact
    :return: Artifact's path, ignorefile, and hash
    :rtype: Tuple[str, str, str]
    """
    if (
        hasattr(artifact, "local_path")
        and artifact.local_path is not None
        or (
            hasattr(artifact, "path")
            and artifact.path is not None
            and not (is_url(artifact.path) or is_mlflow_uri(artifact.path))
        )
    ):
        path = (
            Path(artifact.path)
            if hasattr(artifact, "path") and artifact.path is not None
            else Path(artifact.local_path)
        )
        if not path.is_absolute():
            path = Path(artifact.base_path, path).resolve()

    _validate_path(path, _type=ErrorTarget.CODE)

    ignore_file = get_ignore_file(path)
    asset_hash = get_content_hash(path, ignore_file)

    return path, ignore_file, asset_hash


def _get_existing_snapshot_by_hash(
    datastore_operation,
    asset_hash,
    workspace: Workspace,
    requests_pipeline: HttpPipeline,
) -> Dict[str, str]:
    """
    Check if an asset with the same hash already exists in the workspace. If so, return the asset name and version.
    :param datastore_operation: Datastore Operations object from MLClient
    :type operations: azure.ai.ml.operations._datastore_operations.DatastoreOperations
    :param asset_hash: The hash of the specified local upload
    :type asset_hash: str
    :param workspace: Workspace object
    :type workspace: azure.ai.ml._restclient.v2022_05_01.models.Workspace
    :param requests_pipeline: Proxy for sending HTTP requests
    :type requests_pipeline: azure.ai.ml._utils._http_utils.HttpPipeline
    :return: Existing asset's name and version, if found
    :rtype: Optional[Dict[str, str]]
    """
    ws_base_url = datastore_operation._operation._client._base_url
    token = datastore_operation._credential.get_token(ws_base_url + "/.default").token
    request_headers = {"Authorization": "Bearer " + token}
    request_headers["Content-Type"] = "application/json; charset=UTF-8"

    existing_asset = _get_asset_by_hash(
        operations=datastore_operation,
        hash_str=asset_hash,
        request_headers=request_headers,
        workspace=workspace,
        requests_pipeline=requests_pipeline,
    )

    return existing_asset


def _upload_snapshot_to_datastore(
    operation_scope: OperationScope,
    datastore_operation: DatastoreOperations,
    path: Union[str, Path, os.PathLike],
    workspace: Workspace,
    requests_pipeline: HttpPipeline,
    datastore_name: str = None,
    show_progress: bool = True,
    asset_name: str = None,
    asset_version: str = None,
    asset_hash: str = None,
    ignore_file: IgnoreFile = IgnoreFile(),
    sas_uri: str = None,  # contains registry sas url
) -> ArtifactStorageInfo:
    """
    Upload a code snapshot to workspace datastore.
    :param operation_scope: Workspace scope information
    :type operation_scope: azure.ai.ml._scope_dependent_operations.OperationScope
    :param datastore_operation: Datastore Operations object from MLClient
    :type datastore_operation: azure.ai.ml.operations._datastore_operations.DatastoreOperations
    :param path: The local path of the artifact
    :type path: Union[str, Path, os.PathLike]
    :param workspace: Workspace object
    :type workspace: azure.ai.ml._restclient.v2022_05_01.models.Workspace
    :param requests_pipeline: Proxy for sending HTTP requests
    :type requests_pipeline: azure.ai.ml._utils._http_utils.HttpPipeline
    :param datastore_name: Name of the datastore to upload to
    :type datastore_name: str
    :param show_progress: Whether or not to show progress bar during upload, defaults to True
    :type show_progress: bool
    :param asset_name: Name of the asset to be created
    :type asset_name: str
    :param asset_version: Version of the asset to be created
    :type asset_version: str
    :param asset_hash: The hash of the specified local upload
    :type asset_hash: str
    :param ignore_file: Information about the path's .gitignore or .amlignore file, if exists
    :type ignore_file: azure.ai.ml._utils._asset_utils.IgnoreFile
    :param sas_uri: SAS uri for uploading to datastore
    :type sas_uri: str
    :return: Uploaded artifact's storage information
    :rtype: azure.ai.ml.entities._assets._artifacts.artifact.ArtifactStorageInfo
    """
    ws_base_url = datastore_operation._operation._client._base_url
    token = datastore_operation._credential.get_token(ws_base_url + "/.default").token
    request_headers = {"Authorization": "Bearer " + token}
    request_headers["Content-Type"] = "application/json; charset=UTF-8"

    if not sas_uri:
        sas_uri, blob_uri = _get_snapshot_temporary_data_reference(
            requests_pipeline=requests_pipeline,
            asset_name=asset_name,
            asset_version=asset_version,
            request_headers=request_headers,
            workspace=workspace,
        )

    artifact = upload_artifact(
        str(path),
        datastore_operation,
        operation_scope,
        datastore_name,
        show_progress=show_progress,
        asset_hash=asset_hash,
        asset_name=asset_name,
        asset_version=asset_version,
        ignore_file=ignore_file,
        sas_uri=sas_uri,
    )
    artifact.storage_account_url = blob_uri

    return artifact


def _check_and_upload_snapshot(
    artifact: T,
    asset_operations: Union["DataOperations", "ModelOperations", "CodeOperations"],
    path: Union[str, Path, os.PathLike],
    workspace: Workspace,
    requests_pipeline: HttpPipeline,
    ignore_file: IgnoreFile = None,
    datastore_name: str = WORKSPACE_BLOB_STORE,
    sas_uri: str = None,
    show_progress: bool = True,
) -> Tuple[T, str]:
    """Checks whether `artifact` is a path or a uri and uploads it to the
    datastore if necessary.
    param T artifact: artifact to check and upload param
    Union["DataOperations", "ModelOperations", "CodeOperations"]
    asset_operations:     the asset operations to use for uploading
    param str datastore_name: the name of the datastore to upload to
    param str sas_uri: the sas uri to use for uploading
    """
    uploaded_artifact = _upload_snapshot_to_datastore(
        operation_scope=asset_operations._operation_scope,
        datastore_operation=asset_operations._datastore_operation,
        path=path,
        workspace=workspace,
        requests_pipeline=requests_pipeline,
        datastore_name=datastore_name,
        asset_name=artifact.name,
        asset_version=str(artifact.version),
        asset_hash=artifact._upload_hash if hasattr(artifact, "_upload_hash") else None,
        show_progress=show_progress,
        sas_uri=sas_uri,
        ignore_file=ignore_file,
    )

    if artifact._is_anonymous:
        artifact.name, artifact.version = (
            uploaded_artifact.name,
            uploaded_artifact.version,
        )
    # Pass all of the upload information to the assets, and they will each construct the URLs that they support
    artifact._update_path(uploaded_artifact)

    return artifact


def _check_and_upload_env_build_context(
    environment: Environment,
    operations: "EnvironmentOperations",
    sas_uri=None,
    show_progress: bool = True,
) -> Environment:
    if environment.path:
        uploaded_artifact = _upload_to_datastore(
            operations._operation_scope,
            operations._datastore_operation,
            environment.path,
            asset_name=environment.name,
            asset_version=str(environment.version),
            asset_hash=environment._upload_hash,
            sas_uri=sas_uri,
            artifact_type=ErrorTarget.ENVIRONMENT,
            datastore_name=environment.datastore,
            show_progress=show_progress,
        )
        # TODO: Depending on decision trailing "/" needs to stay or not. EMS requires it to be present
        environment.build.path = uploaded_artifact.full_storage_path + "/"
    return environment
