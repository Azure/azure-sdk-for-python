# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from os import PathLike
from typing import IO, Any, AnyStr, Callable, Dict, List, Optional, Union, cast

from marshmallow import ValidationError

from azure.ai.ml import MLClient

from ..exceptions import ValidationException
from . import Component, Job
from ._load_functions import _load_common_raising_marshmallow_error, _try_load_yaml_dict
from ._validation import PathAwareSchemaValidatableMixin, ValidationResult, ValidationResultBuilder


def validate_common(
    cls: Any,
    path: Union[str, PathLike, IO[AnyStr]],
    validate_func: Callable,
    params_override: Optional[List[Dict]] = None,
) -> ValidationResult:
    params_override = params_override or []
    yaml_dict = _try_load_yaml_dict(path)

    try:
        cls, _ = cls._resolve_cls_and_type(data=yaml_dict, params_override=params_override)

        entity = _load_common_raising_marshmallow_error(
            cls=cls, yaml_dict=yaml_dict, relative_origin=path, params_override=params_override
        )

        if validate_func is not None:
            res = cast(ValidationResult, validate_func(entity))
            return res
        if isinstance(entity, PathAwareSchemaValidatableMixin):
            return entity._validate()
        return ValidationResultBuilder.success()
    except ValidationException as err:
        return ValidationResultBuilder.from_single_message(err.message)
    except ValidationError as err:
        return ValidationResultBuilder.from_validation_error(err, source_path=path)


def validate_component(
    path: Union[str, PathLike, IO[AnyStr]],
    ml_client: Optional[MLClient] = None,
    params_override: Optional[List[Dict]] = None,
) -> ValidationResult:
    """Validate a component defined in a local file.

    :param path: The path to the component definition file.
    :type path: Union[str, PathLike, IO[AnyStr]]
    :param ml_client: The client to use for validation. Will skip remote validation if None.
    :type ml_client: azure.ai.ml.core.AzureMLComputeClient
    :param params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]
    :return: The validation result.
    :rtype: ValidationResult
    """
    return validate_common(
        cls=Component,
        path=path,
        validate_func=ml_client.components.validate if ml_client is not None else None,
        params_override=params_override,
    )


def validate_job(
    path: Union[str, PathLike, IO[AnyStr]],
    ml_client: Optional[MLClient] = None,
    params_override: Optional[List[Dict]] = None,
) -> ValidationResult:
    """Validate a job defined in a local file.

    :param path: The path to the job definition file.
    :type path: str
    :param ml_client: The client to use for validation. Will skip remote validation if None.
    :type ml_client: azure.ai.ml.core.AzureMLComputeClient
    :param params_override: Fields to overwrite on top of the yaml file.
        Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]
    :return: The validation result.
    :rtype: ValidationResult
    """
    return validate_common(
        cls=Job,
        path=path,
        validate_func=ml_client.jobs.validate if ml_client is not None else None,
        params_override=params_override,
    )
