# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re
from typing import Optional, Tuple, Union

from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient
from azure.ai.ml._artifacts._constants import STORAGE_URI_REGEX
from azure.ai.ml._artifacts._fileshare_storage_helper import FileStorageClient
from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient
from azure.ai.ml._azure_environments import _get_storage_endpoint_from_metadata
from azure.ai.ml._restclient.v2022_10_01.models import DatastoreType
from azure.ai.ml.constants._common import (
    FILE_PREFIX,
    FOLDER_PREFIX,
    JOB_URI_REGEX_FORMAT,
    LONG_URI_FORMAT,
    LONG_URI_REGEX_FORMAT,
    MLFLOW_URI_REGEX_FORMAT,
    OUTPUT_URI_REGEX_FORMAT,
    SHORT_URI_FORMAT,
    SHORT_URI_REGEX_FORMAT,
    STORAGE_ACCOUNT_URLS,
)
from azure.ai.ml.exceptions import ErrorTarget, MlException, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


class AzureMLDatastorePathUri:
    """Parser for an azureml:// datastore path URI, e.g.: azureml://datastores/mydatastore/paths/images/dogs'.

    :param uri: The AzureML datastore path URI.
    :type uri: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the AzureML datastore
        path URI is incorrectly formatted.
    '
    """

    def __init__(self, uri: str):
        if uri.startswith(FILE_PREFIX):
            uri = uri[len(FILE_PREFIX) :]
        elif uri.startswith(FOLDER_PREFIX):
            uri = uri[len(FOLDER_PREFIX) :]
        self.uri = uri

        short_uri_match = re.match(SHORT_URI_REGEX_FORMAT, uri)
        ml_flow_uri_match = re.match(MLFLOW_URI_REGEX_FORMAT, uri)
        job_uri_match = re.match(JOB_URI_REGEX_FORMAT, uri)
        long_uri_match = re.match(LONG_URI_REGEX_FORMAT, uri)
        output_uri_match = re.match(OUTPUT_URI_REGEX_FORMAT, uri)

        if short_uri_match:
            self.datastore = short_uri_match.group(1)
            self.path = short_uri_match.group(2)
            self.uri_type = "Datastore"
            self.workspace_name = None
            self.resource_group = None
            self.subscription_id = None
        elif ml_flow_uri_match:
            self.datastore = ml_flow_uri_match.group(1)
            self.path = ml_flow_uri_match.group(2)
            self.uri_type = "MlFlow"
            self.workspace_name = None
            self.resource_group = None
            self.subscription_id = None
        elif job_uri_match:
            self.datastore = job_uri_match.group(1)
            self.path = job_uri_match.group(2)
            self.uri_type = "Job"
            self.workspace_name = None
            self.resource_group = None
            self.subscription_id = None
        elif output_uri_match:
            self.datastore = output_uri_match.group(1)
            self.path = output_uri_match.group(2)
            self.uri_type = None
            self.workspace_name = None
            self.resource_group = None
            self.subscription_id = None
        elif long_uri_match:
            self.datastore = long_uri_match.group(4)
            self.path = long_uri_match.group(5)
            self.uri_type = "Datastore"
            self.workspace_name = long_uri_match.group(3)
            self.resource_group = long_uri_match.group(2)
            self.subscription_id = long_uri_match.group(1)
        else:
            msg = "Invalid AzureML datastore path URI {}"
            raise ValidationException(
                message=msg.format(uri),
                no_personal_data_message=msg.format("[uri]"),
                target=ErrorTarget.DATASTORE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def to_short_uri(self) -> str:
        return SHORT_URI_FORMAT.format(self.datastore, self.path)

    def to_long_uri(self, subscription_id: str, resource_group_name: str, workspace_name: str) -> str:
        return LONG_URI_FORMAT.format(
            subscription_id,
            resource_group_name,
            workspace_name,
            self.datastore,
            self.path,
        )

    def get_uri_type(self) -> str:
        if self.uri[0:20] == "azureml://datastores":
            return "Datastore"
        if self.uri[0:14] == "azureml://jobs":
            return "Jobs"

        if self.uri[0 : self.uri.find(":")] == "runs":
            return "MLFlow"
        msg = "Invalid uri format for {}. URI must start with 'azureml://' or 'runs:/'"
        raise ValidationException(
            message=msg.format(self.uri),
            no_personal_data_message=msg.format("[self.uri]"),
            target=ErrorTarget.DATASTORE,
            error_type=ValidationErrorType.INVALID_VALUE,
        )


def get_storage_client(
    credential: str,
    storage_account: str,
    storage_type: Union[DatastoreType, str] = DatastoreType.AZURE_BLOB,
    account_url: Optional[str] = None,
    container_name: Optional[str] = None,
) -> Union[BlobStorageClient, FileStorageClient, Gen2StorageClient]:
    """Return a storage client class instance based on the storage account type.

    :param credential: The credential
    :type credential: str
    :param storage_account: The storage_account name
    :type storage_account: str
    :param storage_type: The storage type
    :type storage_type: Union[DatastoreType, str]
    :param account_url: The account url
    :type account_url: Optional[str]
    :param container_name: The container name
    :type container_name: Optional[str]
    :return: The storage client
    :rtype: Union[BlobStorageClient, FileStorageClient, Gen2StorageClient]
    """
    client_builders = {
        DatastoreType.AZURE_BLOB: lambda credential, container_name, account_url: BlobStorageClient(
            credential=credential, account_url=account_url, container_name=container_name
        ),
        DatastoreType.AZURE_DATA_LAKE_GEN2: lambda credential, container_name, account_url: Gen2StorageClient(
            credential=credential, file_system=container_name, account_url=account_url
        ),
        DatastoreType.AZURE_FILE: lambda credential, container_name, account_url: FileStorageClient(
            credential=credential, file_share_name=container_name, account_url=account_url
        ),
    }

    if storage_type not in client_builders:
        msg = (
            f"Datastore type {storage_type} is not supported. Supported storage"
            + f"types for artifact upload include: {*client_builders,}"
        )
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.DATASTORE,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    storage_endpoint = _get_storage_endpoint_from_metadata()
    if not account_url and storage_endpoint:
        account_url = STORAGE_ACCOUNT_URLS[storage_type].format(storage_account, storage_endpoint)
    return client_builders[storage_type](credential, container_name, account_url)


def get_artifact_path_from_storage_url(blob_url: str, container_name: dict) -> str:
    split_blob_url = blob_url.split(container_name)
    if len(split_blob_url) > 1:
        path = split_blob_url[-1]
        if path.startswith("/"):
            return path[1:]
        return path
    return blob_url


def get_ds_name_and_path_prefix(asset_uri: str, registry_name: Optional[str] = None) -> Tuple[str, str]:
    if registry_name:
        try:
            split_paths = re.findall(STORAGE_URI_REGEX, asset_uri)
            if split_paths[0][3] == "":
                path_prefix = split_paths[0][2]
            else:
                path_prefix = split_paths[0][3]
        except Exception as e:
            msg = "Registry asset URI could not be parsed."
            raise MlException(message=msg, no_personal_data_message=msg) from e
        ds_name = None
    else:
        try:
            ds_name = asset_uri.split("paths")[0].split("/")[-2]
            path_prefix = asset_uri.split("paths")[1][1:]
        except Exception as e:
            msg = "Workspace asset URI could not be parsed."
            raise MlException(message=msg, no_personal_data_message=msg) from e

    return ds_name, path_prefix
