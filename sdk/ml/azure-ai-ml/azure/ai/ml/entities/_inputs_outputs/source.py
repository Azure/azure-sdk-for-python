# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin
# disable redefined-builtin to use type/min/max as argument name

from inspect import Parameter
from typing import Dict, Optional, overload, List

from typing_extensions import Literal

from azure.ai.ml.constants._component import ExternalDataType
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from .utils import _get_param_with_standard_annotation, _remove_empty_values


class Source(DictMixin, RestTranslatableMixin):  # pylint: disable=too-many-instance-attributes
    """Define an source of a DataTransfer Component or Job.


    :param type: The type of the data input. Possible values include: 'file_system', 'database'.
    :type type: str
    :param path: The path to which the input is pointing. Could be pointing to the path of file system.
    :type path: str
    :param query: The sql query to get data from database
    :type default: str
    :param stored_procedure: stored_procedure
    :type stored_procedure: str
    :param stored_procedure_params: stored_procedure_params
    :type stored_procedure_params: List[dict]
    :param connection: Connection is workspace, we didn't support storage connection here, need leverage workspace
    connection to store these credential info.
    :type connection: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Source cannot be successfully validated.
        Details will be provided in the error message.
    """

    _EMPTY = Parameter.empty

    @overload
    def __init__(
        self,
        *,
        type: Literal["file_system"] = "file_system",
        path: Optional[str] = None,
        connection: Optional[str] = None,
        **kwargs,
    ):
        """Initialize an input.

        :param type: The type of the data input. Can only be set to "file_system".
        :type type: str
        :param path: The path to which the input is pointing. Could be pointing to the path of file system.
        :type path: str
        :param connection: Connection is workspace, we didn't support storage connection here, need leverage workspace
        connection to store these credential info.
        :type connection: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Source cannot be successfully validated.
            Details will be provided in the error message.
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["database"] = "database",
        query: Optional[str] = None,
        stored_procedure: Optional[str] = None,
        stored_procedure_params: Optional[List[dict]] = None,
        connection: Optional[str] = None,
        **kwargs,
    ):
        """Initialize a bool input.

        :param type: The type of the data input. Can only be set to "database".
        :type type: str
        :param query: The sql query to get data from database
        :type default: str
        :param stored_procedure: stored_procedure
        :type stored_procedure: str
        :param stored_procedure_params: stored_procedure_params
        :type stored_procedure_params: List[dict]
        :param connection: Connection is workspace, we didn't support storage connection here, need leverage workspace
        connection to store these credential info.
        :type connection: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Source cannot be successfully validated.
            Details will be provided in the error message.
        """

    def __init__(
        self,
        *,
        type: str,
        path: Optional[str] = None,
        query: Optional[str] = None,
        stored_procedure: Optional[str] = None,
        stored_procedure_params: Optional[List[dict]] = None,
        connection: Optional[str] = None,
        **kwargs,
    ):
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.type = type
        self.name = None

        if path is not None and not isinstance(path, str):
            # this logic will make dsl data binding expression working in the same way as yaml
            # it's written to handle InputOutputBase, but there will be loop import if we import InputOutputBase here
            self.path = str(path)
        else:
            self.path = path
        self.query = query
        self.stored_procedure = stored_procedure
        self.stored_procedure_params = stored_procedure_params
        self.connection = connection

        self._validate_parameter_combinations()

    def _to_dict(self, remove_name=True):
        """Convert the Source object to a dict."""
        keys = ["name", "path", "type", "query", "stored_procedure", "stored_procedure_params", "connection"]
        if remove_name:
            keys.remove("name")
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)

    def _update_name(self, name):
        self.name = name

    def _validate_parameter_combinations(self):
        """Validate different parameter combinations according to type."""
        parameters = ["path", "type", "query", "stored_procedure", "stored_procedure_params", "connection"]
        parameters = {key: getattr(self, key, None) for key in parameters}
        type = parameters.pop("type")

        # validate parameter combination
        if type in ExternalDataType.EXTERNAL_DATA_TYPE_COMBINATION:
            valid_parameters = ExternalDataType.EXTERNAL_DATA_TYPE_COMBINATION[type]
            for key, value in parameters.items():
                if key not in valid_parameters and value is not None:
                    msg = "Invalid parameter for '{}' Source, parameter '{}' should be None but got '{}'"
                    raise ValidationException(
                        message=msg.format(type, key, value),
                        no_personal_data_message=msg.format("[type]", "[parameter]", "[parameter_value]"),
                        error_category=ErrorCategory.USER_ERROR,
                        target=ErrorTarget.PIPELINE,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )

    @classmethod
    def _get_param_with_standard_annotation(cls, func):
        # todo: update
        return _get_param_with_standard_annotation(func, is_func=True)

    def _to_rest_object(self) -> Dict:
        # this is for component rest object when using Source as component inputs, as for job input usage,
        # rest object is generated by extracting Source's properties, see details in to_rest_dataset_literal_inputs()
        result = self._to_dict()
        return result

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "Source":
        # this is for component rest object when using Source as component inputs
        return Source(**obj)
