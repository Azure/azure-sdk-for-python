# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import logging
import os
import re
import typing
from abc import abstractmethod
from pathlib import Path
from typing import List


from azure.ai.ml.constants import (
    ARM_ID_PREFIX,
    AZUREML_RESOURCE_PROVIDER,
    BASE_PATH_CONTEXT_KEY,
    CONDA_FILE,
    DOCKER_FILE_NAME,
    FILE_PREFIX,
    LOCAL_COMPUTE_TARGET,
    RESOURCE_ID_FORMAT,
    AzureMLResourceType,
    EXPERIMENTAL_FIELD_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
    REGISTRY_URI_FORMAT,
)

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._utils._arm_id_utils import (
    AMLVersionedArmId,
    is_ARM_id_for_resource,
    parse_name_version,
    parse_name_label,
)

from azure.ai.ml._utils.utils import load_file, load_yaml, is_data_binding_expression, is_valid_node_name
from azure.ai.ml._utils._experimental import _is_warning_cached
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

from marshmallow import RAISE, fields
from marshmallow.exceptions import ValidationError
from marshmallow.fields import Field, Nested, _T
from marshmallow.utils import FieldInstanceResolutionError, resolve_field_instance


module_logger = logging.getLogger(__name__)


class StringTransformedEnum(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allowed_values = kwargs.get("allowed_values", None)
        self.casing_transform = kwargs.get("casing_transform", lambda x: x.lower())
        if isinstance(self.allowed_values, str):
            self.allowed_values = [self.allowed_values]
        self.allowed_values = [self.casing_transform(x) for x in self.allowed_values]

    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "enum": self.allowed_values}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return
        if isinstance(value, str) and self.casing_transform(value) in self.allowed_values:
            return self.casing_transform(value)
        else:
            raise ValidationError(f"Value {value} passed is not in set {self.allowed_values}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and self.casing_transform(value) in self.allowed_values:
            return self.casing_transform(value)
        raise ValidationError(f"Value {value} passed is not in set {self.allowed_values}")


class DataBindingStr(Field):
    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "pattern": r"\$\{\{\s*(\S*)\s*\}\}"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        from azure.ai.ml.entities._job.pipeline._io import InputOutputBase

        if isinstance(value, InputOutputBase):
            value = str(value)
        elif not isinstance(value, str):
            raise ValidationError(f"Value {value} passed is neither a string nor an InputOutputBase")

        if is_data_binding_expression(value, is_singular=False):
            return value
        else:
            raise ValidationError(f"Value passed is not a data binding string: {value}")

    def _deserialize(self, value, attr, data, **kwargs):
        if is_data_binding_expression(value, is_singular=False):
            return value
        else:
            raise ValidationError(f"Value passed is not a data binding string: {type(value)}: {value}")


class ArmStr(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.azureml_type = kwargs.get("azureml_type", None)

    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "pattern": "^azureml:.*", "arm_type": self.azureml_type}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        # TODO: (1795017) Improve pre-serialization checks
        if isinstance(value, str):
            return f"{ARM_ID_PREFIX}{value}"
        elif value is None and not self.required:
            return None
        else:
            raise ValidationError(f"Non-string passed to ArmStr for {attr}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and value.startswith(ARM_ID_PREFIX):
            name = value[len(ARM_ID_PREFIX) :]
            return name
        else:
            raise ValidationError(
                f"In order to specify an existing {self.azureml_type}, please provide either of the following prefixed with 'azureml:':\n"
                "1. The full ARM ID for the resource, e.g."
                f"azureml:{RESOURCE_ID_FORMAT.format('<subscription_id>', '<resource_group>', AZUREML_RESOURCE_PROVIDER, '<workspace_name>/') + self.azureml_type +'/<resource_name>/<version-if applicable>)'}\n"
                "2. The short-hand name of the resource registered in the workspace, eg: azureml:<short-hand-name>:<version-if applicable>. For example, version 1 of the environment registered as 'my-env' in the workspace can be referenced as 'azureml:my-env:1'"
            )


class ArmVersionedStr(ArmStr):
    def __init__(self, **kwargs):
        self.allow_default_version = kwargs.pop("allow_default_version", False)
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str) and value.startswith(ARM_ID_PREFIX):
            return value
        else:
            return super()._serialize(value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        arm_id = super()._deserialize(value, attr, data, **kwargs)
        try:
            AMLVersionedArmId(arm_id)
            return arm_id
        except ValidationException:
            pass

        if is_ARM_id_for_resource(name=arm_id, resource_type=self.azureml_type):
            msg = "id for {} is invalid"
            raise ValidationError(message=msg.format(attr))

        try:
            name, label = parse_name_label(arm_id)
        except ValidationException as e:
            # Schema will try to deserialize the value with all possible Schema & catch ValidationError
            # So raise ValidationError instead of ValidationException
            raise ValidationError(e.message)

        version = None
        if not label:
            name, version = parse_name_version(arm_id)

        if not (label or version):
            if self.allow_default_version:
                return name
            raise ValidationError(f"Either version or label is not provided for {attr} or the id is not valid.")

        if version:
            return f"{name}:{version}"
        else:
            return f"{name}@{label}"


class FileRefField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _jsonschema_type_mapping(self):
        schema = {"type": "string"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and not value.startswith(FILE_PREFIX):
            base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])
            path = Path(value)
            if not path.is_absolute():
                path = base_path / path
                path.resolve()
            data = load_file(path)
            return data
        else:
            raise ValidationError(f"Not supporting non file for {attr}")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        raise ValidationError("Serialize on FileRefField is not supported.")


class RefField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _jsonschema_type_mapping(self):
        schema = {"type": "string"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and (
            value.startswith(FILE_PREFIX)
            or (os.path.isdir(value) or os.path.isfile(value))
            or value == DOCKER_FILE_NAME
        ):  # "Dockerfile" w/o file: prefix doesn't register as a path
            if value.startswith(FILE_PREFIX):
                value = value[len(FILE_PREFIX) :]
            base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])

            path = Path(value)
            if not path.is_absolute():
                path = base_path / path
                path.resolve()
            if attr == CONDA_FILE:  # conda files should be loaded as dictionaries
                data = load_yaml(path)
            else:
                data = load_file(path)
            return data
        else:
            raise ValidationError(f"Not supporting non file for {attr}")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        raise ValidationError("Serialize on RefField is not supported.")


class NestedField(Nested):
    """
    anticipates the default coming in next marshmallow version, unknown=True.
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get("unknown") is None:
            kwargs["unknown"] = RAISE
        super().__init__(*args, **kwargs)


class UnionField(fields.Field):
    def __init__(self, union_fields: List[fields.Field], **kwargs):
        super().__init__(**kwargs)
        try:
            # add the validation and make sure union_fields must be subclasses or instances of
            # marshmallow.base.FieldABC
            self._union_fields = [resolve_field_instance(cls_or_instance) for cls_or_instance in union_fields]
        except FieldInstanceResolutionError as error:
            raise ValueError(
                'Elements of "union_fields" must be subclasses or ' "instances of marshmallow.base.FieldABC."
            ) from error

    @property
    def union_fields(self):
        return self._union_fields

    # This sets the parent for the schema and also handles nesting.
    def _bind_to_schema(self, field_name, schema):
        super()._bind_to_schema(field_name, schema)
        new_union_fields = []
        for field in self._union_fields:
            field = copy.deepcopy(field)
            field._bind_to_schema(field_name, self)
            new_union_fields.append(field)

        self._union_fields = new_union_fields

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        errors = []
        for field in self._union_fields:
            try:
                return field._serialize(value, attr, obj, **kwargs)

            except ValidationError as e:
                errors.extend(e.messages)
            except (TypeError, ValueError, AttributeError, ValidationException) as e:
                errors.extend([str(e)])
        raise ValidationError(message=errors, field_name=attr)

    def _deserialize(self, value, attr, data, **kwargs):
        errors = []
        for schema in self._union_fields:
            try:
                return schema.deserialize(value, attr, data, **kwargs)
            except ValidationError as e:
                # Revert base path to original path when job schema fail to deserialize job. For example, when load
                # parallel job with component file reference starting with FILE prefex, maybe first CommandSchema will
                # load component yaml according to AnonymousCommandComponentSchema, and YamlFileSchema will update base
                # path. When CommandSchema fail to load, then Parallelschema will load component yaml according to
                # AnonymousParallelComponentSchema, but base path now is incorrect, and will raise path not found error
                # when load component yaml file.
                if (
                    hasattr(schema, "name")
                    and schema.name == "jobs"
                    and hasattr(schema, "schema")
                    and isinstance(schema.schema, PathAwareSchema)
                ):
                    # use old base path to recover original base path
                    schema.schema.context[BASE_PATH_CONTEXT_KEY] = schema.schema.old_base_path
                    # recover base path of parent schema
                    schema.context[BASE_PATH_CONTEXT_KEY] = schema.schema.context[BASE_PATH_CONTEXT_KEY]
                errors.append(e.normalized_messages())
        raise ValidationError(errors, field_name=attr)


def ComputeField(**kwargs):
    """
    :param required : if set to True, it is not possible to pass None
    :type required: bool
    """
    return UnionField(
        [
            StringTransformedEnum(allowed_values=[LOCAL_COMPUTE_TARGET]),
            ArmStr(azureml_type=AzureMLResourceType.COMPUTE),
            # Case for virtual clusters
            fields.Str(),
        ],
        metadata={"description": "The compute resource."},
        **kwargs,
    )


class VersionField(Field):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _jsonschema_type_mapping(self):
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _deserialize(self, value, attr, data, **kwargs) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            raise Exception(f"Type {type(value)} is not supported for version.")


class DumpableIntegerField(fields.Integer):
    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[typing.Union[str, _T]]:
        if self.strict and not isinstance(value, int):
            raise ValidationError("Given value is not an integer")
        return super()._serialize(value, attr, obj, **kwargs)


class DumpableStringField(fields.String):
    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[typing.Union[str, _T]]:
        if not isinstance(value, str):
            raise ValidationError("Given value is not a string")
        return super()._serialize(value, attr, obj, **kwargs)


class ExperimentalField(fields.Field):
    def __init__(self, experimental_field: fields.Field, **kwargs):
        super().__init__(**kwargs)
        try:
            self._experimental_field = resolve_field_instance(experimental_field)
            self.required = experimental_field.required
        except FieldInstanceResolutionError as error:
            raise ValueError(
                '"experimental_field" must be subclasses or ' "instances of marshmallow.base.FieldABC."
            ) from error

    # This sets the parent for the schema and also handles nesting.
    def _bind_to_schema(self, field_name, schema):
        super()._bind_to_schema(field_name, schema)
        self._experimental_field._bind_to_schema(field_name, schema)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return self._experimental_field._serialize(value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is not None:
            message = "Field '{0}': {1} {2}".format(attr, EXPERIMENTAL_FIELD_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
            if not _is_warning_cached(message):
                module_logger.warning(message)

        return self._experimental_field._deserialize(value, attr, data, **kwargs)


class RegistryStr(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.azureml_type = kwargs.get("azureml_type", None)

    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "pattern": "^azureml://registries/.*", "arm_type": self.azureml_type}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str) and value.startswith(REGISTRY_URI_FORMAT):
            return f"{value}"
        elif value is None and not self.required:
            return None
        else:
            raise ValidationError(f"Non-string passed to RegistryStr for {attr}")

    def _deserialize(self, value, attr, data, **kwargse):
        if isinstance(value, str) and value.startswith(REGISTRY_URI_FORMAT):
            name = value
            return name
        else:
            raise ValidationError(
                f"In order to specify an existing {self.azureml_type}, please provide the correct registry path prefixed with 'azureml://':\n"
            )


class PythonFuncNameStr(fields.Str):
    @abstractmethod
    def _get_field_name(self) -> str:
        """Returns field name, used for error message."""
        pass

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        """Validate component name"""
        name = super()._deserialize(value, attr, data, **kwargs)
        pattern = r"^[a-z][a-z\d_]*$"
        if not re.match(pattern, name):
            raise ValidationError(
                f"{self._get_field_name()} name should only contain lower letter, number, underscore and start with a lower letter. Currently got {name}."
            )
        return name


class PipelineNodeNameStr(fields.Str):
    @abstractmethod
    def _get_field_name(self) -> str:
        """Returns field name, used for error message."""
        pass

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        """Validate component name"""
        name = super()._deserialize(value, attr, data, **kwargs)
        if not is_valid_node_name(name):
            raise ValidationError(
                f"{self._get_field_name()} name should be a valid python identifier(lower letters, numbers, underscore and start with a letter or underscore). Currently got {name}."
            )
        return name
