# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import io
import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Union
from urllib.parse import urljoin, urlparse

import yaml
from jsonschema import Draft7Validator, ValidationError
from jsonschema.exceptions import best_match

from azure.ai.ml._artifacts._artifact_utilities import get_datastore_info, get_storage_client
from azure.ai.ml._artifacts._constants import INVALID_MLTABLE_METADATA_SCHEMA_ERROR, INVALID_MLTABLE_METADATA_SCHEMA_MSG
from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.operations._datastore_operations import DatastoreOperations

from ._http_utils import HttpPipeline
from ._storage_utils import AzureMLDatastorePathUri
from .utils import load_yaml

module_logger = logging.getLogger(__name__)


def download_mltable_metadata_schema(mltable_schema_url: str, requests_pipeline: HttpPipeline):
    response = requests_pipeline.get(mltable_schema_url)
    return response.json()


def read_local_mltable_metadata_contents(*, path: str) -> Dict:
    metadata_path = str(Path(path, "MLTable"))
    return load_yaml(metadata_path)


def read_remote_mltable_metadata_contents(
    *,
    base_uri: str,
    datastore_operations: DatastoreOperations,
    requests_pipeline: HttpPipeline,
) -> Union[Dict, None]:
    scheme = urlparse(base_uri).scheme
    if scheme == "https":
        response = requests_pipeline.get(urljoin(base_uri, "MLTable"))
        yaml_file = io.BytesIO(response.content)
        return yaml.safe_load(yaml_file)
    if scheme == "azureml":
        datastore_path_uri = AzureMLDatastorePathUri(base_uri)
        datastore_info = get_datastore_info(datastore_operations, datastore_path_uri.datastore)
        storage_client = get_storage_client(**datastore_info)
        with TemporaryDirectory() as tmp_dir:
            starts_with = datastore_path_uri.path.rstrip("/")
            storage_client.download(f"{starts_with}/MLTable", tmp_dir)
            downloaded_mltable_path = Path(tmp_dir, "MLTable")
            with open(downloaded_mltable_path, "r", encoding=DefaultOpenEncoding.READ) as f:
                return yaml.safe_load(f)
    return None


def validate_mltable_metadata(*, mltable_metadata_dict: Dict, mltable_schema: Dict):
    # use json-schema to validate dict
    error: Union[ValidationError, None] = best_match(Draft7Validator(mltable_schema).iter_errors(mltable_metadata_dict))
    if error:
        err_path = ".".join(error.path)
        err_path = f"{err_path}: " if err_path != "" else ""
        msg = INVALID_MLTABLE_METADATA_SCHEMA_ERROR.format(
            jsonSchemaErrorPath=err_path,
            jsonSchemaMessage=error.message,
            invalidMLTableMsg=INVALID_MLTABLE_METADATA_SCHEMA_MSG,
            invalidSchemaSnippet=json.dumps(error.schema, indent=2),
        )
        raise ValidationException(
            message=msg,
            no_personal_data_message=INVALID_MLTABLE_METADATA_SCHEMA_MSG,
            error_type=ValidationErrorType.INVALID_VALUE,
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
        )
