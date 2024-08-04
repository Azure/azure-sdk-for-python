# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple, TypeVar, Union

from typing_extensions import Literal

from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient
from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient
from azure.ai.ml._azure_environments import _get_storage_endpoint_from_metadata
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
    get_content_hash,
    get_ignore_file,
    get_object_hash,
)
from azure.ai.ml._utils._storage_utils import (
    AzureMLDatastorePathUri,
    get_artifact_path_from_storage_url,
    get_storage_client,
)
from azure.ai.ml._utils.utils import is_mlflow_uri, is_url
from azure.ai.ml.constants._common import SHORT_URI_FORMAT, STORAGE_ACCOUNT_URLS
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities._assets._artifacts.artifact import Artifact, ArtifactStorageInfo
from azure.ai.ml.entities._datastore._constants import WORKSPACE_BLOB_STORE
from azure.ai.ml.exceptions import ErrorTarget, MlException, ValidationException
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.filedatalake import FileSasPermissions, generate_file_sas

if TYPE_CHECKING:
    from azure.ai.ml.operations import (
        DataOperations,
        EnvironmentOperations,
        EvaluatorOperations,
        FeatureSetOperations,
        IndexOperations,
        ModelOperations,
    )
    from azure.ai.ml.operations._code_operations import CodeOperations

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
    return str(datastore_name)


def get_datastore_info(
    operations: DatastoreOperations,
    name: str,
    *,
    credential=None,
    **kwargs,
) -> Dict[Literal["storage_type", "storage_account", "account_url", "container_name", "credential"], str]:
    """Get datastore account, type, and auth information.

    :param operations: DatastoreOperations object
    :type operations: DatastoreOperations
    :param name: Name of the datastore. If not provided, the default datastore will be used.
    :type name: str
    :keyword credential: Local credential to use for authentication. This argument is no longer used as of 1.18.0.
        Instead, a SAS token will be requested from the datastore, and the MLClient credential will be used as backup,
        if necessary.
    :paramtype credential: str
    :return: The dictionary with datastore info
    :rtype: Dict[Literal["storage_type", "storage_account", "account_url", "container_name", "credential"], str]
    """
    datastore_info: Dict = {}
    datastore = operations.get(name) if name else operations.get_default()

    storage_endpoint = _get_storage_endpoint_from_metadata()
    datastore_info["storage_type"] = datastore.type
    datastore_info["storage_account"] = datastore.account_name
    datastore_info["account_url"] = STORAGE_ACCOUNT_URLS[datastore.type].format(
        datastore.account_name, storage_endpoint
    )

    try:
        credential = operations._list_secrets(name=name, expirable_secret=True)
        datastore_info["credential"] = credential.sas_token
    except HttpResponseError:
        datastore_info["credential"] = operations._credential

    if datastore.type == DatastoreType.AZURE_BLOB:
        datastore_info["container_name"] = str(datastore.container_name)
    elif datastore.type == DatastoreType.AZURE_DATA_LAKE_GEN2:
        datastore_info["container_name"] = str(datastore.filesystem)
    else:
        msg = (
            f"Datastore type {datastore.type} is not supported for uploads. "
            f"Supported types are {DatastoreType.AZURE_BLOB} and {DatastoreType.AZURE_DATA_LAKE_GEN2}."
        )
        raise MlException(message=msg, no_personal_data_message=msg)

    for override_param_name, value in kwargs.items():
        if override_param_name in datastore_info:
            datastore_info[override_param_name] = value

    return datastore_info


def list_logs_in_datastore(
    ds_info: Dict[Literal["storage_type", "storage_account", "account_url", "container_name", "credential"], str],
    prefix: str,
    legacy_log_folder_name: str,
) -> Dict[str, str]:
    """Returns a dictionary of file name to blob or data lake uri with SAS token, matching the structure of
    RunDetails.logFiles.

    :param ds_info: The datastore info
    :type ds_info: Dict[Literal["storage_type", "storage_account", "account_url", "container_name", "credential"], str]
    :param prefix: A prefix used to filter logs by path
    :type prefix: str
    :param legacy_log_folder_name: the name of the folder in the datastore that contains the logs
        * /azureml-logs/*.txt is the legacy log structure for commandJob and sweepJob
        * /logs/azureml/*.txt is the legacy log structure for pipeline parent Job
    :type legacy_log_folder_name: str
    :return: A mapping of log file name to the remote URI
    :rtype: Dict[str, str]
    """
    if ds_info["storage_type"] not in [
        DatastoreType.AZURE_BLOB,
        DatastoreType.AZURE_DATA_LAKE_GEN2,
    ]:
        msg = "Only Blob and Azure DataLake Storage Gen2 datastores are supported."
        raise MlException(message=msg, no_personal_data_message=msg)

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
    sas_uri: Optional[str] = None,
) -> ArtifactStorageInfo:
    """Upload local file or directory to datastore.

    :param local_path: The local file or directory to upload
    :type local_path: str
    :param datastore_operation: The datastore operation
    :type datastore_operation: DatastoreOperations
    :param operation_scope: The operation scope
    :type operation_scope: OperationScope
    :param datastore_name: The datastore name
    :type datastore_name: Optional[str]
    :param asset_hash: The asset hash
    :type asset_hash: Optional[str]
    :param show_progress: Whether to show progress on the console. Defaults to True.
    :type show_progress: bool
    :param asset_name: The asset name
    :type asset_name: Optional[str]
    :param asset_version: The asset version
    :type asset_version: Optional[str]
    :param ignore_file: The IgnoreFile determining which, if any, files to ignore when uploading
    :type ignore_file: IgnoreFile
    :param sas_uri: The sas uri to use for uploading
    :type sas_uri: Optional[str]
    :return: The artifact storage info
    :rtype: ArtifactStorageInfo
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

    :param starts_with: Prefix of blobs to download
    :type starts_with: Union[str, os.PathLike]
    :param destination: Path that files will be written to
    :type destination: str
    :param datastore_operation: Datastore operations
    :type datastore_operation: DatastoreOperations
    :param datastore_name: name of datastore
    :type datastore_name: Optional[str]
    :param datastore_info: the return value of invoking get_datastore_info
    :type datastore_info: Optional[Dict]
    :return: Path that files were written to
    :rtype: str
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
    """Download datastore blob URL to local file or directory.

    :param blob_url: The blob url to download
    :type blob_url: str
    :param destination: Path that the artifact will be written to
    :type destination: str
    :param datastore_operation: The datastore operations
    :type datastore_operation: DatastoreOperations
    :param datastore_name: The datastore name
    :type datastore_name: Optional[str]
    :return: Path that files were written to
    :rtype: str
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


def download_artifact_from_aml_uri(uri: str, destination: str, datastore_operation: DatastoreOperations) -> str:
    """Downloads artifact pointed to by URI of the form `azureml://...` to destination.

    :param str uri: AzureML uri of artifact to download
    :param str destination: Path to download artifact to
    :param DatastoreOperations datastore_operation: datastore operations
    :return: Path that files were downloaded to
    :rtype: str
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
) -> bool:
    """Checks whether `uri` of the form "azureml://" points to either a directory or a file.

    :param str uri: azure ml datastore uri
    :param DatastoreOperations datastore_operation: Datastore operation
    :param dict datastore_info: return value of get_datastore_info
    :return: True if uri exists False otherwise
    :rtype: bool
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
    sas_uri: Optional[str] = None,
    blob_uri: Optional[str] = None,
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
    if blob_uri:
        artifact.storage_account_url = blob_uri

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


T = TypeVar("T", bound=Artifact)


def _check_and_upload_path(
    artifact: T,
    asset_operations: Union[
        "DataOperations",
        "ModelOperations",
        "EvaluatorOperations",
        "CodeOperations",
        "FeatureSetOperations",
        "IndexOperations",
    ],
    artifact_type: str,
    datastore_name: Optional[str] = None,
    sas_uri: Optional[str] = None,
    show_progress: bool = True,
    blob_uri: Optional[str] = None,
) -> Tuple[T, Optional[str]]:
    """Checks whether `artifact` is a path or a uri and uploads it to the datastore if necessary.

    :param artifact: artifact to check and upload param
    :type artifact: T
    :param asset_operations: The asset operations to use for uploading
    :type asset_operations: Union["DataOperations", "ModelOperations", "CodeOperations", "IndexOperations"]
    :param artifact_type: The artifact type
    :type artifact_type: str
    :param datastore_name: the name of the datastore to upload to
    :type datastore_name: Optional[str]
    :param sas_uri: the sas uri to use for uploading
    :type sas_uri: Optional[str]
    :param show_progress: Whether to show progress on the console. Defaults to True.
    :type show_progress: bool
    :param blob_uri: The storage account uri
    :type blob_uri: Optional[str]
    :return: A 2-tuple of the uploaded artifact, and the indicator file.
    :rtype: Tuple[T, Optional[str]]
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
            asset_hash=getattr(artifact, "_upload_hash", None),
            sas_uri=sas_uri,
            artifact_type=artifact_type,
            show_progress=show_progress,
            ignore_file=getattr(artifact, "_ignore_file", None),
            blob_uri=blob_uri,
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
        if environment.build is not None:
            # TODO: Depending on decision trailing "/" needs to stay or not. EMS requires it to be present
            environment.build.path = str(uploaded_artifact.full_storage_path) + "/"
    return environment


def _get_snapshot_path_info(artifact) -> Optional[Tuple[Path, IgnoreFile, str]]:
    """
    Validate an Artifact's local path and get its resolved path, ignore file, and hash. If no local path, return None.
    :param artifact: Artifact object
    :type artifact: azure.ai.ml.entities._assets._artifacts.artifact.Artifact
    :return: Artifact's path, ignorefile, and hash
    :rtype: Tuple[os.PathLike, IgnoreFile, str]
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
    else:
        return None

    _validate_path(path, _type=ErrorTarget.CODE)

    # to align with _check_and_upload_path, we need to try getting the ignore file from the artifact first
    ignore_file = getattr(artifact, "_ignore_file", get_ignore_file(path))
    # Note that we haven't used getattr(artifact, "_upload_hash", get_content_hash(path, ignore_file)) here, which
    # is aligned with _check_and_upload_path. Current guess is that content_hash is what we used in blob, so we must
    # use it to retrieve the artifact.
    # TODO: Core SDK team to provide more information on this
    asset_hash = get_content_hash(path, ignore_file)

    return path, ignore_file, asset_hash
