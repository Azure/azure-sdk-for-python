# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from marshmallow import ValidationError

from ..exceptions import ValidationException
from . import Component, Job
from ._load_functions import _load_common_raising_marshmallow_error, _try_load_yaml_dict
from ._validation import SchemaValidatableMixin, ValidationResult, _ValidationResultBuilder


def validate_common(cls, path, validate_func, params_override=None) -> ValidationResult:
    params_override = params_override or []
    yaml_dict = _try_load_yaml_dict(path)

    try:
        cls, _ = cls._resolve_cls_and_type(data=yaml_dict, params_override=params_override)

        entity = _load_common_raising_marshmallow_error(
            cls=cls, yaml_dict=yaml_dict, relative_origin=path, params_override=params_override
        )

        if validate_func is not None:
            return validate_func(entity)
        if isinstance(entity, SchemaValidatableMixin):
            return entity._validate()
        return _ValidationResultBuilder.success()
    except ValidationException as err:
        return _ValidationResultBuilder.from_single_message(err.message)
    except ValidationError as err:
        return _ValidationResultBuilder.from_validation_error(err, source_path=path)


def validate_component(path, ml_client=None, params_override=None) -> ValidationResult:
    """Validate a component defined in a local file.

    :param path: The path to the component definition file.
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
        cls=Component,
        path=path,
        validate_func=ml_client.components.validate if ml_client is not None else None,
        params_override=params_override,
    )


def validate_job(path, ml_client=None, params_override=None) -> ValidationResult:
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
