# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
from typing import List, Optional, Dict, TypeVar, Union, Tuple
from pathlib import Path
import uuid
from azure.ai.ml._azure_environments import ENDPOINT_URLS, _get_cloud_details
from azure.ai.ml._ml_exceptions import ValidationException
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml._utils._storage_utils import get_storage_client
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities._assets._artifacts.artifact import Artifact, ArtifactStorageInfo
from azure.ai.ml.entities._datastore.credentials import AccountKeyCredentials
from azure.ai.ml._utils._arm_id_utils import (
    get_datastore_arm_id,
    get_resource_name_from_arm_id,
    remove_aml_prefix,
    is_ARM_id_for_resource,
)
from azure.ai.ml._utils._asset_utils import (
    _validate_path,
    get_object_hash,
    get_ignore_file,
    IgnoreFile,
    _build_metadata_dict,
)
from azure.ai.ml._utils._storage_utils import get_artifact_path_from_storage_url, AzureMLDatastorePathUri
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._restclient.v2021_10_01.models import (
    DatastoreType,
)
from azure.ai.ml._utils.utils import is_url, is_mlflow_uri
from azure.ai.ml._utils._arm_id_utils import AMLNamedArmId
from azure.ai.ml.constants import SHORT_URI_FORMAT, STORAGE_ACCOUNT_URLS
from azure.ai.ml.entities._datastore._constants import WORKSPACE_BLOB_STORE

module_logger = logging.getLogger(__name__)


def _get_datastore_name(*, datastore_name: Optional[str] = WORKSPACE_BLOB_STORE) -> str:
    datastore_name = WORKSPACE_BLOB_STORE if not datastore_name else datastore_name
    try:
        datastore_name = get_resource_name_from_arm_id(datastore_name)
    except (ValueError, AttributeError, ValidationException):
        module_logger.debug(f"datastore_name {datastore_name} is not a full arm id. Proceed with a shortened name.\n")
    datastore_name = remove_aml_prefix(datastore_name)
    if is_ARM_id_for_resource(datastore_name):
        datastore_name = get_resource_name_from_arm_id(datastore_name)
    return datastore_name


def _build_datastore_info(datastore, operations) -> Dict[str, str]:
    """
    Get datastore account, type, and auth information
    """
    datastore_info = {}
    cloud_details = _get_cloud_details()
    storage_endpoint = cloud_details.get(ENDPOINT_URLS.STORAGE_ENDPOINT)
    credentials = datastore.credentials
    datastore_info["storage_type"] = datastore.type
    datastore_info["storage_account"] = datastore.account_name
    datastore_info["account_url"] = STORAGE_ACCOUNT_URLS[datastore.type].format(
        datastore.account_name, storage_endpoint
    )
    if isinstance(credentials, AccountKeyCredentials):
        datastore_info["credential"] = credentials.account_key
    else:
        try:
            datastore_info["credential"] = credentials.sas_token
        except Exception as e:
            if not hasattr(credentials, "sas_token"):
                datastore_info["credential"] = operations._credential
            else:
                raise e

    if datastore.type == DatastoreType.AZURE_BLOB:
        datastore_info["container_name"] = str(datastore.container_name)
    elif datastore.type == DatastoreType.AZURE_DATA_LAKE_GEN2:
        datastore_info["container_name"] = str(datastore.filesystem)
    elif datastore.type == DatastoreType.AZURE_FILE:
        datastore_info["container_name"] = str(datastore.file_share_name)
    else:
        datastore_info["container_name"] = ""
        module_logger.warning(f"Warning: datastore type {datastore.type} may not be supported for uploads.")
    return datastore_info


def get_datastore_info(operations: DatastoreOperations, name: str) -> Dict[str, str]:
    """
    Get datastore account, type, and auth information
    """
    if name:
        datastore = operations.get(name, include_secrets=True)
    else:
        datastore = operations.get_default(include_secrets=True)
    return _build_datastore_info(datastore, operations)


async def get_datastore_info_async(operations: DatastoreOperations, name: str) -> Dict[str, str]:
    """
    Get datastore account, type, and auth information
    """
    if name:
        datastore = await operations.get(name, include_secrets=True)
    else:
        datastore = await operations.get_default(include_secrets=True)
    return _build_datastore_info(datastore, operations)


def _build_logs(ds_info: Dict[str, str], items: List[str], prefix: str, storage_client) -> Dict[str, str]:
    log_dict = {}
    for item_name in items:
        sub_name = item_name.split(prefix + "/")[1]
        token = storage_client.generate_sas(
            account_name=ds_info["storage_account"],
            account_key=ds_info["credential"],
            item_path=ds_info["container_name"],
            item_name=item_name
        )
        log_dict[sub_name] = "{}/{}/{}?{}".format(ds_info["account_url"], ds_info["container_name"], item_name, token)
    return log_dict


def list_logs_in_datastore(ds_info: Dict[str, str], prefix: str, legacy_log_folder_name: str) -> Dict[str, str]:
    """
    Returns a dictionary of file name to blob or data lake uri with SAS token, matching the structure of RunDetails.logFiles

    legacy_log_folder_name: the name of the folder in the datastore that contains the logs
        /azureml-logs/*.txt is the legacy log structure for commandJob and sweepJob
        /logs/azureml/*.txt is the legacy log structure for pipeline parent Job
    """
    if ds_info["storage_type"] not in [DatastoreType.AZURE_BLOB, DatastoreType.AZURE_DATA_LAKE_GEN2]:
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
    return _build_logs(ds_info, items, prefix, storage_client)


async def list_logs_in_datastore_async(ds_info: Dict[str, str], prefix: str, legacy_log_folder_name: str) -> Dict[str, str]:
    """
    Returns a dictionary of file name to blob or data lake uri with SAS token, matching the structure of RunDetails.logFiles

    legacy_log_folder_name: the name of the folder in the datastore that contains the logs
        /azureml-logs/*.txt is the legacy log structure for commandJob and sweepJob
        /logs/azureml/*.txt is the legacy log structure for pipeline parent Job
    """
    if ds_info["storage_type"] not in [DatastoreType.AZURE_BLOB, DatastoreType.AZURE_DATA_LAKE_GEN2]:
        raise Exception("Only Blob and Azure DataLake Storage Gen2 datastores are supported.")

    storage_client = get_storage_client(
        credential=ds_info["credential"],
        container_name=ds_info["container_name"],
        storage_account=ds_info["storage_account"],
        storage_type=ds_info["storage_type"],
        use_async=True
    )

    items = await storage_client.list(starts_with=prefix + "/user_logs/")
    # Append legacy log files if present
    items.extend(await storage_client.list(starts_with=prefix + legacy_log_folder_name))
    return _build_logs(ds_info, items, prefix, storage_client)


def _get_default_datastore_info(datastore_operation):
    return get_datastore_info(datastore_operation, None)


def upload_artifact(
    local_path: str,
    datastore_operation: DatastoreOperations,
    operation_scope: OperationScope,
    datastore_name: Optional[str],
    asset_hash: str = None,
    show_progress: bool = True,
    asset_name: str = None,
    asset_version: str = None,
    ignore_file: IgnoreFile = IgnoreFile(None),
    sas_uri=None,
) -> ArtifactStorageInfo:
    """
    Upload local file or directory to datastore
    """
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
        container_name=storage_client.item_path,
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
    datastore_info: Dict = None,
) -> str:
    """
    Download datastore path to local file or directory.

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
    """
    Download datastore blob URL to local file or directory.
    """
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
    """Downloads artifact pointed to by URI of the form `azureml://...` to destination

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


def aml_datastore_path_exists(uri: str, datastore_operation: DatastoreOperations, datastore_info: dict = None):
    """Checks whether `uri` of the form "azureml://" points to either a directory or a file

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
    datastore_name: str = None,
    show_progress: bool = True,
    asset_name: str = None,
    asset_version: str = None,
    asset_hash: str = None,
    ignore_file: IgnoreFile = None,
    sas_uri: str = None,  # contains regstry sas url
) -> ArtifactStorageInfo:
    _validate_path(path)
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
    datastore_name: str = None,
) -> str:

    # Asset name is required for uploading to a datastore
    asset_name = str(uuid.uuid4())
    artifact_info = _upload_to_datastore(
        operation_scope=operation_scope,
        datastore_operation=datastore_operation,
        path=path,
        datastore_name=datastore_name,
        asset_name=asset_name,
    )

    path = artifact_info.relative_path
    datastore = AMLNamedArmId(artifact_info.datastore_arm_id).asset_name
    return SHORT_URI_FORMAT.format(datastore, path)


def _update_metadata(name: str, version: str, indicator_file: str, datastore_info) -> None:
    storage_client = get_storage_client(**datastore_info)
    storage_client.update_metadata(name, version, indicator_file)


T = TypeVar("T", bound=Artifact)


def _check_and_upload_path(
    artifact: T,
    asset_operations: Union["DatasetOperations", "DataOperations", "ModelOperations", "CodeOperations"],
    datastore_name: str = None,
    sas_uri: str = None,
) -> Tuple[T, str]:
    """Checks whether `artifact` is a path or a uri and uploads it to the datastore if necessary.
    param T artifact: artifact to check and upload
    param Union["DatasetOperations", "DataOperations", "ModelOperations", "CodeOperations"] asset_operations:
        the asset operations to use for uploading
    param str datastore_name: the name of the datastore to upload to
    param str sas_uri: the sas uri to use for uploading
    """

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
        )
        indicator_file = uploaded_artifact.indicator_file  # reference to storage contents
        if artifact._is_anonymous:
            artifact.name, artifact.version = uploaded_artifact.name, uploaded_artifact.version
        # Pass all of the upload information to the assets, and they will each construct the URLs that they support
        artifact._update_path(uploaded_artifact)
    return artifact, indicator_file


def _check_and_upload_env_build_context(
    environment: Environment, operations: "EnvironmentOperations", sas_uri=None
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
        )
        # TODO: Depending on decision trailing "/" needs to stay or not. EMS requires it to be present
        environment.build.path = uploaded_artifact.full_storage_path + "/"
    return environment
