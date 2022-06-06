# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import io
import logging
import yaml
import requests
import json
from azure.ai.ml.entities._data.mltable_metadata import MLTableMetadata
from azure.ai.ml._schema._data.mltable_metadata_schema import MLTableMetadataSchema
from azure.ai.ml._operations import DatastoreOperations
from azure.ai.ml._artifacts._artifact_utilities import get_datastore_info, get_storage_client
from azure.ai.ml.entities._util import decorate_validation_error
from azure.ai.ml.constants import SKIP_VALIDATION_MESSAGE
from tempfile import TemporaryDirectory
from os import PathLike
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Union
from .utils import is_url, load_yaml
from ._storage_utils import AzureMLDatastorePathUri
from jsonschema import Draft7Validator, ValidationError
from jsonschema.exceptions import best_match
from knack.cli import CLIError

module_logger = logging.getLogger(__name__)


def read_mltable_metadata_contents(
    *, datastore_operations: DatastoreOperations, path: Union[str, PathLike], debug: bool = False
) -> Union[Dict, None]:
    mltable_path = str(path)
    metadata_path = str(Path(path, "MLTable"))
    if is_url(mltable_path):
        try:
            scheme = urlparse(mltable_path).scheme
            if scheme == "https":
                response = requests.get(metadata_path)
                yaml_file = io.BytesIO(response.content)
                return yaml.safe_load(yaml_file)
            if scheme == "azureml":
                datastore_path_uri = AzureMLDatastorePathUri(mltable_path)
                datastore_info = get_datastore_info(datastore_operations, datastore_path_uri.datastore)
                storage_client = get_storage_client(**datastore_info)
                with TemporaryDirectory() as tmp_dir:
                    starts_with = datastore_path_uri.path.rstrip("/")
                    storage_client.download(Path(starts_with, "MLTable"), tmp_dir)
                    downloaded_mltable_path = Path(tmp_dir, "MLTable")
                    with open(downloaded_mltable_path, "r") as f:
                        return yaml.safe_load(f)
        except Exception:
            if debug:
                module_logger.info("Failed to read MLTable metadata from remote path %s", mltable_path, exc_info=1)
    else:
        return load_yaml(metadata_path)
    return None


def download_schema(mltable_schema_url: str, *, debug: bool = False) -> Union[Dict, None]:
    try:
        response = requests.get(mltable_schema_url, stream=True)
        return response.json()
    except Exception:
        if debug:
            module_logger.info(
                'Failed to download MLTable jsonschema from "%s", skipping validation', mltable_schema_url, exc_info=1
            )
        return None


def validate_mltable_metadata_schema(
    mltable_metadata_dict: Dict, *, mltable_schema_url: str, path: Union[str, PathLike], debug: bool = False
) -> Union[MLTableMetadata, None]:
    # first load content into class for bare minimum marshmallow schema validation (mltable_metdata_schema)
    metadata = MLTableMetadata._load(mltable_metadata_dict, path)
    schema = download_schema(mltable_schema_url, debug=debug)
    if schema:
        # use json-schema to validate dict
        error: Union[ValidationError, None] = best_match(Draft7Validator(schema).iter_errors(mltable_metadata_dict))
        if error:
            raise CLIError(
                decorate_validation_error(
                    MLTableMetadataSchema,
                    '"{}": {}\nSchema:\n{}'.format(
                        ".".join(error.path), error.message, json.dumps(error.schema, indent=2)
                    ),
                    SKIP_VALIDATION_MESSAGE,
                )
            )
    return metadata


def extract_referenced_uris(mltable_metadata_dict: Dict, *, debug: bool = False) -> List[str]:
    try:
        referenced_uris = []
        for path in mltable_metadata_dict["paths"]:
            folder = path.get("folder", None)
            file = path.get("file", None)
            if isinstance(folder, str):
                referenced_uris.append(folder)
            elif isinstance(file, str):
                referenced_uris.append(file)
        return referenced_uris
    except Exception:
        if debug:
            module_logger.info("Failed to extract MLTable referenced uris", exc_info=1)
    return []
