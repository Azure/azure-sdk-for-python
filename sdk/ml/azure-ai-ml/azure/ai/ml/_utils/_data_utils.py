# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import io
import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Union
from urllib.parse import urlparse

import requests
import yaml
from jsonschema import Draft7Validator, ValidationError
from jsonschema.exceptions import best_match

from azure.ai.ml._artifacts._artifact_utilities import get_datastore_info, get_storage_client
from azure.ai.ml._artifacts._constants import INVALID_MLTABLE_METADATA_SCHEMA_ERROR, INVALID_MLTABLE_METADATA_SCHEMA_MSG
from azure.ai.ml._ml_exceptions import DataException, ErrorCategory, ErrorTarget
from azure.ai.ml.operations._datastore_operations import DatastoreOperations

from ._storage_utils import AzureMLDatastorePathUri
from .utils import load_yaml

module_logger = logging.getLogger(__name__)


def download_mltable_metadata_schema(mltable_schema_url: str):
    response = requests.get(mltable_schema_url, stream=True)
    return response.json()


def read_local_mltable_metadata_contents(*, path: str) -> Dict:
    metadata_path = str(Path(path, "MLTable"))
    return load_yaml(metadata_path)


def read_remote_mltable_metadata_contents(*, path: str, datastore_operations: DatastoreOperations) -> Union[Dict, None]:
    mltable_path = str(path)
    metadata_path = str(Path(path, "MLTable"))
    scheme = urlparse(mltable_path).scheme
    if scheme == "https":
        response = requests.get(metadata_path)
        yaml_file = io.BytesIO(response.content)
        return yaml.safe_load(yaml_file)
    elif scheme == "azureml":
        datastore_path_uri = AzureMLDatastorePathUri(mltable_path)
        datastore_info = get_datastore_info(datastore_operations, datastore_path_uri.datastore)
        storage_client = get_storage_client(**datastore_info)
        with TemporaryDirectory() as tmp_dir:
            starts_with = datastore_path_uri.path.rstrip("/")
            storage_client.download(Path(starts_with, "MLTable"), tmp_dir)
            downloaded_mltable_path = Path(tmp_dir, "MLTable")
            with open(downloaded_mltable_path, "r") as f:
                return yaml.safe_load(f)
    return None


def validate_mltable_metadata(*, mltable_metadata_dict: Dict, mltable_schema: Dict):
    # use json-schema to validate dict
    error: Union[ValidationError, None] = best_match(Draft7Validator(mltable_schema).iter_errors(mltable_metadata_dict))
    if error:
        err_path = ".".join(error.path)
        err_path = f"{err_path}: " if err_path != "" else ""
        raise DataException(
            message=INVALID_MLTABLE_METADATA_SCHEMA_ERROR.format(
                jsonSchemaErrorPath=err_path,
                jsonSchemaMessage=error.message,
                invalidMLTableMsg=INVALID_MLTABLE_METADATA_SCHEMA_MSG,
                invalidSchemaSnippet=json.dumps(error.schema, indent=2),
            ),
            no_personal_data_message=INVALID_MLTABLE_METADATA_SCHEMA_MSG,
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
        )
