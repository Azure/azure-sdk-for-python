# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re
from typing import Tuple, Union

from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient
from azure.ai.ml._artifacts._fileshare_storage_helper import FileStorageClient
from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient
from azure.ai.ml._azure_environments import _get_storage_endpoint_from_metadata
from azure.ai.ml._ml_exceptions import ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2021_10_01.models import DatastoreType
from azure.ai.ml.constants import (
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

module_logger = logging.getLogger(__name__)

SUPPORTED_STORAGE_TYPES = [
    DatastoreType.AZURE_BLOB,
    DatastoreType.AZURE_DATA_LAKE_GEN2,
    DatastoreType.AZURE_FILE,
]


class AzureMLDatastorePathUri:
    """Parser for an azureml:// datastore path URI, e.g.:
    azureml://datastores/mydatastore/paths/images/dogs."""

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
        else:
            msg = "Invalid uri format for {}. URI must start with 'azureml://' or 'runs:/'"
            raise ValidationException(
                message=msg.format(self.uri),
                no_personal_data_message=msg.format("[self.uri]"),
                target=ErrorTarget.DATASTORE,
            )


def get_storage_client(
    credential: str,
    storage_account: str,
    storage_type: Union[DatastoreType, str] = DatastoreType.AZURE_BLOB,
    account_url: str = None,
    container_name: str = None,
) -> Union[BlobStorageClient, FileStorageClient, Gen2StorageClient]:
    """Return a storage client class instance based on the storage account
    type."""
    if storage_type not in SUPPORTED_STORAGE_TYPES:
        msg = f"Datastore type {storage_type} is not supported. Supported storage"
        f"types for artifact upload include: {*SUPPORTED_STORAGE_TYPES,}"
        raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.DATASTORE)

    storage_endpoint = _get_storage_endpoint_from_metadata()
    if not account_url and storage_endpoint:
        account_url = STORAGE_ACCOUNT_URLS[storage_type].format(storage_account, storage_endpoint)

    if storage_type == DatastoreType.AZURE_BLOB:
        return BlobStorageClient(
            credential=credential,
            container_name=container_name,
            account_url=account_url,
        )
    elif storage_type == DatastoreType.AZURE_DATA_LAKE_GEN2:
        return Gen2StorageClient(credential=credential, file_system=container_name, account_url=account_url)
    elif storage_type == DatastoreType.AZURE_FILE:
        return FileStorageClient(
            credential=credential,
            file_share_name=container_name,
            account_url=account_url,
        )


def get_artifact_path_from_storage_url(blob_url: str, container_name: dict) -> str:
    split_blob_url = blob_url.split(container_name)
    if len(split_blob_url) > 1:
        path = split_blob_url[-1]
        if path.startswith("/"):
            return path[1:]
        return path
    return blob_url


def get_ds_name_and_path_prefix(asset_uri: str) -> Tuple[str, str]:
    ds_name = asset_uri.split("paths")[0].split("/")[-2]
    path_prefix = asset_uri.split("paths")[1][1:]
    return ds_name, path_prefix
