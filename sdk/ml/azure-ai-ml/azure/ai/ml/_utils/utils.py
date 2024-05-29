# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,too-many-lines
import copy
import decimal
import hashlib
import json
import logging
import os
import random
import re
import string
import sys
import tempfile
import time
import warnings
from collections import OrderedDict
from contextlib import contextmanager, nullcontext
from datetime import timedelta
from functools import singledispatch, wraps
from os import PathLike
from pathlib import Path, PureWindowsPath
from typing import IO, Any, AnyStr, Callable, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse
from uuid import UUID

import isodate
import pydash
import yaml

from azure.ai.ml._restclient.v2022_05_01.models import ListViewType, ManagedServiceIdentity
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml.constants._common import (
    AZUREML_DISABLE_CONCURRENT_COMPONENT_REGISTRATION,
    AZUREML_DISABLE_ON_DISK_CACHE_ENV_VAR,
    AZUREML_INTERNAL_COMPONENTS_ENV_VAR,
    AZUREML_INTERNAL_COMPONENTS_SCHEMA_PREFIX,
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
    CommonYamlFields,
    DefaultOpenEncoding,
    WorkspaceDiscoveryUrlKey,
)
from azure.ai.ml.exceptions import MlException
from azure.core.pipeline.policies import RetryPolicy

module_logger = logging.getLogger(__name__)

DEVELOPER_URL_MFE_ENV_VAR = "AZUREML_DEV_URL_MFE"

# Prefix used when hitting MFE skipping ARM
MFE_PATH_PREFIX = "/mferp/managementfrontend"


def _get_mfe_url_override() -> Optional[str]:
    return os.getenv(DEVELOPER_URL_MFE_ENV_VAR)


def _is_https_url(url: str) -> Union[bool, str]:
    if url:
        return url.lower().startswith("https")
    return False


def _csv_parser(text: Optional[str], convert: Callable) -> Optional[str]:
    if not text:
        return None
    if "," in text:
        return ",".join(convert(t.strip()) for t in text.split(","))

    return convert(text)


def _snake_to_pascal_convert(text: str) -> str:
    return string.capwords(text.replace("_", " ")).replace(" ", "")


def snake_to_pascal(text: Optional[str]) -> str:
    """Convert snake name to pascal.

    :param text: String to convert
    :type text: Optional[str]
    :return:
        * None if text is None
        * Converted text from snake_case to PascalCase
    :rtype: Optional[str]
    """
    return _csv_parser(text, _snake_to_pascal_convert)


def snake_to_kebab(text: Optional[str]) -> Optional[str]:
    """Convert snake name to kebab.

    :param text: String to convert
    :type text: Optional[str]
    :return:
        * None if text is None
        * Converted text from snake_case to kebab-case
    :rtype: Optional[str]
    """
    if text:
        return re.sub("_", "-", text)
    return None


# https://stackoverflow.com/questions/1175208
# This works for pascal to snake as well
def _camel_to_snake_convert(text: str) -> str:
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", text).lower()


def camel_to_snake(text: str) -> Optional[str]:
    """Convert camel name to snake.

     :param text: String to convert
     :type text: str
     :return:
        * None if text is None
        * Converted text from camelCase to snake_case
    :rtype: Optional[str]
    """
    return _csv_parser(text, _camel_to_snake_convert)


# This is snake to camel back which is different from snake to camel
# https://stackoverflow.com/questions/19053707
def snake_to_camel(text: Optional[str]) -> Optional[str]:
    """Convert snake name to camel.

    :param text: String to convert
    :type text: Optional[str]
    :return:
       * None if text is None
       * Converted text from snake_case to camelCase
    :rtype: Optional[str]
    """
    if text:
        return re.sub("_([a-zA-Z0-9])", lambda m: m.group(1).upper(), text)
    return None


# This is real snake to camel
def _snake_to_camel(name):
    return re.sub(r"(?:^|_)([a-z])", lambda x: x.group(1).upper(), name)


def float_to_str(f):
    """Convert a float to a string without scientific notation.

    :param f: Float to convert
    :type f: float
    :return: String representation of the float
    :rtype: str
    """
    with decimal.localcontext() as ctx:
        ctx.prec = 20  # Support up to 20 significant figures.
        float_as_dec = ctx.create_decimal(repr(f))
        return format(float_as_dec, "f")


def create_requests_pipeline_with_retry(*, requests_pipeline: HttpPipeline, retries: int = 3) -> HttpPipeline:
    """Creates an HttpPipeline that reuses the same configuration as the supplied pipeline (including the transport),
    but overwrites the retry policy.

    :keyword requests_pipeline: Pipeline to base new one off of.
    :paramtype requests_pipeline: HttpPipeline
    :keyword retries: Number of retries. Defaults to 3.
    :paramtype retries: int
    :return: Pipeline identical to provided one, except with a new retry policy
    :rtype: HttpPipeline
    """
    return requests_pipeline.with_policies(retry_policy=get_retry_policy(num_retry=retries))


def get_retry_policy(num_retry: int = 3) -> RetryPolicy:
    """Retrieves a retry policy to use in an azure.core.pipeline.Pipeline

    :param num_retry: The number of retries
    :type num_retry: int
    :return: Returns the msrest or requests REST client retry policy.
    :rtype: RetryPolicy
    """
    status_forcelist = [413, 429, 500, 502, 503, 504]
    backoff_factor = 0.4
    return RetryPolicy(
        retry_total=num_retry,
        retry_read=num_retry,
        retry_connect=num_retry,
        retry_backoff_factor=backoff_factor,
        retry_on_status_codes=status_forcelist,
    )


def download_text_from_url(
    source_uri: str,
    requests_pipeline: HttpPipeline,
    timeout: Optional[Union[float, Tuple[float, float]]] = None,
) -> str:
    """Downloads the content from an URL.

    :param source_uri: URI to download
    :type source_uri: str
    :param requests_pipeline:  Used to send the request
    :type requests_pipeline: HttpPipeline
    :param timeout: One of
      * float that specifies the connect and read time outs
      * a 2-tuple that specifies the connect and read time out in that order
    :type timeout: Union[float, Tuple[float, float]]
    :return: The Response text
    :rtype: str
    """
    if not timeout:
        timeout_params = {}
    else:
        connect_timeout, read_timeout = timeout if isinstance(timeout, tuple) else (timeout, timeout)
        timeout_params = {"read_timeout": read_timeout, "connection_timeout": connect_timeout}

    response = requests_pipeline.get(source_uri, **timeout_params)
    # Match old behavior from execution service's status API.
    if response.status_code == 404:
        return ""

    # _raise_request_error(response, "Retrieving content from " + uri)
    return response.text()


def load_file(file_path: str) -> str:
    """Load a local file.

    :param file_path: The relative or absolute path to the local file.
    :type file_path: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if file or folder cannot be found.
    :return: A string representation of the local file's contents.
    :rtype: str
    """
    from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override

    try:
        with open(file_path, "r", encoding=DefaultOpenEncoding.READ) as f:
            cfg = f.read()
    except OSError as e:  # FileNotFoundError introduced in Python 3
        msg = "No such file or directory: {}"
        raise ValidationException(
            message=msg.format(file_path),
            no_personal_data_message=msg.format("[file_path]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        ) from e
    return cfg


def load_json(file_path: Optional[Union[str, os.PathLike]]) -> Dict:
    """Load a local json file.

    :param file_path: The relative or absolute path to the local file.
    :type file_path: Union[str, os.PathLike]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if file or folder cannot be found.
    :return: A dictionary representation of the local file's contents.
    :rtype: Dict
    """
    from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override

    try:
        with open(file_path, "r", encoding=DefaultOpenEncoding.READ) as f:
            cfg = json.load(f)
    except OSError as e:  # FileNotFoundError introduced in Python 3
        msg = "No such file or directory: {}"
        raise ValidationException(
            message=msg.format(file_path),
            no_personal_data_message=msg.format("[file_path]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        ) from e
    return cfg


def load_yaml(source: Optional[Union[AnyStr, PathLike, IO]]) -> Dict:
    # null check - just return an empty dict.
    # Certain CLI commands rely on this behavior to produce a resource
    # via CLI, which is then populated through CLArgs.
    """Load a local YAML file.

    :param source: Either
       * The relative or absolute path to the local file.
       * A readable File-like object
    :type source: Optional[Union[AnyStr, PathLike, IO]]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if file or folder cannot be successfully loaded.
        Details will be provided in the error message.
    :return: A dictionary representation of the local file's contents.
    :rtype: Dict
    """
    from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override

    if source is None:
        return {}

    if isinstance(source, (str, os.PathLike)):
        try:
            cm = open(source, "r", encoding=DefaultOpenEncoding.READ)
        except OSError as e:
            msg = "No such file or directory: {}"
            raise ValidationException(
                message=msg.format(source),
                no_personal_data_message=msg.format("[file_path]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
            ) from e
    else:
        # source is a subclass of IO
        if not source.readable():
            msg = "File Permissions Error: The already-open \n\n inputted file is not readable."
            raise ValidationException(
                message=msg,
                no_personal_data_message="File Permissions error",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        cm = nullcontext(enter_result=source)

    with cm as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            msg = f"Error while parsing yaml file: {source} \n\n {str(e)}"
            raise ValidationException(
                message=msg,
                no_personal_data_message="Error while parsing yaml file",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.CANNOT_PARSE,
            ) from e


# pylint: disable-next=docstring-missing-param
def dump_yaml(*args, **kwargs):
    """A thin wrapper over yaml.dump which forces `OrderedDict`s to be serialized as mappings.

    Otherwise behaves identically to yaml.dump

    :return: The yaml object
    :rtype: Any
    """

    class OrderedDumper(yaml.Dumper):
        """A modified yaml serializer that forces pyyaml to represent an OrderedDict as a mapping instead of a
        sequence."""

    OrderedDumper.add_representer(OrderedDict, yaml.representer.SafeRepresenter.represent_dict)
    return yaml.dump(*args, Dumper=OrderedDumper, **kwargs)


def dump_yaml_to_file(
    dest: Optional[Union[AnyStr, PathLike, IO]],
    data_dict: Union[OrderedDict, Dict],
    default_flow_style=False,
    args=None,  # pylint: disable=unused-argument
    **kwargs,
) -> None:
    """Dump dictionary to a local YAML file.

    :param dest: The relative or absolute path where the YAML dictionary will be dumped.
    :type dest: Optional[Union[AnyStr, PathLike, IO]]
    :param data_dict: Dictionary representing a YAML object
    :type data_dict: Union[OrderedDict, Dict]
    :param default_flow_style: Use flow style for formatting nested YAML collections
        instead of block style. Defaults to False.
    :type default_flow_style: bool
    :param path: Deprecated. Use 'dest' param instead.
    :type path: Optional[Union[AnyStr, PathLike]]
    :param args: Deprecated.
    :type: Any
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if object cannot be successfully dumped.
        Details will be provided in the error message.
    """
    from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override
    # Check for deprecated path input, either named or as first unnamed input
    path = kwargs.pop("path", None)
    if dest is None:
        if path is not None:
            dest = path
            warnings.warn(
                "the 'path' input for dump functions is deprecated. Please use 'dest' instead.", DeprecationWarning
            )
        else:
            msg = "No dump destination provided."
            raise ValidationException(
                message=msg,
                no_personal_data_message="No dump destination Provided",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

    if isinstance(dest, (str, os.PathLike)):
        try:
            cm = open(dest, "w", encoding=DefaultOpenEncoding.WRITE)
        except OSError as e:  # FileNotFoundError introduced in Python 3
            msg = "No such parent folder path or not a file path: {}"
            raise ValidationException(
                message=msg.format(dest),
                no_personal_data_message=msg.format("[file_path]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
            ) from e
    else:
        # dest is a subclass of IO
        if not dest.writable():  # dest is misformatted stream or file
            msg = "File Permissions Error: The already-open \n\n inputted file is not writable."
            raise ValidationException(
                message=msg,
                no_personal_data_message="File Permissions error",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.CANNOT_PARSE,
            )
        cm = nullcontext(enter_result=dest)

    with cm as f:
        try:
            dump_yaml(data_dict, f, default_flow_style=default_flow_style)
        except yaml.YAMLError as e:
            msg = f"Error while parsing yaml file \n\n {str(e)}"
            raise ValidationException(
                message=msg,
                no_personal_data_message="Error while parsing yaml file",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.CANNOT_PARSE,
            ) from e


def dict_eq(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> bool:
    """Compare two dictionaries.

    :param dict1: The first dictionary
    :type dict1: Dict[str, Any]
    :param dict2: The second dictionary
    :type dict2: Dict[str, Any]
    :return: True if the two dictionaries are equal, False otherwise
    :rtype: bool
    """
    if not dict1 and not dict2:
        return True
    return dict1 == dict2


def xor(a: Any, b: Any) -> bool:
    """XOR two values.

    :param a: The first value
    :type a: Any
    :param b: The second value
    :type b: Any
    :return: False if the two values are both True or both False, True otherwise
    :rtype: bool
    """
    return bool(a) != bool(b)


def is_url(value: Union[PathLike, str]) -> bool:
    """Check if a string is a valid URL.

    :param value: The string to check
    :type value: Union[PathLike, str]
    :return: True if the string is a valid URL, False otherwise
    :rtype: bool
    """
    try:
        result = urlparse(str(value))
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


# Resolve an URL to long form if it is an azureml short from datastore URL, otherwise return the same value
def resolve_short_datastore_url(value: Union[PathLike, str], workspace: OperationScope) -> str:
    """Resolve an URL to long form if it is an azureml short from datastore URL, otherwise return the same value.

    :param value: The URL to resolve
    :type value: Union[PathLike, str]
    :param workspace: The workspace
    :type workspace: OperationScope
    :return: The resolved URL
    :rtype: str
    """
    from azure.ai.ml.exceptions import ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override

    try:
        # Check if the URL is an azureml URL
        if urlparse(str(value)).scheme == "azureml":
            from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri

            data_store_path_uri = AzureMLDatastorePathUri(value)
            if data_store_path_uri.uri_type == "Datastore":
                return AzureMLDatastorePathUri(value).to_long_uri(
                    subscription_id=workspace.subscription_id,
                    resource_group_name=workspace.resource_group_name,
                    workspace_name=workspace.workspace_name,
                )

    except (ValueError, ValidationException):
        pass

    # If the URL is not an valid URL (e.g. a local path) or not an azureml URL
    # (e.g. a http URL), just return the same value
    return value


def is_mlflow_uri(value: Union[PathLike, str]) -> bool:
    """Check if a string is a valid mlflow uri.

    :param value: The string to check
    :type value: Union[PathLike, str]
    :return: True if the string is a valid mlflow uri, False otherwise
    :rtype: bool
    """
    try:
        return urlparse(str(value)).scheme == "runs"
    except ValueError:
        return False


def validate_ml_flow_folder(path: str, model_type: string) -> None:
    """Validate that the path is a valid ml flow folder.

    :param path: The path to validate
    :type path: str
    :param model_type: The model type
    :type model_type: str
    :return: No return value
    :rtype: None
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the path is not a valid ml flow folder.
    """
    from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override

    if not isinstance(path, str):
        path = path.as_posix()
    path_array = path.split("/")
    if model_type != "mlflow_model" or "." not in path_array[-1]:
        return
    msg = "Error with path {}. Model of type mlflow_model cannot register a file."
    raise ValidationException(
        message=msg.format(path),
        no_personal_data_message=msg.format("[path]"),
        target=ErrorTarget.MODEL,
        error_type=ValidationErrorType.INVALID_VALUE,
    )


# modified from: https://stackoverflow.com/a/33245493/8093897
def is_valid_uuid(test_uuid: str) -> bool:
    """Check if a string is a valid UUID.

    :param test_uuid: The string to check
    :type test_uuid: str
    :return: True if the string is a valid UUID, False otherwise
    :rtype: bool
    """
    try:
        uuid_obj = UUID(test_uuid, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == test_uuid


@singledispatch
def from_iso_duration_format(duration: Optional[Any] = None) -> int:  # pylint: disable=unused-argument
    """Convert ISO duration format to seconds.

    :param duration: The duration to convert
    :type duration: Optional[Any]
    :return: The converted duration
    :rtype: int
    """
    return None


@from_iso_duration_format.register(str)
def _(duration: str) -> int:
    return int(isodate.parse_duration(duration).total_seconds())


@from_iso_duration_format.register(timedelta)
def _(duration: timedelta) -> int:
    return int(duration.total_seconds())


def to_iso_duration_format_mins(time_in_mins: Optional[Union[int, float]]) -> str:
    """Convert minutes to ISO duration format.

    :param time_in_mins: The time in minutes to convert
    :type time_in_mins: Optional[Union[int, float]]
    :return: The converted time in ISO duration format
    :rtype: str
    """
    return isodate.duration_isoformat(timedelta(minutes=time_in_mins)) if time_in_mins else None


def from_iso_duration_format_mins(duration: Optional[str]) -> int:
    """Convert ISO duration format to minutes.

    :param duration: The duration to convert
    :type duration: Optional[str]
    :return: The converted duration
    :rtype: int
    """
    return int(from_iso_duration_format(duration) / 60) if duration else None


def to_iso_duration_format(time_in_seconds: Optional[Union[int, float]]) -> str:
    """Convert seconds to ISO duration format.

    :param time_in_seconds: The time in seconds to convert
    :type time_in_seconds: Optional[Union[int, float]]
    :return: The converted time in ISO duration format
    :rtype: str
    """
    return isodate.duration_isoformat(timedelta(seconds=time_in_seconds)) if time_in_seconds else None


def to_iso_duration_format_ms(time_in_ms: Optional[Union[int, float]]) -> str:
    """Convert milliseconds to ISO duration format.

    :param time_in_ms: The time in milliseconds to convert
    :type time_in_ms: Optional[Union[int, float]]
    :return: The converted time in ISO duration format
    :rtype: str
    """
    return isodate.duration_isoformat(timedelta(milliseconds=time_in_ms)) if time_in_ms else None


def from_iso_duration_format_ms(duration: Optional[str]) -> int:
    """Convert ISO duration format to milliseconds.

    :param duration: The duration to convert
    :type duration: Optional[str]
    :return: The converted duration
    :rtype: int
    """
    return from_iso_duration_format(duration) * 1000 if duration else None


def to_iso_duration_format_days(time_in_days: Optional[int]) -> str:
    """Convert days to ISO duration format.

    :param time_in_days: The time in days to convert
    :type time_in_days: Optional[int]
    :return: The converted time in ISO duration format
    :rtype: str
    """
    return isodate.duration_isoformat(timedelta(days=time_in_days)) if time_in_days else None


@singledispatch
def from_iso_duration_format_days(duration: Optional[Any] = None) -> int:  # pylint: disable=unused-argument
    return None


@from_iso_duration_format_days.register(str)
def _(duration: str) -> int:
    return int(isodate.parse_duration(duration).days)


@from_iso_duration_format_days.register(timedelta)
def _(duration: timedelta) -> int:
    return int(duration.days)


def _get_base_urls_from_discovery_service(
    workspace_operations: "WorkspaceOperations", workspace_name: str, requests_pipeline: HttpPipeline
) -> Dict[WorkspaceDiscoveryUrlKey, str]:
    """Fetch base urls for a workspace from the discovery service.

    :param WorkspaceOperations workspace_operations:
    :param str workspace_name: The name of the workspace
    :param HttpPipeline requests_pipeline: An HTTP pipeline to make requests with
    :returns: A dictionary mapping url types to base urls
    :rtype: Dict[WorkspaceDiscoveryUrlKey,str]
    """
    discovery_url = workspace_operations.get(workspace_name).discovery_url

    return json.loads(
        download_text_from_url(
            discovery_url,
            create_requests_pipeline_with_retry(requests_pipeline=requests_pipeline),
        )
    )


def _get_mfe_base_url_from_discovery_service(
    workspace_operations: Any, workspace_name: str, requests_pipeline: HttpPipeline
) -> str:
    all_urls = _get_base_urls_from_discovery_service(workspace_operations, workspace_name, requests_pipeline)
    return f"{all_urls[WorkspaceDiscoveryUrlKey.API]}{MFE_PATH_PREFIX}"


def _get_mfe_base_url_from_registry_discovery_service(
    workspace_operations: Any, workspace_name: str, requests_pipeline: HttpPipeline
) -> str:
    all_urls = _get_base_urls_from_discovery_service(workspace_operations, workspace_name, requests_pipeline)
    return all_urls[WorkspaceDiscoveryUrlKey.API]


def _get_workspace_base_url(workspace_operations: Any, workspace_name: str, requests_pipeline: HttpPipeline) -> str:
    all_urls = _get_base_urls_from_discovery_service(workspace_operations, workspace_name, requests_pipeline)
    return all_urls[WorkspaceDiscoveryUrlKey.API]


def _get_mfe_base_url_from_batch_endpoint(endpoint: "BatchEndpoint") -> str:
    return endpoint.scoring_uri.split("/subscriptions/")[0]


# Allows to use a modified client with a provided url
@contextmanager
def modified_operation_client(operation_to_modify, url_to_use):
    """Modify the operation client to use a different url.

    :param operation_to_modify: The operation to modify
    :type operation_to_modify: Any
    :param url_to_use: The url to use
    :type url_to_use: str
    :return: The modified operation
    :rtype: Any
    """
    original_api_base_url = None
    try:
        # Modify the operation
        if url_to_use:
            original_api_base_url = operation_to_modify._client._base_url
            operation_to_modify._client._base_url = url_to_use
        yield
    finally:
        # Undo the modification
        if original_api_base_url:
            operation_to_modify._client._base_url = original_api_base_url


def from_iso_duration_format_min_sec(duration: Optional[str]) -> str:
    """Convert ISO duration format to min:sec format.

    :param duration: The duration to convert
    :type duration: Optional[str]
    :return: The converted duration
    :rtype: str
    """
    return duration.split(".")[0].replace("PT", "").replace("M", "m ") + "s"


def hash_dict(items: Dict[str, Any], keys_to_omit: Optional[Iterable[str]] = None) -> str:
    """Return hash GUID of a dictionary except keys_to_omit.

    :param items: The dict to hash
    :type items: Dict[str, Any]
    :param keys_to_omit: Keys to omit before hashing
    :type keys_to_omit: Optional[Iterable[str]]
    :return: The hash GUID of the dictionary
    :rtype: str
    """
    if keys_to_omit is None:
        keys_to_omit = []
    items = pydash.omit(items, keys_to_omit)
    # serialize dict with order so same dict will have same content
    serialized_component_interface = json.dumps(items, sort_keys=True)
    object_hash = hashlib.md5()  # nosec
    object_hash.update(serialized_component_interface.encode("utf-8"))
    return str(UUID(object_hash.hexdigest()))


def convert_identity_dict(
    identity: Optional[ManagedServiceIdentity] = None,
) -> ManagedServiceIdentity:
    """Convert identity to the right format.

    :param identity: The identity to convert
    :type identity: Optional[ManagedServiceIdentity]
    :return: The converted identity
    :rtype: ManagedServiceIdentity
    """
    if identity:
        if identity.type.lower() in ("system_assigned", "none"):
            identity = ManagedServiceIdentity(type="SystemAssigned")
        else:
            if identity.user_assigned_identities:
                if isinstance(identity.user_assigned_identities, dict):  # if the identity is already in right format
                    return identity
                ids = {}
                for id in identity.user_assigned_identities:  # pylint: disable=redefined-builtin
                    ids[id["resource_id"]] = {}
                identity.user_assigned_identities = ids
                identity.type = snake_to_camel(identity.type)
    else:
        identity = ManagedServiceIdentity(type="SystemAssigned")
    return identity


def strip_double_curly(io_binding_val: str) -> str:
    """Strip double curly brackets from a string.

    :param io_binding_val: The string to strip
    :type io_binding_val: str
    :return: The string with double curly brackets stripped
    :rtype: str
    """
    return io_binding_val.replace("${{", "").replace("}}", "")


def append_double_curly(io_binding_val: str) -> str:
    """Append double curly brackets to a string.

    :param io_binding_val: The string to append to
    :type io_binding_val: str
    :return: The string with double curly brackets appended
    :rtype: str
    """
    return f"${{{{{io_binding_val}}}}}"


def map_single_brackets_and_warn(command: str) -> str:
    """Map single brackets to double brackets and warn if found.

    :param command: The command to map
    :type command: str
    :return: The mapped command
    :rtype: str
    """

    def _check_for_parameter(param_prefix: str, command_string: str) -> Tuple[bool, str]:
        template_prefix = r"(?<!\{)\{"
        template_suffix = r"\.([^}]*)\}(?!\})"
        template = template_prefix + param_prefix + template_suffix
        should_warn = False
        if bool(re.search(template, command_string)):
            should_warn = True
            command_string = re.sub(template, r"${{" + param_prefix + r".\g<1>}}", command_string)
        return (should_warn, command_string)

    input_warn, command = _check_for_parameter("inputs", command)
    output_warn, command = _check_for_parameter("outputs", command)
    sweep_warn, command = _check_for_parameter("search_space", command)
    if input_warn or output_warn or sweep_warn:
        module_logger.warning("Use of {} for parameters is deprecated, instead use ${{}}.")
    return command


def transform_dict_keys(data: Dict[str, Any], casing_transform: Callable[[str], str]) -> Dict[str, Any]:
    """Convert all keys of a nested dictionary according to the passed casing_transform function.

    :param data: The data to transform
    :type data: Dict[str, Any]
    :param casing_transform: A callable applied to all keys in data
    :type casing_transform: Callable[[str], str]
    :return: A dictionary with transformed keys
    :rtype: dict
    """
    return {
        casing_transform(key): transform_dict_keys(val, casing_transform) if isinstance(val, dict) else val
        for key, val in data.items()
    }


def merge_dict(origin, delta, dep=0) -> dict:
    """Merge two dicts recursively.
    Note that the function will return a copy of the origin dict if the depth of the recursion is 0.

    :param origin: The original dictionary
    :type origin: dict
    :param delta: The delta dictionary
    :type delta: dict
    :param dep: The depth of the recursion
    :type dep: int
    :return: The merged dictionary
    :rtype: dict
    """
    result = copy.deepcopy(origin) if dep == 0 else origin
    for key, val in delta.items():
        origin_val = origin.get(key)
        # Merge delta dict with original dict
        if isinstance(origin_val, dict) and isinstance(val, dict):
            result[key] = merge_dict(origin_val, val, dep + 1)
            continue
        result[key] = copy.deepcopy(val)
    return result


def retry(
    exceptions: Union[Tuple[Exception], Exception],
    failure_msg: str,
    logger: Any,
    max_attempts: int = 1,
    delay_multiplier: int = 0.25,
) -> Callable:
    """Retry a function if it fails.

    :param exceptions: Exceptions to retry on.
    :type exceptions: Union[Tuple[Exception], Exception]
    :param failure_msg: Message to log on failure.
    :type failure_msg: str
    :param logger: Logger to use.
    :type logger: Any
    :param max_attempts: Maximum number of attempts.
    :type max_attempts: int
    :param delay_multiplier: Multiplier for delay between attempts.
    :type delay_multiplier: int
    :return: Decorated function.
    :rtype: Callable
    """

    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
            tries = max_attempts + 1
            counter = 1
            while tries > 1:
                delay = delay_multiplier * 2**counter + random.uniform(0, 1)
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    tries -= 1
                    counter += 1
                    if tries == 1:
                        logger.warning(failure_msg)
                        raise e
                    logger.info(f"Operation failed. Retrying in {delay} seconds.")
                    time.sleep(delay)

        return func_with_retries

    return retry_decorator


def get_list_view_type(include_archived: bool, archived_only: bool) -> ListViewType:
    """Get the list view type based on the include_archived and archived_only flags.

    :param include_archived: Whether to include archived items.
    :type include_archived: bool
    :param archived_only: Whether to only include archived items.
    :type archived_only: bool
    :return: The list view type.
    :rtype: ListViewType
    """
    if include_archived and archived_only:
        msg = "Cannot provide both archived-only and include-archived."
        raise MlException(message=msg, no_personal_data_message=msg)
    if include_archived:
        return ListViewType.ALL
    if archived_only:
        return ListViewType.ARCHIVED_ONLY
    return ListViewType.ACTIVE_ONLY


def is_data_binding_expression(
    value: str, binding_prefix: Union[str, List[str]] = "", is_singular: bool = True
) -> bool:
    """Check if a value is a data-binding expression with specific binding target(prefix). Note that the function will
    return False if the value is not a str. For example, if binding_prefix is ["parent", "jobs"], then input_value is a
    data-binding expression only if the binding target starts with "parent.jobs", like "${{parent.jobs.xxx}}" if
    is_singular is False, return True even if input_value includes non-binding part or multiple binding targets, like
    "${{parent.jobs.xxx}}_extra" and "${{parent.jobs.xxx}}_{{parent.jobs.xxx}}".

    :param value: Value to check.
    :type value: str
    :param binding_prefix: Prefix to check for.
    :type binding_prefix: Union[str, List[str]]
    :param is_singular: should the value be a singular data-binding expression, like "${{parent.jobs.xxx}}".
    :type is_singular: bool
    :return: True if the value is a data-binding expression, False otherwise.
    :rtype: bool
    """
    return len(get_all_data_binding_expressions(value, binding_prefix, is_singular)) > 0


def get_all_data_binding_expressions(
    value: str, binding_prefix: Union[str, List[str]] = "", is_singular: bool = True
) -> List[str]:
    """Get all data-binding expressions in a value with specific binding target(prefix). Note that the function will
    return an empty list if the value is not a str.

    :param value: Value to extract.
    :type value: str
    :param binding_prefix: Prefix to filter.
    :type binding_prefix: Union[str, List[str]]
    :param is_singular: should the value be a singular data-binding expression, like "${{parent.jobs.xxx}}".
    :type is_singular: bool
    :return: list of data-binding expressions.
    :rtype: List[str]
    """
    if isinstance(binding_prefix, str):
        binding_prefix = [binding_prefix]
    if isinstance(value, str):
        target_regex = r"\$\{\{\s*(" + "\\.".join(binding_prefix) + r"\S*?)\s*\}\}"
        if is_singular:
            target_regex = "^" + target_regex + "$"
        return re.findall(target_regex, value)
    return []


def is_private_preview_enabled():
    """Check if private preview features are enabled.

    :return: True if private preview features are enabled, False otherwise.
    :rtype: bool
    """
    return os.getenv(AZUREML_PRIVATE_FEATURES_ENV_VAR) in ["True", "true", True]


def is_bytecode_optimization_enabled():
    """Check if bytecode optimization is enabled:
    1) bytecode package is installed
    2) private preview is enabled
    3) python version is between 3.6 and 3.11

    :return: True if bytecode optimization is enabled, False otherwise.
    :rtype: bool
    """
    try:
        import bytecode  # pylint: disable=unused-import

        return is_private_preview_enabled() and (3, 6) < sys.version_info < (3, 12)
    except ImportError:
        return False


def is_on_disk_cache_enabled():
    """Check if on-disk cache for component registrations in pipeline submission is enabled.

    :return: True if on-disk cache is enabled, False otherwise.
    :rtype: bool
    """
    return os.getenv(AZUREML_DISABLE_ON_DISK_CACHE_ENV_VAR) not in ["True", "true", True]


def is_concurrent_component_registration_enabled():  # pylint: disable=name-too-long
    """Check if concurrent component registrations in pipeline submission is enabled.

    :return: True if concurrent component registration is enabled, False otherwise.
    :rtype: bool
    """
    return os.getenv(AZUREML_DISABLE_CONCURRENT_COMPONENT_REGISTRATION) not in ["True", "true", True]


def _is_internal_components_enabled():
    return os.getenv(AZUREML_INTERNAL_COMPONENTS_ENV_VAR) in ["True", "true", True]


def try_enable_internal_components(*, force=False) -> bool:
    """Try to enable internal components for the current process. This is the only function outside _internal that
    references _internal.

    :keyword force: Force enable internal components even if enabled before.
    :type force: bool
    :return: True if internal components are enabled, False otherwise.
    :rtype: bool
    """
    if _is_internal_components_enabled():
        from azure.ai.ml._internal import enable_internal_components_in_pipeline

        enable_internal_components_in_pipeline(force=force)

        return True
    return False


def is_internal_component_data(data: Dict[str, Any], *, raise_if_not_enabled: bool = False) -> bool:
    """Check if the data is an internal component data by checking schema url prefix.

    :param data: The data to check.
    :type data: Dict[str, Any]
    :keyword raise_if_not_enabled: Raise exception if the data is an internal component data but
        internal components is not enabled.
    :type raise_if_not_enabled: bool
    :return: True if the data is an internal component data, False otherwise.
    :rtype: bool
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the data is an internal component data but
        internal components is not enabled.
    """
    from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

    # These imports can't be placed in at top file level because it will cause a circular import in
    # exceptions.py via _get_mfe_url_override

    schema = data.get(CommonYamlFields.SCHEMA, None)

    if schema is None or not isinstance(schema, str):
        return False

    if not schema.startswith(AZUREML_INTERNAL_COMPONENTS_SCHEMA_PREFIX):
        return False

    if not _is_internal_components_enabled() and raise_if_not_enabled:
        no_personal_data_message = (
            f"Internal components is a private feature in v2, please set environment variable "
            f"{AZUREML_INTERNAL_COMPONENTS_ENV_VAR} to true to use it."
        )
        msg = f"Detected schema url {schema}. {no_personal_data_message}"
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPONENT,
            error_type=ValidationErrorType.INVALID_VALUE,
            no_personal_data_message=no_personal_data_message,
            error_category=ErrorCategory.USER_ERROR,
        )

    return True


def is_valid_node_name(name: str) -> bool:
    """Check if `name` is a valid node name

    :param name: A node name
    :type name: str
    :return: Return True if the string is a valid Python identifier in lower ASCII range, False otherwise.
    :rtype: bool
    """
    return isinstance(name, str) and name.isidentifier() and re.fullmatch(r"^[a-z_][a-z\d_]*", name) is not None


def parse_args_description_from_docstring(docstring: str) -> Dict[str, str]:
    """Return arg descriptions in docstring with google style.

    e.g.
        docstring =
            '''
            A pipeline with detailed docstring, including descriptions for inputs and outputs.

            In this pipeline docstring, there are descriptions for inputs and outputs
            Input/Output descriptions can infer from descriptions here.

            Args:
                job_in_path: a path parameter
                job_in_number: a number parameter
                                with multi-line description
                job_in_int (int): a int parameter

            Other docstring xxxxxx
                random_key: random_value
            '''

    return dict:
            args = {
                'job_in_path': 'a path parameter',
                'job_in_number': 'a number parameter with multi-line description',
                'job_in_int': 'a int parameter'
            }

    :param docstring: A Google-style docstring
    :type docstring: str
    :return: A map of parameter names to parameter descriptions
    :rtype: Dict[str, str]
    """
    args = {}
    if not isinstance(docstring, str):
        return args
    lines = [line.strip() for line in docstring.splitlines()]
    for index, line in enumerate(lines):
        if line.lower() == "args:":
            args_region = lines[index + 1 :]
            args_line_end = args_region.index("") if "" in args_region else len(args_region)
            args_region = args_region[0:args_line_end]
            while len(args_region) > 0 and ":" in args_region[0]:
                arg_line = args_region[0]
                colon_index = arg_line.index(":")
                arg, description = (
                    arg_line[0:colon_index].strip(),
                    arg_line[colon_index + 1 :].strip(),
                )
                # handle case like "param (float) : xxx"
                if "(" in arg:
                    arg = arg[0 : arg.index("(")].strip()
                args[arg] = description
                args_region.pop(0)
                # handle multi-line description, assuming description has no colon inside.
                while len(args_region) > 0 and ":" not in args_region[0]:
                    args[arg] += " " + args_region[0]
                    args_region.pop(0)
    return args


def convert_windows_path_to_unix(path: Union[str, PathLike]) -> str:
    """Convert a Windows path to a Unix path.

    :param path: A Windows path
    :type path: Union[str, os.PathLike]
    :return: A Unix path
    :rtype: str
    """
    return PureWindowsPath(path).as_posix()


def _is_user_error_from_status_code(http_status_code):
    return 400 <= http_status_code < 500


def _str_to_bool(s: str) -> bool:
    """Converts a string to a boolean

    Can be used as a type for argument in argparse, return argument's boolean value according to it's literal value.

    :param s: The string to convert
    :type s: str
    :return: True if s is "true" (case-insensitive), otherwise returns False.
    :rtype: bool
    """
    if not isinstance(s, str):
        return False
    return s.lower() == "true"


def _is_user_error_from_exception_type(e: Optional[Exception]) -> bool:
    """Determine whether if an exception is user error from it's exception type.

    :param e: An exception
    :type e: Optional[Exception]
    :return: True if exception is a user error
    :rtype: bool
    """
    # Connection error happens on user's network failure, should be user error.
    # For OSError/IOError with error no 28: "No space left on device" should be sdk user error
    return isinstance(e, (ConnectionError, KeyboardInterrupt)) or (isinstance(e, (IOError, OSError)) and e.errno == 28)


class DockerProxy:
    """A proxy class for docker module. It will raise a more user-friendly error message if docker module is not
    installed.
    """

    def __getattribute__(self, name: str) -> Any:
        try:
            import docker  # pylint: disable=import-error

            return getattr(docker, name)
        except ModuleNotFoundError as e:
            msg = "Please install docker in the current python environment with `pip install docker` and try again."
            raise MlException(message=msg, no_personal_data_message=msg) from e


def get_all_enum_values_iter(enum_type: type) -> Iterable[Any]:
    """Get all values of an enum type.

    :param enum_type: An "enum" (not necessary enum.Enum)
    :type enum_type: Type
    :return: An iterable of all of the attributes of `enum_type`
    :rtype: Iterable[Any]
    """
    for key in dir(enum_type):
        if not key.startswith("_"):
            yield getattr(enum_type, key)


def write_to_shared_file(file_path: Union[str, PathLike], content: str):
    """Open file with specific mode and return the file object.

    :param file_path: Path to the file.
    :type file_path: Union[str, os.PathLike]
    :param content: Content to write to the file.
    :type content: str
    """
    with open(file_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
        f.write(content)

    # share_mode means read/write for owner, group and others
    share_mode, mode_mask = 0o666, 0o777
    if os.stat(file_path).st_mode & mode_mask != share_mode:
        try:
            os.chmod(file_path, share_mode)
        except PermissionError:
            pass


def _get_valid_dot_keys_with_wildcard_impl(
    left_reversed_parts, root, *, validate_func=None, cur_node=None, processed_parts=None
) -> List[str]:
    if len(left_reversed_parts) == 0:
        if validate_func is None or validate_func(root, processed_parts):
            return [".".join(processed_parts)]
        return []

    if cur_node is None:
        cur_node = root
    if not isinstance(cur_node, dict):
        return []
    if processed_parts is None:
        processed_parts = []

    key: str = left_reversed_parts.pop()
    result = []
    if key == "*":
        for next_key in cur_node:
            if not isinstance(next_key, str):
                continue
            processed_parts.append(next_key)
            result.extend(
                _get_valid_dot_keys_with_wildcard_impl(
                    left_reversed_parts,
                    root,
                    validate_func=validate_func,
                    cur_node=cur_node[next_key],
                    processed_parts=processed_parts,
                )
            )
            processed_parts.pop()
    elif key in cur_node:
        processed_parts.append(key)
        result = _get_valid_dot_keys_with_wildcard_impl(
            left_reversed_parts,
            root,
            validate_func=validate_func,
            cur_node=cur_node[key],
            processed_parts=processed_parts,
        )
        processed_parts.pop()

    left_reversed_parts.append(key)
    return result


def get_valid_dot_keys_with_wildcard(
    root: Dict[str, Any],
    dot_key_wildcard: str,
    *,
    validate_func: Optional[Callable[[List[str], Dict[str, Any]], bool]] = None,
) -> List[str]:
    """Get all valid dot keys with wildcard. Only "x.*.x" and "x.*" is supported for now.

    A valid dot key should satisfy the following conditions:
    1) It should be a valid dot key in the root node.
    2) It should satisfy the validation function.

    :param root: Root node.
    :type root: Dict[str, Any]
    :param dot_key_wildcard: Dot key with wildcard, e.g. "a.*.c".
    :type dot_key_wildcard: str
    :keyword validate_func: Validation function. It takes two parameters: the root node and the dot key parts.
    If None, no validation will be performed.
    :paramtype validate_func: Optional[Callable[[List[str], Dict[str, Any]], bool]]
    :return: List of valid dot keys.
    :rtype: List[str]
    """
    left_reversed_parts = dot_key_wildcard.split(".")[::-1]
    return _get_valid_dot_keys_with_wildcard_impl(left_reversed_parts, root, validate_func=validate_func)


def get_base_directory_for_cache() -> Path:
    """Get the base directory for cache files.

    :return: The base directory for cache files.
    :rtype: Path
    """
    return Path(tempfile.gettempdir()).joinpath("azure-ai-ml")


def get_versioned_base_directory_for_cache() -> Path:
    """Get the base directory for cache files of current version of azure-ai-ml.
    Cache files of different versions will be stored in different directories.

    :return: The base directory for cache files of current version of azure-ai-ml.
    :rtype: Path
    """
    # import here to avoid circular import
    from azure.ai.ml._version import VERSION

    return get_base_directory_for_cache().joinpath(VERSION)


# pylint: disable-next=name-too-long
def get_resource_and_group_name_from_resource_id(armstr: str) -> str:
    if armstr.find("/") == -1:
        return armstr, None
    return armstr.split("/")[-1], armstr.split("/")[-5]


# pylint: disable-next=name-too-long
def get_resource_group_name_from_resource_group_id(armstr: str) -> str:
    if armstr.find("/") == -1:
        return armstr
    return armstr.split("/")[-1]


def extract_name_and_version(azureml_id: str) -> Dict[str, str]:
    """Extract name and version from azureml id.

    :param azureml_id: AzureML id.
    :type azureml_id: str
    :return: A dict of name and version.
    :rtype: Dict[str, str]
    """
    if not isinstance(azureml_id, str):
        raise ValueError("azureml_id should be a string but got {}: {}.".format(type(azureml_id), azureml_id))
    if azureml_id.count(":") != 1:
        raise ValueError("azureml_id should be in the format of name:version but got {}.".format(azureml_id))
    name, version = azureml_id.split(":")
    return {
        "name": name,
        "version": version,
    }


def _get_evaluator_properties():
    return {"is-promptflow": "true", "is-evaluator": "true"}


def _is_evaluator(properties: Dict[str, str]) -> bool:
    return properties.get("is-evaluator") == "true" and properties.get("is-promptflow") == "true"
