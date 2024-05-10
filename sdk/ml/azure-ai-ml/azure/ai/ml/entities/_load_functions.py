# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-lines

import logging
import warnings
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Union, cast

from marshmallow import ValidationError
from pydash import objects

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._assets._artifacts._package.model_package import ModelPackage
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._assets._artifacts.data import Data
from azure.ai.ml.entities._assets._artifacts.feature_set import FeatureSet
from azure.ai.ml.entities._assets._artifacts.index import Index
from azure.ai.ml.entities._assets._artifacts.model import Model
from azure.ai.ml.entities._assets.environment import Environment
from azure.ai.ml.entities._autogen_entities.models import MarketplaceSubscription, ServerlessEndpoint
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
from azure.ai.ml.entities._deployment.model_batch_deployment import ModelBatchDeployment
from azure.ai.ml.entities._deployment.online_deployment import OnlineDeployment
from azure.ai.ml.entities._deployment.pipeline_component_batch_deployment import PipelineComponentBatchDeployment
from azure.ai.ml.entities._endpoint.batch_endpoint import BatchEndpoint
from azure.ai.ml.entities._endpoint.online_endpoint import OnlineEndpoint
from azure.ai.ml.entities._feature_set.feature_set_backfill_request import FeatureSetBackfillRequest
from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.ai.ml.entities._feature_store_entity.feature_store_entity import FeatureStoreEntity
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._registry.registry import Registry
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._schedule.schedule import Schedule
from azure.ai.ml.entities._validation import PathAwareSchemaValidatableMixin, ValidationResultBuilder
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)

_DEFAULT_RELATIVE_ORIGIN = "./"


def load_common(
    cls: Any,
    source: Union[str, PathLike, IO[AnyStr]],
    relative_origin: Optional[str] = None,
    params_override: Optional[list] = None,
    **kwargs: Any,
) -> Resource:
    """Private function to load a yaml file to an entity object.

    :param cls: The entity class type.
    :type cls: type[Resource]
    :param source: A source of yaml.
    :type source: Union[str, PathLike, IO[AnyStr]]
    :param relative_origin: The origin of to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Must be provided, and is assumed to be assigned by other internal
        functions that call this.
    :type relative_origin: str
    :param params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]
    :return: The loaded resource
    :rtype: Resource
    """

    path = kwargs.pop("path", None)
    # Check for deprecated path input, either named or as first unnamed input
    if source is None and path is not None:
        source = path
        warnings.warn(
            "the 'path' input for load functions is deprecated. Please use 'source' instead.", DeprecationWarning
        )

    if relative_origin is None:
        if isinstance(source, (str, PathLike)):
            relative_origin = str(source)
        else:
            try:
                relative_origin = source.name
            except AttributeError:  # input is a stream or something
                relative_origin = _DEFAULT_RELATIVE_ORIGIN

    params_override = params_override or []
    yaml_dict = _try_load_yaml_dict(source)

    # pylint: disable=protected-access
    cls, type_str = cls._resolve_cls_and_type(data=yaml_dict, params_override=params_override)

    try:
        return _load_common_raising_marshmallow_error(cls, yaml_dict, relative_origin, params_override, **kwargs)
    except ValidationError as e:
        if issubclass(cls, PathAwareSchemaValidatableMixin):
            validation_result = ValidationResultBuilder.from_validation_error(e, source_path=relative_origin)
            schema = cls._create_schema_for_validation(context={BASE_PATH_CONTEXT_KEY: Path.cwd()})
            if type_str is None:
                additional_message = ""
            else:
                additional_message = (
                    f"If you are trying to configure an entity that is not "
                    f"of type {type_str}, please specify the correct "
                    f"type in the 'type' property."
                )

            def build_error(message: str, _: Any) -> ValidationError:
                from azure.ai.ml.entities._util import decorate_validation_error

                return ValidationError(
                    message=decorate_validation_error(
                        schema=schema.__class__,
                        pretty_error=message,
                        additional_message=additional_message,
                    ),
                )

            validation_result.try_raise(error_func=build_error)
        raise e


def _try_load_yaml_dict(source: Union[str, PathLike, IO[AnyStr]]) -> dict:
    yaml_dict = load_yaml(source)
    if yaml_dict is None:  # This happens when a YAML is empty.
        msg = "Target yaml file is empty"
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPONENT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.CANNOT_PARSE,
        )
    if not isinstance(yaml_dict, dict):  # This happens when a YAML file is mal formatted.
        msg = "Expect dict but get {} after parsing yaml file"
        raise ValidationException(
            message=msg.format(type(yaml_dict)),
            target=ErrorTarget.COMPONENT,
            no_personal_data_message=msg.format(type(yaml_dict)),
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.CANNOT_PARSE,
        )
    return yaml_dict


def _load_common_raising_marshmallow_error(
    cls: Any,
    yaml_dict: Dict,
    relative_origin: Optional[Union[PathLike, str, IO[AnyStr]]],
    params_override: Optional[list] = None,
    **kwargs: Any,
) -> Resource:
    # pylint: disable=protected-access
    res: Resource = cls._load(
        data=yaml_dict, yaml_path=relative_origin, params_override=params_override, **kwargs
    )  # pylint: disable=docstring-keyword-should-match-keyword-only
    return res


def add_param_overrides(data, param_overrides) -> None:
    if param_overrides is not None:
        for override in param_overrides:
            for param, val in override.items():
                # Check that none of the intermediary levels are string references (azureml/file)
                param_tokens = param.split(".")
                test_layer = data
                for layer in param_tokens:
                    if test_layer is None:
                        continue
                    if isinstance(test_layer, str):
                        # pylint: disable=broad-exception-raised
                        raise Exception(f"Cannot use '--set' on properties defined by reference strings: --set {param}")
                    test_layer = test_layer.get(layer, None)
                objects.set_(data, param, val)


def load_from_autogen_entity(cls, source: Union[str, PathLike, IO[AnyStr]], **kwargs):
    loaded_dict = _try_load_yaml_dict(source)
    add_param_overrides(loaded_dict, param_overrides=kwargs.get("params_override", None))
    entity = cls(loaded_dict)
    try:
        entity._validate()  # pylint: disable=protected-access
    except ValueError as e:
        validation_result = ValidationResultBuilder.from_single_message(singular_error_message=str(e))
        validation_result.try_raise()
    return entity


def load_job(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Job:
    """Constructs a Job object from a YAML file.

    :param source: A path to a local YAML file or an already-open file object containing a job configuration.
        If the source is a path, it will be opened and read. If the source is an open file, the file will be read
        directly.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The root directory for the YAML. This directory will be used as the origin for deducing
        the relative locations of files referenced in the parsed YAML. Defaults to the same directory as source if
        source is a file or file path input. Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: Optional[str]
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Job cannot be successfully validated.
        Details will be provided in the error message.
    :return: A loaded Job object.
    :rtype: ~azure.ai.ml.entities.Job

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START load_job]
            :end-before: [END load_job]
            :language: python
            :dedent: 8
            :caption: Loading a Job from a YAML config file.
    """
    return cast(Job, load_common(Job, source, relative_origin, params_override, **kwargs))


@experimental
def load_index(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Index:
    """Constructs a Index object from a YAML file.

    :param source: A path to a local YAML file or an already-open file object containing an index configuration.
        If the source is a path, it will be opened and read. If the source is an open file, the file will be read
        directly.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The root directory for the YAML. This directory will be used as the origin for deducing
        the relative locations of files referenced in the parsed YAML. Defaults to the same directory as source if
        source is a file or file path input. Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: Optional[str]
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Index cannot be successfully validated.
        Details will be provided in the error message.
    :return: A loaded Index object.
    :rtype: ~azure.ai.ml.entities.Index
    """
    return cast(Index, load_common(Index, source, relative_origin, params_override, **kwargs))


@experimental
def load_serverless_endpoint(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> ServerlessEndpoint:
    return load_from_autogen_entity(ServerlessEndpoint, source, **kwargs)


@experimental
def load_marketplace_subscription(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> MarketplaceSubscription:
    return load_from_autogen_entity(MarketplaceSubscription, source, **kwargs)


def load_workspace(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Workspace:
    """Load a workspace object from a yaml file. This includes workspace sub-classes
    like hubs and projects.

    :param source: The local yaml source of a workspace. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Loaded workspace object.
    :rtype: Workspace

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START load_workspace]
            :end-before: [END load_workspace]
            :language: python
            :dedent: 8
            :caption: Loading a Workspace from a YAML config file.
    """
    return cast(Workspace, load_common(Workspace, source, relative_origin, params_override, **kwargs))


def load_registry(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Registry:
    """Load a registry object from a yaml file.

    :param source: The local yaml source of a registry. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Loaded registry object.
    :rtype: Registry
    """
    return cast(Registry, load_common(Registry, source, relative_origin, params_override, **kwargs))


def load_datastore(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Datastore:
    """Construct a datastore object from a yaml file.

    :param source: The local yaml source of a datastore. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Datastore cannot be successfully validated.
        Details will be provided in the error message.
    :return: Loaded datastore object.
    :rtype: Datastore
    """
    return cast(Datastore, load_common(Datastore, source, relative_origin, params_override, **kwargs))


def load_code(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Code:
    """Construct a code object from a yaml file.

    :param source: The local yaml source of a code object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: Optional[str]
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Code cannot be successfully validated.
        Details will be provided in the error message.
    :return: Loaded code object.
    :rtype: ~azure.ai.ml.entities._assets._artifacts.code.Code
    """
    return cast(Code, load_common(Code, source, relative_origin, params_override, **kwargs))


def load_compute(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict[str, str]]] = None,
    **kwargs: Any,
) -> Compute:
    """Construct a compute object from a yaml file.

    :param source: The local yaml source of a compute. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: Optional[str]
    :keyword params_override: Optional parameters to override in the loaded yaml.
    :paramtype params_override: Optional[List[Dict[str, str]]
    :return: Loaded compute object.
    :rtype: ~azure.ai.ml.entities.Compute

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START load_compute]
            :end-before: [END load_compute]
            :language: python
            :dedent: 8
            :caption: Loading a Compute object from a YAML file and overriding its description.
    """
    return cast(Compute, load_common(Compute, source, relative_origin, params_override, **kwargs))


def load_component(
    source: Optional[Union[str, PathLike, IO[AnyStr]]] = None,
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Union[CommandComponent, ParallelComponent, PipelineComponent]:
    """Load component from local or remote to a component function.

    :param source: The local yaml source of a component. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: A Component object
    :rtype: Union[CommandComponent, ParallelComponent, PipelineComponent]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_component_configurations.py
            :start-after: [START configure_load_component]
            :end-before: [END configure_load_component]
            :language: python
            :dedent: 8
            :caption: Loading a Component object from a YAML file, overriding its version to "1.0.2", and
                registering it remotely.
    """

    client = kwargs.pop("client", None)
    name = kwargs.pop("name", None)
    version = kwargs.pop("version", None)

    if source:
        component_entity = load_common(Component, source, relative_origin, params_override, **kwargs)
    elif client and name and version:
        component_entity = client.components.get(name, version)
    else:
        msg = "One of (client, name, version), (source) should be provided."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.COMPONENT,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.MISSING_FIELD,
        )
    return cast(Union[CommandComponent, ParallelComponent, PipelineComponent], component_entity)


def load_model(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Model:
    """Constructs a Model object from a YAML file.

    :param source: A path to a local YAML file or an already-open file object containing a job configuration.
        If the source is a path, it will be opened and read. If the source is an open file, the file will be read
        directly.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The root directory for the YAML. This directory will be used as the origin for deducing
        the relative locations of files referenced in the parsed YAML. Defaults to the same directory as source if
        source is a file or file path input. Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: Optional[str]
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Job cannot be successfully validated.
        Details will be provided in the error message.
    :return: A loaded Model object.
    :rtype: ~azure.ai.ml.entities.Model

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START load_model]
            :end-before: [END load_model]
            :language: python
            :dedent: 8
            :caption: Loading a Model from a YAML config file, overriding the name and version parameters.
    """
    return cast(Model, load_common(Model, source, relative_origin, params_override, **kwargs))


def load_data(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Data:
    """Construct a data object from yaml file.

    :param source: The local yaml source of a data object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Data cannot be successfully validated.
        Details will be provided in the error message.
    :return: Constructed Data or DataImport object.
    :rtype: Data
    """
    return cast(Data, load_common(Data, source, relative_origin, params_override, **kwargs))


def load_environment(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Environment:
    """Construct a environment object from yaml file.

    :param source: The local yaml source of an environment. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Environment cannot be successfully validated.
        Details will be provided in the error message.
    :return: Constructed environment object.
    :rtype: Environment
    """
    return cast(Environment, load_common(Environment, source, relative_origin, params_override, **kwargs))


def load_online_deployment(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> OnlineDeployment:
    """Construct a online deployment object from yaml file.

    :param source: The local yaml source of an online deployment object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Online Deployment cannot be successfully validated.
        Details will be provided in the error message.
    :return: Constructed online deployment object.
    :rtype: OnlineDeployment
    """
    return cast(OnlineDeployment, load_common(OnlineDeployment, source, relative_origin, params_override, **kwargs))


def load_batch_deployment(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> BatchDeployment:
    """Construct a batch deployment object from yaml file.

    :param source: The local yaml source of a batch deployment object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Constructed batch deployment object.
    :rtype: BatchDeployment
    """
    return cast(BatchDeployment, load_common(BatchDeployment, source, relative_origin, params_override, **kwargs))


def load_model_batch_deployment(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> ModelBatchDeployment:
    """Construct a model batch deployment object from yaml file.

    :param source: The local yaml source of a batch deployment object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Constructed model batch deployment object.
    :rtype: ModelBatchDeployment
    """
    return cast(
        ModelBatchDeployment, load_common(ModelBatchDeployment, source, relative_origin, params_override, **kwargs)
    )


def load_pipeline_component_batch_deployment(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> PipelineComponentBatchDeployment:
    """Construct a pipeline component batch deployment object from yaml file.

    :param source: The local yaml source of a batch deployment object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Constructed pipeline component batch deployment object.
    :rtype: PipelineComponentBatchDeployment
    """
    return cast(
        PipelineComponentBatchDeployment,
        load_common(PipelineComponentBatchDeployment, source, relative_origin, params_override, **kwargs),
    )


def load_online_endpoint(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> OnlineEndpoint:
    """Construct a online endpoint object from yaml file.

    :param source: The local yaml source of an online endpoint object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Online Endpoint cannot be successfully validated.
        Details will be provided in the error message.
    :return: Constructed online endpoint object.
    :rtype: OnlineEndpoint
    """
    return cast(OnlineEndpoint, load_common(OnlineEndpoint, source, relative_origin, params_override, **kwargs))


def load_batch_endpoint(
    source: Union[str, PathLike, IO[AnyStr]],
    relative_origin: Optional[str] = None,
    *,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> BatchEndpoint:
    """Construct a batch endpoint object from yaml file.

    :param source: The local yaml source of a batch endpoint object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :param relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :type relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Constructed batch endpoint object.
    :rtype: BatchEndpoint
    """
    return cast(BatchEndpoint, load_common(BatchEndpoint, source, relative_origin, params_override, **kwargs))


@experimental
def load_connection(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> WorkspaceConnection:
    """Construct a connection object from yaml file.

    :param source: The local yaml source of a connection object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Constructed connection object.
    :rtype: Connection

    """
    return cast(
        WorkspaceConnection, load_common(WorkspaceConnection, source, relative_origin, params_override, **kwargs)
    )


# Unlike other aspects of connections, this wasn't made experimental, and thus couldn't just be replaced
# During the renaming from 'workspace connection' to just 'connection'.
def load_workspace_connection(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    **kwargs: Any,
) -> WorkspaceConnection:
    """Deprecated - use 'load_connection' instead. Construct a connection object from yaml file.

    :param source: The local yaml source of a connection object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str

    :return: Constructed connection object.
    :rtype: Connection

    """
    warnings.warn(
        "the 'load_workspace_connection' function is deprecated. Use 'load_connection' instead.", DeprecationWarning
    )
    return load_connection(source, relative_origin=relative_origin, **kwargs)


def load_schedule(
    source: Union[str, PathLike, IO[AnyStr]],
    relative_origin: Optional[str] = None,
    *,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> Schedule:
    """Construct a schedule object from yaml file.

    :param source: The local yaml source of a schedule object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :param relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :type relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Constructed schedule object.
    :rtype: Schedule
    """
    return cast(Schedule, load_common(Schedule, source, relative_origin, params_override, **kwargs))


def load_feature_store(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> FeatureStore:
    """Load a feature store object from a yaml file.

    :param source: The local yaml source of a feature store. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :return: Loaded feature store object.
    :rtype: FeatureStore
    """
    return cast(FeatureStore, load_common(FeatureStore, source, relative_origin, params_override, **kwargs))


def load_feature_set(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> FeatureSet:
    """Construct a FeatureSet object from yaml file.

    :param source: The local yaml source of a FeatureSet object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureSet cannot be successfully validated.
        Details will be provided in the error message.
    :return: Constructed FeatureSet object.
    :rtype: FeatureSet
    """
    return cast(FeatureSet, load_common(FeatureSet, source, relative_origin, params_override, **kwargs))


def load_feature_store_entity(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> FeatureStoreEntity:
    """Construct a FeatureStoreEntity object from yaml file.

    :param source: The local yaml source of a FeatureStoreEntity object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureStoreEntity cannot be successfully validated.
        Details will be provided in the error message.
    :return: Constructed FeatureStoreEntity object.
    :rtype: FeatureStoreEntity
    """
    return cast(FeatureStoreEntity, load_common(FeatureStoreEntity, source, relative_origin, params_override, **kwargs))


@experimental
def load_model_package(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> ModelPackage:
    """Constructs a ModelPackage object from a YAML file.

    :param source: A path to a local YAML file or an already-open file object containing a job configuration.
        If the source is a path, it will be opened and read. If the source is an open file, the file will be read
        directly.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The root directory for the YAML. This directory will be used as the origin for deducing
        the relative locations of files referenced in the parsed YAML. Defaults to the same directory as source if
        source is a file or file path input. Defaults to "./" if the source is a stream input with no name value.
    :paramtype relative_origin: Optional[str]
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Job cannot be successfully validated.
        Details will be provided in the error message.
    :return: A loaded ModelPackage object.
    :rtype: ~azure.ai.ml.entities.ModelPackage

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START load_model_package]
            :end-before: [END load_model_package]
            :language: python
            :dedent: 8
            :caption: Loading a ModelPackage from a YAML config file.
    """
    return cast(ModelPackage, load_common(ModelPackage, source, relative_origin, params_override, **kwargs))


def load_feature_set_backfill_request(
    source: Union[str, PathLike, IO[AnyStr]],
    *,
    relative_origin: Optional[str] = None,
    params_override: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> FeatureSetBackfillRequest:
    """Construct a FeatureSetBackfillRequest object from yaml file.

    :param source: The local yaml source of a FeatureSetBackfillRequest object. Must be either a
        path to a local file, or an already-open file.
        If the source is a path, it will be open and read.
        An exception is raised if the file does not exist.
        If the source is an open file, the file will be read directly,
        and an exception is raised if the file is not readable.
    :type source: Union[PathLike, str, io.TextIOWrapper]
    :keyword relative_origin: The origin to be used when deducing
        the relative locations of files referenced in the parsed yaml.
        Defaults to the inputted source's directory if it is a file or file path input.
        Defaults to "./" if the source is a stream input with no name value.
    :type relative_origin: str
    :keyword params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :paramtype params_override: List[Dict]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureSetBackfillRequest
        cannot be successfully validated. Details will be provided in the error message.
    :return: Constructed FeatureSetBackfillRequest object.
    :rtype: FeatureSetBackfillRequest
    """
    return cast(
        FeatureSetBackfillRequest,
        load_common(FeatureSetBackfillRequest, source, relative_origin, params_override, **kwargs),
    )
