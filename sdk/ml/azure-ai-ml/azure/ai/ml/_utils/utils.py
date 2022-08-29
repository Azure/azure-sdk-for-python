# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import hashlib
import json
import logging
import os
import random
import re
import string
import sys
import time
from collections import OrderedDict
from contextlib import contextmanager
from datetime import timedelta
from functools import singledispatch, wraps
from os import PathLike
from pathlib import PosixPath, PureWindowsPath
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
from uuid import UUID

import isodate
import pydash
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_05_01.models import ListViewType, ManagedServiceIdentity
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants import API_URL_KEY, AZUREML_INTERNAL_COMPONENTS_ENV_VAR, AZUREML_PRIVATE_FEATURES_ENV_VAR

module_logger = logging.getLogger(__name__)

DEVELOPER_URL_MFE_ENV_VAR = "AZUREML_DEV_URL_MFE"

# Prefix used when hitting MFE skipping ARM
MFE_PATH_PREFIX = "/mferp/managementfrontend"


def _get_mfe_url_override() -> Optional[str]:
    return os.getenv(DEVELOPER_URL_MFE_ENV_VAR)


def _is_https_url(url: str) -> bool:
    if url:
        return url.lower().startswith("https")
    return False


def _csv_parser(text: Optional[str], convert: Callable) -> str:
    if text:
        if "," in text:
            txts = []
            for text in text.split(","):
                text = convert(text.strip())
                txts.append(text)
            return ",".join(txts)
        else:
            return convert(text)


def _snake_to_pascal_convert(text: str) -> str:
    return string.capwords(text.replace("_", " ")).replace(" ", "")


def snake_to_pascal(text: Optional[str]) -> str:
    return _csv_parser(text, _snake_to_pascal_convert)


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
    if text:
        """convert snake name to camel."""
        return re.sub("_([a-zA-Z0-9])", lambda m: m.group(1).upper(), text)


# This is real snake to camel
def _snake_to_camel(name):
    return re.sub(r"(?:^|_)([a-z])", lambda x: x.group(1).upper(), name)


def camel_case_transformer(key, attr_desc, value):
    """transfer string to camel case."""
    return (snake_to_camel(key), value)


def create_session_with_retry(retry=3) -> requests.Session:
    """Create requests.session with retry.

    :type retry: int
    rtype: Response
    """
    retry_policy = get_retry_policy(num_retry=retry)

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_policy))
    session.mount("http://", HTTPAdapter(max_retries=retry_policy))
    return session


def get_retry_policy(num_retry=3):
    """
    :return: Returns the msrest or requests REST client retry policy.
    :rtype: urllib3.Retry
    """
    status_forcelist = [413, 429, 500, 502, 503, 504]
    backoff_factor = 0.4
    retry_policy = Retry(
        total=num_retry,
        read=num_retry,
        connect=num_retry,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        # By default this is True. We set it to false to get the full error trace, including url and
        # status code of the last retry. Otherwise, the error message is 'too many 500 error responses',
        # which is not useful.
        raise_on_status=False,
    )
    return retry_policy


def download_text_from_url(source_uri: str, session: requests.Session, timeout: tuple = None):
    """
    Downloads the content from an URL
    Returns the Response text
    :return:
    :rtype: str
    """

    if session is None:
        session = create_session_with_retry()
    response = session.get(source_uri, timeout=timeout)

    # Match old behavior from execution service's status API.
    if response.status_code == 404:
        return ""

    # _raise_request_error(response, "Retrieving content from " + uri)
    return response.text


def load_file(file_path: str) -> str:
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
        )
    return cfg


def load_json(file_path: Union[str, os.PathLike, None]) -> Dict:
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
        )
    return cfg


def load_yaml(file_path: Union[str, os.PathLike, None]) -> Dict:
    try:
        cfg = {}
        if file_path is not None:
            with open(file_path, "r") as f:
                cfg = yaml.safe_load(f)
        return cfg
    except OSError:  # FileNotFoundError introduced in Python 3
        msg = "No such file or directory: {}"
        raise ValidationException(
            message=msg.format(file_path),
            no_personal_data_message=msg.format("[file_path]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )
    except yaml.YAMLError as e:
        msg = f"Error while parsing yaml file: {file_path} \n\n {str(e)}"
        raise ValidationException(
            message=msg,
            no_personal_data_message="Error while parsing yaml file",
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )


def dump_yaml(*args, **kwargs):
    """A thin wrapper over yaml.dump which forces `OrderedDict`s to be
    serialized as mappings

    Otherwise behaves identically to yaml.dump
    """

    class OrderedDumper(yaml.Dumper):
        """A modified yaml serializer that forces pyyaml to represent
        an OrderedDict as a mapping instead of a sequence.
        """

        pass

    OrderedDumper.add_representer(OrderedDict, yaml.representer.SafeRepresenter.represent_dict)

    return yaml.dump(*args, Dumper=OrderedDumper, **kwargs)


def dump_yaml_to_file(
    file_path: Union[str, os.PathLike, None],
    data_dict: Union[OrderedDict, dict],
    default_flow_style=None,
) -> None:
    try:
        if file_path is not None:
            with open(file_path, "w") as f:
                dump_yaml(data_dict, f, default_flow_style=default_flow_style, sort_keys=False)
    except OSError:  # FileNotFoundError introduced in Python 3
        msg = "No such file or directory: {}"
        raise ValidationException(
            message=msg.format(file_path),
            no_personal_data_message=msg.format("[file_path]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )
    except yaml.YAMLError as e:
        msg = f"Error while parsing yaml file: {file_path} \n\n {str(e)}"
        raise ValidationException(
            message=msg,
            no_personal_data_message="Error while parsing yaml file",
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )


def dict_eq(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> bool:
    if not dict1 and not dict2:
        return True
    return dict1 == dict2


def get_http_response_and_deserialized_from_pipeline_response(
    pipeline_response: Any, deserialized: Any, *args
) -> Tuple[Any, Any]:
    return pipeline_response.http_response, deserialized


def initialize_logger_info(module_logger: logging.Logger, terminator="\n") -> None:
    module_logger.setLevel(logging.INFO)
    module_logger.propagate = False
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.terminator = terminator
    handler.flush = sys.stderr.flush
    module_logger.addHandler(handler)


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

    # If the URL is not an valid URL (e.g. a local path) or not an azureml URL (e.g. a http URL), just return the same value
    return value


def is_mlflow_uri(value: Union[PathLike, str]) -> bool:
    try:
        if urlparse(str(value)).scheme == "runs":
            return value
    except ValueError:
        return False


def validate_ml_flow_folder(path: str, model_type: string) -> None:
    if not isinstance(path, str):
        path = path.as_posix()
    path_array = path.split("/")
    if model_type != "mlflow_model" or "." not in path_array[-1]:
        return
    else:
        msg = "Error with path {}. Model of type mlflow_model cannot register a file."
        raise ValidationException(
            message=msg.format(path),
            no_personal_data_message=msg.format("[path]"),
            target=ErrorTarget.MODEL,
        )


# modified from: https://stackoverflow.com/a/33245493/8093897
def is_valid_uuid(test_uuid: str) -> bool:

    try:
        uuid_obj = UUID(test_uuid, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == test_uuid


@singledispatch
def from_iso_duration_format(duration: Any = None) -> int:
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


def _get_mfe_base_url_from_discovery_service(workspace_operations: Any, workspace_name: str) -> str:
    discovery_url = workspace_operations.get(workspace_name).discovery_url

    all_urls = json.loads(download_text_from_url(discovery_url, create_session_with_retry()))
    return f"{all_urls[API_URL_KEY]}{MFE_PATH_PREFIX}"


def _get_mfe_base_url_from_registry_discovery_service(workspace_operations: Any, workspace_name: str) -> str:
    discovery_url = workspace_operations.get(workspace_name).discovery_url

    all_urls = json.loads(download_text_from_url(discovery_url, create_session_with_retry()))
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
    object_hash = hashlib.md5()
    object_hash.update(serialized_component_interface.encode("utf-8"))
    return str(UUID(object_hash.hexdigest()))


def convert_identity_dict(
    identity: ManagedServiceIdentity = None,
) -> ManagedServiceIdentity:
    if identity:
        if identity.type.lower() in ("system_assigned", "none"):
            identity = ManagedServiceIdentity(type="SystemAssigned")
        else:
            if identity.user_assigned_identities:
                if isinstance(identity.user_assigned_identities, dict):  # if the identity is already in right format
                    return identity
                else:
                    ids = dict()
                    for id in identity.user_assigned_identities:
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
    """Convert all keys of a nested dictionary according to the passed
    casing_transform function."""
    transformed_dict = {}
    for key in data.keys():
        # Modify the environment_variables separately: don't transform values in environment_variables.
        # Todo: Pass in json to the overrides field
        if (exclude_keys and key in exclude_keys) or (not isinstance(data[key], dict)):
            transformed_dict[casing_transform(key)] = data[key]
        else:
            transformed_dict[casing_transform(key)] = transform_dict_keys(data[key], casing_transform)
    return transformed_dict


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


def show_debug_info(response):
    module_logger.info(f"{module_logger.name} :  Request URL: {response.request.url}")
    module_logger.info(f"{module_logger.name} :  Request method: 'POST'")
    module_logger.info(
        f"{module_logger.name} :  Request headers: \n {json.dumps(dict(response.request.headers), indent=4)}"
    )
    module_logger.info(f"{module_logger.name} :  Request body: \n {response.request.body.decode('utf-8')}")
    module_logger.info(f"{module_logger.name} :  Response status: {response.status_code}")
    module_logger.info(f"{module_logger.name} :  Response headers: \n {json.dumps(dict(response.headers), indent=4)}")
    module_logger.info(f"{module_logger.name} :  Response content: \n {response.content.decode('utf-8')}")


def get_list_view_type(include_archived: bool, archived_only: bool) -> ListViewType:
    if include_archived and archived_only:
        raise Exception("Cannot provide both archived-only and include-archived.")
    if include_archived:
        return ListViewType.ALL
    elif archived_only:
        return ListViewType.ARCHIVED_ONLY
    elif include_archived:
        return ListViewType.ALL
    else:
        return ListViewType.ACTIVE_ONLY


def is_data_binding_expression(
    value: str, binding_prefix: Union[str, List[str]] = "", is_singular: bool = True
) -> bool:
    """Check if a value is a data-binding expression with specific binding
    target(prefix). Note that the function will return False if the value is
    not a str. For example, if binding_prefix is ["parent", "jobs"], then
    input_value is a data-binding expression only if the binding target starts
    with "parent.jobs", like "${{parent.jobs.xxx}}" if is_singular is False,
    return True even if input_value includes non-binding part or multiple
    binding targets, like "${{parent.jobs.xxx}}_extra" and
    "${{parent.jobs.xxx}}_{{parent.jobs.xxx}}".

    :param value: Value to check.
    :param binding_prefix: Prefix to check for.
    :param is_singular: should the value be a singular data-binding expression, like "${{parent.jobs.xxx}}".
    :return: True if the value is a data-binding expression, False otherwise.
    """
    return len(get_all_data_binding_expressions(value, binding_prefix, is_singular)) > 0


def get_all_data_binding_expressions(
    value: str, binding_prefix: Union[str, List[str]] = "", is_singular: bool = True
) -> List[str]:
    """Get all data-binding expressions in a value with specific binding
    target(prefix). Note that the function will return an empty list if the
    value is not a str.

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


def is_internal_components_enabled():
    return os.getenv(AZUREML_INTERNAL_COMPONENTS_ENV_VAR) in ["True", "true", True]


def try_enable_internal_components():
    if is_internal_components_enabled():
        pass


def is_valid_node_name(name):
    """Return True if the string is a valid Python identifier in lower ASCII
    range, False otherwise.

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

    Can be used as a type for argument in argparse, return argument's
    boolean value according to it's literal value.
    """
    if not isinstance(s, str):
        return False
    return s.lower() == "true"


def _is_user_error_from_exception_type(e: Union[Exception, None]):
    """Determine whether if an exception is user error from it's exception
    type."""
    # Connection error happens on user's network failure, should be user error.
    # For OSError/IOError with error no 28: "No space left on device" should be sdk user error
    if isinstance(e, (ConnectionError, KeyboardInterrupt)) or (isinstance(e, (IOError, OSError)) and e.errno == 28):
        return True
