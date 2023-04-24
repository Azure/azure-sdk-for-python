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
import time
import warnings
from collections import OrderedDict
from contextlib import contextmanager
from datetime import timedelta
from functools import singledispatch, wraps
from os import PathLike
from pathlib import PosixPath, PureWindowsPath
from typing import IO, Any, AnyStr, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
from uuid import UUID

import isodate
import pydash
import yaml

from azure.ai.ml._restclient.v2022_05_01.models import ListViewType, ManagedServiceIdentity
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml.constants._common import (
    API_URL_KEY,
    AZUREML_INTERNAL_COMPONENTS_ENV_VAR,
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
    AZUREML_DISABLE_ON_DISK_CACHE_ENV_VAR,
    AZUREML_DISABLE_CONCURRENT_COMPONENT_REGISTRATION,
)
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


def _csv_parser(text: Optional[str], convert: Callable) -> str:
    if text:
        if "," in text:
            txts = []
            for t in text.split(","):
                t = convert(t.strip())
                txts.append(t)
            return ",".join(txts)
        return convert(text)


def _snake_to_pascal_convert(text: str) -> str:
    return string.capwords(text.replace("_", " ")).replace(" ", "")


def snake_to_pascal(text: Optional[str]) -> str:
    return _csv_parser(text, _snake_to_pascal_convert)


def snake_to_kebab(text: Optional[str]) -> Optional[str]:
    if text:
        return re.sub("_", "-", text)


# https://stackoverflow.com/questions/1175208
# This works for pascal to snake as well
def _camel_to_snake_convert(text: str) -> str:
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", text).lower()


def camel_to_snake(text: str) -> Optional[str]:
    return _csv_parser(text, _camel_to_snake_convert)


# This is snake to camel back which is different from snake to camel
# https://stackoverflow.com/questions/19053707
def snake_to_camel(text: Optional[str]) -> Optional[str]:
    """convert snake name to camel."""
    if text:
        return re.sub("_([a-zA-Z0-9])", lambda m: m.group(1).upper(), text)


# This is real snake to camel
def _snake_to_camel(name):
    return re.sub(r"(?:^|_)([a-z])", lambda x: x.group(1).upper(), name)


def camel_case_transformer(key, value):
    """transfer string to camel case."""
    return (snake_to_camel(key), value)


def float_to_str(f):
    with decimal.localcontext() as ctx:
        ctx.prec = 20  # Support up to 20 significant figures.
        float_as_dec = ctx.create_decimal(repr(f))
        return format(float_as_dec, "f")


def create_requests_pipeline_with_retry(*, requests_pipeline: HttpPipeline, retries: int = 3) -> HttpPipeline:
    """Creates an HttpPipeline that reuses the same configuration as the supplied pipeline (including the transport),
    but overwrites the retry policy.

    Args:
        requests_pipeline (HttpPipeline): Pipeline to base new one off of.
        retry (int, optional): Number of retries. Defaults to 3.

    Returns:
        HttpPipeline: Pipeline identical to provided one, except with a new
                     retry policy.
    """
    return requests_pipeline.with_policies(retry_policy=get_retry_policy(num_retry=retries))


def get_retry_policy(num_retry=3) -> RetryPolicy:
    """
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

    Args:
        source_uri (str): URI to download
        requests_pipeline (HttpPipeline):  Used to send the request
        timeout (Union[float, Tuple[float, float]], optional): One of
            * float that specifies the connect and read time outs
            * a 2-tuple that specifies the connect and read time out in that order
    Returns:
        str: the Response text
    """
    if not timeout:
        timeout_params = {}
    else:
        connect_timeout, read_timeout = timeout if isinstance(timeout, tuple) else (timeout, timeout)
        timeout_params = dict(read_timeout=read_timeout, connection_timeout=connect_timeout)

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
        with open(file_path, "r") as f:
            cfg = f.read()
    except OSError:  # FileNotFoundError introduced in Python 3
        msg = "No such file or directory: {}"
        raise ValidationException(
            message=msg.format(file_path),
            no_personal_data_message=msg.format("[file_path]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )
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
        with open(file_path, "r") as f:
            cfg = json.load(f)
    except OSError:  # FileNotFoundError introduced in Python 3
        msg = "No such file or directory: {}"
        raise ValidationException(
            message=msg.format(file_path),
            no_personal_data_message=msg.format("[file_path]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )
    return cfg


def load_yaml(source: Optional[Union[AnyStr, PathLike, IO]]) -> Dict:
    # null check - just return an empty dict.
    # Certain CLI commands rely on this behavior to produce a resource
    # via CLI, which is then populated through CLArgs.
    """Load a local YAML file.

    :param file_path: The relative or absolute path to the local file.
    :type file_path: str
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

    # pylint: disable=redefined-builtin
    input = None  # type: IOBase
    must_open_file = False
    try:  # check source type by duck-typing it as an IOBase
        readable = source.readable()
        if not readable:  # source is misformatted stream or file
            msg = "File Permissions Error: The already-open \n\n inputted file is not readable."
            raise ValidationException(
                message=msg,
                no_personal_data_message="File Permissions error",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        # source is an already-open stream or file, we can read() from it directly.
        input = source
    except AttributeError:
        # source has no writable() function, assume it's a string or file path.
        must_open_file = True

    if must_open_file:  # If supplied a file path, open it.
        try:
            input = open(source, "r")
        except OSError:  # FileNotFoundError introduced in Python 3
            msg = "No such file or directory: {}"
            raise ValidationException(
                message=msg.format(source),
                no_personal_data_message=msg.format("[file_path]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
            )
    # input should now be an readable file or stream. Parse it.
    cfg = {}
    try:
        cfg = yaml.safe_load(input)
    except yaml.YAMLError as e:
        msg = f"Error while parsing yaml file: {source} \n\n {str(e)}"
        raise ValidationException(
            message=msg,
            no_personal_data_message="Error while parsing yaml file",
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
            error_type=ValidationErrorType.CANNOT_PARSE,
        )
    finally:
        if must_open_file:
            input.close()
    return cfg


def dump_yaml(*args, **kwargs):
    """A thin wrapper over yaml.dump which forces `OrderedDict`s to be serialized as mappings.

    Otherwise behaves identically to yaml.dump
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

    # Check inputs
    output = None  # type: IOBase
    must_open_file = False
    try:  # check dest type by duck-typing it as an IOBase
        writable = dest.writable()
        if not writable:  # dest is misformatted stream or file
            msg = "File Permissions Error: The already-open \n\n inputted file is not writable."
            raise ValidationException(
                message=msg,
                no_personal_data_message="File Permissions error",
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.CANNOT_PARSE,
            )
        # dest is an already-open stream or file, we can write() to it directly.
        output = dest
    except AttributeError:
        # dest has no writable() function, assume it's a string or file path.
        must_open_file = True

    if must_open_file:  # If supplied a file path, open it.
        try:
            output = open(dest, "w")
        except OSError:  # FileNotFoundError introduced in Python 3
            msg = "No such file or directory: {}"
            raise ValidationException(
                message=msg.format(dest),
                no_personal_data_message=msg.format("[file_path]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
            )

    # Once we have an open file pointer through either method, dump.
    try:
        dump_yaml(data_dict, output, default_flow_style=default_flow_style)
    except yaml.YAMLError as e:
        msg = f"Error while parsing yaml file \n\n {str(e)}"
        raise ValidationException(
            message=msg,
            no_personal_data_message="Error while parsing yaml file",
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
            error_type=ValidationErrorType.CANNOT_PARSE,
        )
    finally:
        # close the file only if we opened it as part of this function.
        if must_open_file:
            output.close()


def dict_eq(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> bool:
    if not dict1 and not dict2:
        return True
    return dict1 == dict2


def get_http_response_and_deserialized_from_pipeline_response(
    pipeline_response: Any, deserialized: Any
) -> Tuple[Any, Any]:
    return pipeline_response.http_response, deserialized


def xor(a: Any, b: Any) -> bool:
    return bool(a) != bool(b)


def is_url(value: Union[PathLike, str]) -> bool:
    try:
        result = urlparse(str(value))
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


# Resolve an URL to long form if it is an azureml short from datastore URL, otherwise return the same value
def resolve_short_datastore_url(value: Union[PathLike, str], workspace: OperationScope) -> str:
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
    try:
        if urlparse(str(value)).scheme == "runs":
            return value
    except ValueError:
        return False


def validate_ml_flow_folder(path: str, model_type: string) -> None:
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
    try:
        uuid_obj = UUID(test_uuid, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == test_uuid


@singledispatch
def from_iso_duration_format(duration: Optional[Any] = None) -> int:  # pylint: disable=unused-argument
    return None


@from_iso_duration_format.register(str)
def _(duration: str) -> int:
    return int(isodate.parse_duration(duration).total_seconds())


@from_iso_duration_format.register(timedelta)
def _(duration: timedelta) -> int:
    return int(duration.total_seconds())


def to_iso_duration_format_mins(time_in_mins: Optional[Union[int, float]]) -> str:
    return isodate.duration_isoformat(timedelta(minutes=time_in_mins)) if time_in_mins else None


def from_iso_duration_format_mins(duration: Optional[str]) -> int:
    return int(from_iso_duration_format(duration) / 60) if duration else None


def to_iso_duration_format(time_in_seconds: Optional[Union[int, float]]) -> str:
    return isodate.duration_isoformat(timedelta(seconds=time_in_seconds)) if time_in_seconds else None


def to_iso_duration_format_ms(time_in_ms: Optional[Union[int, float]]) -> str:
    return isodate.duration_isoformat(timedelta(milliseconds=time_in_ms)) if time_in_ms else None


def from_iso_duration_format_ms(duration: Optional[str]) -> int:
    return from_iso_duration_format(duration) * 1000 if duration else None


def to_iso_duration_format_days(time_in_days: Optional[int]) -> str:
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


def _get_mfe_base_url_from_discovery_service(
    workspace_operations: Any, workspace_name: str, requests_pipeline: HttpPipeline
) -> str:
    discovery_url = workspace_operations.get(workspace_name).discovery_url

    all_urls = json.loads(
        download_text_from_url(
            discovery_url,
            create_requests_pipeline_with_retry(requests_pipeline=requests_pipeline),
        )
    )
    return f"{all_urls[API_URL_KEY]}{MFE_PATH_PREFIX}"


def _get_mfe_base_url_from_registry_discovery_service(
    workspace_operations: Any, workspace_name: str, requests_pipeline: HttpPipeline
) -> str:
    discovery_url = workspace_operations.get(workspace_name).discovery_url

    all_urls = json.loads(
        download_text_from_url(
            discovery_url,
            create_requests_pipeline_with_retry(requests_pipeline=requests_pipeline),
        )
    )
    return all_urls[API_URL_KEY]


def _get_mfe_base_url_from_batch_endpoint(endpoint: "BatchEndpoint") -> str:
    return endpoint.scoring_uri.split("/subscriptions/")[0]


# Allows to use a modified client with a provided url
@contextmanager
def modified_operation_client(operation_to_modify, url_to_use):
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
    return duration.split(".")[0].replace("PT", "").replace("M", "m ") + "s"


def hash_dict(items: dict, keys_to_omit=None):
    """Return hash GUID of a dictionary except keys_to_omit."""
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
    if identity:
        if identity.type.lower() in ("system_assigned", "none"):
            identity = ManagedServiceIdentity(type="SystemAssigned")
        else:
            if identity.user_assigned_identities:
                if isinstance(identity.user_assigned_identities, dict):  # if the identity is already in right format
                    return identity
                ids = dict()
                for id in identity.user_assigned_identities:  # pylint: disable=redefined-builtin
                    ids[id["resource_id"]] = {}
                identity.user_assigned_identities = ids
                identity.type = snake_to_camel(identity.type)
    else:
        identity = ManagedServiceIdentity(type="SystemAssigned")
    return identity


def strip_double_curly(io_binding_val: str) -> str:
    return io_binding_val.replace("${{", "").replace("}}", "")


def append_double_curly(io_binding_val: str) -> str:
    return f"${{{{{io_binding_val}}}}}"


def map_single_brackets_and_warn(command: str):
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


def transform_dict_keys(data: Dict, casing_transform: Callable[[str], str], exclude_keys=None) -> Dict:
    """Convert all keys of a nested dictionary according to the passed casing_transform function."""
    transformed_dict = {}
    for key in data.keys():
        # Modify the environment_variables separately: don't transform values in environment_variables.
        # Todo: Pass in json to the overrides field
        if (exclude_keys and key in exclude_keys) or (not isinstance(data[key], dict)):
            transformed_dict[casing_transform(key)] = data[key]
        else:
            transformed_dict[casing_transform(key)] = transform_dict_keys(data[key], casing_transform)
    return transformed_dict


def merge_dict(origin, delta, dep=0):
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
):
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
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
    if include_archived and archived_only:
        raise Exception("Cannot provide both archived-only and include-archived.")
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
    :param binding_prefix: Prefix to check for.
    :param is_singular: should the value be a singular data-binding expression, like "${{parent.jobs.xxx}}".
    :return: True if the value is a data-binding expression, False otherwise.
    """
    return len(get_all_data_binding_expressions(value, binding_prefix, is_singular)) > 0


def get_all_data_binding_expressions(
    value: str, binding_prefix: Union[str, List[str]] = "", is_singular: bool = True
) -> List[str]:
    """Get all data-binding expressions in a value with specific binding target(prefix). Note that the function will
    return an empty list if the value is not a str.

    :param value: Value to extract.
    :param binding_prefix: Prefix to filter.
    :param is_singular: should the value be a singular data-binding expression, like "${{parent.jobs.xxx}}".
    :return: list of data-binding expressions.
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
    return os.getenv(AZUREML_PRIVATE_FEATURES_ENV_VAR) in ["True", "true", True]


def is_on_disk_cache_enabled():
    return os.getenv(AZUREML_DISABLE_ON_DISK_CACHE_ENV_VAR) not in ["True", "true", True]


def is_concurrent_component_registration_enabled():
    return os.getenv(AZUREML_DISABLE_CONCURRENT_COMPONENT_REGISTRATION) not in ["True", "true", True]


def is_internal_components_enabled():
    return os.getenv(AZUREML_INTERNAL_COMPONENTS_ENV_VAR) in ["True", "true", True]


def try_enable_internal_components(*, force=False):
    """Try to enable internal components for the current process. This is the only function outside _internal that
    references _internal.

    :param force: Force enable internal components even if enabled before.
    """
    if is_internal_components_enabled():
        from azure.ai.ml._internal import enable_internal_components_in_pipeline

        enable_internal_components_in_pipeline(force=force)


def is_valid_node_name(name):
    """Return True if the string is a valid Python identifier in lower ASCII range, False otherwise.

    The regular expression match pattern is r"^[a-z_][a-z0-9_]*".
    """
    return isinstance(name, str) and name.isidentifier() and re.fullmatch(r"^[a-z_][a-z\d_]*", name) is not None


def parse_args_description_from_docstring(docstring):
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


def convert_windows_path_to_unix(path: Union[str, PathLike]) -> PosixPath:
    return PureWindowsPath(path).as_posix()


def _is_user_error_from_status_code(http_status_code):
    return 400 <= http_status_code < 500


def _str_to_bool(s):
    """Returns True if literal 'true' is passed, otherwise returns False.

    Can be used as a type for argument in argparse, return argument's boolean value according to it's literal value.
    """
    if not isinstance(s, str):
        return False
    return s.lower() == "true"


def _is_user_error_from_exception_type(e: Union[Exception, None]):
    """Determine whether if an exception is user error from it's exception type."""
    # Connection error happens on user's network failure, should be user error.
    # For OSError/IOError with error no 28: "No space left on device" should be sdk user error
    if isinstance(e, (ConnectionError, KeyboardInterrupt)) or (isinstance(e, (IOError, OSError)) and e.errno == 28):
        return True


class DockerProxy:
    def __getattribute__(self, name: str) -> Any:
        try:
            import docker  # pylint: disable=import-error

            return getattr(docker, name)
        except ModuleNotFoundError:
            raise Exception(
                "Please install docker in the current python environment with `pip install docker` and try again."
            )


def get_all_enum_values_iter(enum_type):
    """Get all values of an enum type."""
    for key in dir(enum_type):
        if not key.startswith("_"):
            yield getattr(enum_type, key)


def write_to_shared_file(file_path: Union[str, PathLike], content: str):
    """Open file with specific mode and return the file object.

    :param file_path: Path to the file.
    :param content: Content to write to the file.
    """
    with open(file_path, "w") as f:
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
):
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
):
    """Get all valid dot keys with wildcard. Only "x.*.x" and "x.*" is supported for now.

    A valid dot key should satisfy the following conditions:
    1) It should be a valid dot key in the root node.
    2) It should satisfy the validation function.

    :param root: Root node.
    :type root: Dict[str, Any]
    :param dot_key_wildcard: Dot key with wildcard, e.g. "a.*.c".
    :type dot_key_wildcard: str
    :param validate_func: Validation function. It takes two parameters: the root node and the dot key parts.
    If None, no validation will be performed.
    :type validate_func: Optional[Callable[[List[str], Dict[str, Any]], bool]]
    :return: List of valid dot keys.
    """
    left_reversed_parts = dot_key_wildcard.split(".")[::-1]
    return _get_valid_dot_keys_with_wildcard_impl(left_reversed_parts, root, validate_func=validate_func)
