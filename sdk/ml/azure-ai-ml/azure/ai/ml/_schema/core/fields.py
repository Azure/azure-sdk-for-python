# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

import copy
import logging
import os
import re
import typing
from abc import abstractmethod
from pathlib import Path
from typing import List

from marshmallow import RAISE, fields
from marshmallow.exceptions import ValidationError
from marshmallow.fields import _T, Field, Nested
from marshmallow.utils import FieldInstanceResolutionError, from_iso_datetime, resolve_field_instance

from azure.ai.ml._ml_exceptions import ValidationException
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._utils._arm_id_utils import (
    AMLVersionedArmId,
    is_ARM_id_for_resource,
    parse_name_label,
    parse_name_version,
)
from azure.ai.ml._utils._experimental import _is_warning_cached
from azure.ai.ml._utils.utils import is_data_binding_expression, is_valid_node_name, load_file, load_yaml
from azure.ai.ml.constants import (
    ARM_ID_PREFIX,
    AZUREML_RESOURCE_PROVIDER,
    BASE_PATH_CONTEXT_KEY,
    CONDA_FILE,
    DOCKER_FILE_NAME,
    EXPERIMENTAL_FIELD_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
    FILE_PREFIX,
    LOCAL_COMPUTE_TARGET,
    REGISTRY_URI_FORMAT,
    RESOURCE_ID_FORMAT,
    AzureMLResourceType,
)
from azure.ai.ml.entities._job.pipeline._attr_dict import try_get_non_arbitrary_attr_for_potential_attr_dict

module_logger = logging.getLogger(__name__)


class StringTransformedEnum(Field):
    def __init__(self, **kwargs):
        # pop marshmallow unknown args to avoid warnings
        self.allowed_values = kwargs.pop("allowed_values", None)
        self.casing_transform = kwargs.pop("casing_transform", lambda x: x.lower())
        super().__init__(**kwargs)
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
        raise ValidationError(f"Value {value} passed is not in set {self.allowed_values}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and self.casing_transform(value) in self.allowed_values:
            return self.casing_transform(value)
        raise ValidationError(f"Value {value} passed is not in set {self.allowed_values}")


class LocalPathField(fields.Str):
    """A field that validates that the input is a local path.

    Can only be used as fields of PathAwareSchema.
    """

    def __init__(self, allow_dir=True, allow_file=True):
        self._allow_dir = allow_dir
        self._allow_file = allow_file
        super().__init__()

    def _jsonschema_type_mapping(self):
        schema = {"type": "string"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is None:
            return None
        self._validate(value)
        return super(LocalPathField, self)._serialize(value, attr, obj, **kwargs)

    def _validate(self, value):
        try:
            path = Path(value)
            base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])
            if not path.is_absolute():
                path = base_path / path
                path.resolve()
            if (self._allow_dir and path.is_dir()) or (self._allow_file and path.is_file()):
                return super(LocalPathField, self)._validate(value)
        except OSError:
            pass
        if self._allow_dir and self._allow_file:
            raise ValidationError(f"{value} is not a valid path")
        elif self._allow_dir:
            raise ValidationError(f"{value} is not a valid directory")
        raise ValidationError(f"{value} is not a valid file")


class SerializeValidatedUrl(fields.Url):
    """This field will validate if value is an url during serialization, so
    that only valid urls can be serialized as this schema.

    Use this schema instead of fields.Url when unioned with ArmStr or
    its subclasses like ArmVersionedStr, so that the field can be
    serialized correctly after deserialization. azureml:xxx => xxx =>
    azureml:xxx e.g. The field will still always be serializable as any
    string can be serialized as an ArmStr.
    """

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is None:
            return None
        self._validate(value)
        return super(SerializeValidatedUrl, self)._serialize(value, attr, obj, **kwargs)


class DataBindingStr(fields.Str):
    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "pattern": r"\$\{\{\s*(\S*)\s*\}\}"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        # None value handling logic is inside _serialize but outside _validate/_deserialize
        if value is None:
            return None

        from azure.ai.ml.entities._job.pipeline._io import InputOutputBase

        if isinstance(value, InputOutputBase):
            value = str(value)

        self._validate(value)
        return super(DataBindingStr, self)._serialize(value, attr, obj, **kwargs)

    def _validate(self, value):
        if is_data_binding_expression(value, is_singular=False):
            return super(DataBindingStr, self)._validate(value)
        raise ValidationError(f"Value passed is not a data binding string: {value}")


class DateTimeStr(fields.Str):
    def _jsonschema_type_mapping(self):
        schema = {"type": "string"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        self._validate(value)
        return super(DateTimeStr, self)._serialize(value, attr, obj, **kwargs)

    def _validate(self, value):
        try:
            from_iso_datetime(value)
        except Exception:
            raise ValidationError(f"Not a valid ISO8601-formatted datetime string: {value}")


class ArmStr(Field):
    def __init__(self, **kwargs):
        self.azureml_type = kwargs.pop("azureml_type", None)
        self.pattern = kwargs.pop("pattern", "^azureml:.*")
        super().__init__(**kwargs)

    def _jsonschema_type_mapping(self):
        schema = {
            "type": "string",
            "pattern": "^azureml:.*",
            "arm_type": self.azureml_type,
        }
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        # TODO: (1795017) Improve pre-serialization checks
        if isinstance(value, str):
            return f"{ARM_ID_PREFIX}{value}"
        if value is None and not self.required:
            return None
        raise ValidationError(f"Non-string passed to ArmStr for {attr}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and value.startswith(ARM_ID_PREFIX):
            name = value[len(ARM_ID_PREFIX) :]
            return name
        raise ValidationError(
            f"In order to specify an existing {self.azureml_type if self.azureml_type is not None else 'asset'}, please provide either of the following prefixed with 'azureml:':\n"
            "1. The full ARM ID for the resource, e.g."
            f"azureml:{RESOURCE_ID_FORMAT.format('<subscription_id>', '<resource_group>', AZUREML_RESOURCE_PROVIDER, '<workspace_name>/') + self.azureml_type if self.azureml_type is not None else '<asset_type>' +'/<resource_name>/<version-if applicable>)'}\n"
            "2. The short-hand name of the resource registered in the workspace, eg: azureml:<short-hand-name>:<version-if applicable>. For example, version 1 of the environment registered as 'my-env' in the workspace can be referenced as 'azureml:my-env:1'"
        )


class ArmVersionedStr(ArmStr):
    def __init__(self, **kwargs):
        self.allow_default_version = kwargs.pop("allow_default_version", False)
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str) and value.startswith(ARM_ID_PREFIX):
            return value
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
        raise ValidationError(f"Not supporting non file for {attr}")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        raise ValidationError("Serialize on RefField is not supported.")


class NestedField(Nested):
    """anticipates the default coming in next marshmallow version,
    unknown=True."""

    def __init__(self, *args, **kwargs):
        if kwargs.get("unknown") is None:
            kwargs["unknown"] = RAISE
        super().__init__(*args, **kwargs)


class UnionField(fields.Field):
    def __init__(self, union_fields: List[fields.Field], is_strict=False, **kwargs):
        super().__init__(**kwargs)
        try:
            # add the validation and make sure union_fields must be subclasses or instances of
            # marshmallow.base.FieldABC
            self._union_fields = [resolve_field_instance(cls_or_instance) for cls_or_instance in union_fields]
            self.is_strict = is_strict  # S\When True, combine fields with oneOf instead of anyOf at schema generation
        except FieldInstanceResolutionError as error:
            raise ValueError(
                'Elements of "union_fields" must be subclasses or ' "instances of marshmallow.base.FieldABC."
            ) from error

    @property
    def union_fields(self):
        return iter(self._union_fields)

    def insert_union_field(self, field):
        self._union_fields.insert(0, field)

    # This sets the parent for the schema and also handles nesting.
    def _bind_to_schema(self, field_name, schema):
        super()._bind_to_schema(field_name, schema)
        self._union_fields = self._create_bind_fields(self._union_fields, field_name)

    def _create_bind_fields(self, _fields, field_name):
        new_union_fields = []
        for field in _fields:
            field = copy.deepcopy(field)
            field._bind_to_schema(field_name, self)
            new_union_fields.append(field)
        return new_union_fields

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
                errors.append(e.normalized_messages())
            except (ValidationException, FileNotFoundError, TypeError) as e:
                errors.append([str(e)])
            finally:
                # Revert base path to original path when job schema fail to deserialize job. For example, when load
                # parallel job with component file reference starting with FILE prefix, maybe first CommandSchema will
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
        raise ValidationError(errors, field_name=attr)


class TypeSensitiveUnionField(UnionField):
    """Union field which will try to simplify error messages based on type
    field in failed serialization/deserialization.

    If value doesn't have type, will skip error messages from fields
    with type field If value has type & its type doesn't match any
    allowed types, raise "Value {} not in set {}" If value has type &
    its type matches at least 1 allowed value, it will raise the first
    matched error.
    """

    def __init__(
        self,
        type_sensitive_fields_dict: typing.Dict[str, List[fields.Field]],
        *,
        plain_union_fields: List[fields.Field] = None,
        allow_load_from_file: bool = True,
        type_field_name="type",
        **kwargs,
    ):
        """param type_sensitive_fields_dict: a dict of type name to list of
        type sensitive fields param plain_union_fields: list of fields that
        will be used if value doesn't have type field type plain_union_fields:
        List[fields.Field] param allow_load_from_file: whether to allow load
        from file, default to True type allow_load_from_file: bool param
        type_field_name: field name of type field, default value is "type" type
        type_field_name: str."""
        self._type_sensitive_fields_dict = {}
        self._allow_load_from_yaml = allow_load_from_file

        union_fields = plain_union_fields or []
        for type_name, type_sensitive_fields in type_sensitive_fields_dict.items():
            union_fields.extend(type_sensitive_fields)
            self._type_sensitive_fields_dict[type_name] = [
                resolve_field_instance(cls_or_instance) for cls_or_instance in type_sensitive_fields
            ]

        super(TypeSensitiveUnionField, self).__init__(union_fields, **kwargs)
        self._type_field_name = type_field_name

    def _bind_to_schema(self, field_name, schema):
        super()._bind_to_schema(field_name, schema)
        for (
            type_name,
            type_sensitive_fields,
        ) in self._type_sensitive_fields_dict.items():
            self._type_sensitive_fields_dict[type_name] = self._create_bind_fields(type_sensitive_fields, field_name)

    @property
    def type_field_name(self) -> str:
        return self._type_field_name

    @property
    def allowed_types(self) -> List[str]:
        return list(self._type_sensitive_fields_dict.keys())

    def insert_type_sensitive_field(self, type_name, field):
        """Insert a new type sensitive field for a specific type."""
        if type_name not in self._type_sensitive_fields_dict:
            self._type_sensitive_fields_dict[type_name] = []
        self._type_sensitive_fields_dict[type_name].insert(0, field)
        self.insert_union_field(field)

    def _raise_simplified_error_base_on_type(self, e, value, attr):
        """If value doesn't have type, raise original error; If value has type
        & its type doesn't match any allowed types, raise "Value {} not in set
        {}"; If value has type & its type matches at least 1 field, return the
        first matched error message;"""
        value_type = try_get_non_arbitrary_attr_for_potential_attr_dict(value, self.type_field_name)
        if value_type is None:
            # if value has no type field, raise original error
            raise e
        if value_type not in self.allowed_types:
            # if value has type field but its value doesn't match any allowed value, raise ValidationError directly
            raise ValidationError(
                message={self.type_field_name: f"Value {value_type} passed is not in set {self.allowed_types}"},
                field_name=attr,
            )
        # if value has type field and its value match at least 1 allowed value, raise first matched
        for error in e.messages:
            # for non-nested schema, their error message will be {"_schema": ["xxx"]}
            if len(error) == 1 and "_schema" in error:
                continue
            # for nested schema, type field won't be within error only if type field value is matched
            # then return first matched error message
            if self.type_field_name not in error:
                raise ValidationError(message=error, field_name=attr)
        # shouldn't reach here
        raise e

    def _serialize(self, value, attr, obj, **kwargs):
        union_fields = self._union_fields[:]
        value_type = try_get_non_arbitrary_attr_for_potential_attr_dict(value, self.type_field_name)
        if value_type is not None and value_type in self.allowed_types:
            target_fields = self._type_sensitive_fields_dict[value_type]
            if len(target_fields) == 1:
                return target_fields[0]._serialize(value, attr, obj, **kwargs)
            self._union_fields = target_fields

        try:
            return super(TypeSensitiveUnionField, self)._serialize(value, attr, obj, **kwargs)
        except ValidationError as e:
            self._raise_simplified_error_base_on_type(e, value, attr)
        finally:
            self._union_fields = union_fields

    def _try_load_from_yaml(self, value):
        target_path = value
        if target_path.startswith(FILE_PREFIX):
            target_path = target_path[len(FILE_PREFIX) :]
        try:
            import yaml

            base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])
            target_path = Path(target_path)
            if not target_path.is_absolute():
                target_path = base_path / target_path
                target_path.resolve()
            if target_path.is_file():
                self.context[BASE_PATH_CONTEXT_KEY] = target_path.parent
                with target_path.open() as f:
                    return yaml.safe_load(f)
        except Exception:
            pass
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return super(TypeSensitiveUnionField, self)._deserialize(value, attr, data, **kwargs)
        except ValidationError as e:
            if isinstance(value, str) and self._allow_load_from_yaml:
                value = self._try_load_from_yaml(value)
            self._raise_simplified_error_base_on_type(e, value, attr)


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
        if isinstance(value, (int, float)):
            return str(value)
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
        self.azureml_type = kwargs.pop("azureml_type", None)
        super().__init__(**kwargs)

    def _jsonschema_type_mapping(self):
        schema = {
            "type": "string",
            "pattern": "^azureml://registries/.*",
            "arm_type": self.azureml_type,
        }
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str) and value.startswith(REGISTRY_URI_FORMAT):
            return f"{value}"
        if value is None and not self.required:
            return None
        raise ValidationError(f"Non-string passed to RegistryStr for {attr}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and value.startswith(REGISTRY_URI_FORMAT):
            return value
        raise ValidationError(
            f"In order to specify an existing {self.azureml_type}, please provide the correct registry path prefixed with 'azureml://':\n"
        )


class PythonFuncNameStr(fields.Str):
    @abstractmethod
    def _get_field_name(self) -> str:
        """Returns field name, used for error message."""

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        """Validate component name."""
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

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        """Validate component name."""
        name = super()._deserialize(value, attr, data, **kwargs)
        if not is_valid_node_name(name):
            raise ValidationError(
                f"{self._get_field_name()} name should be a valid python identifier(lower letters, numbers, underscore and start with a letter or underscore). Currently got {name}."
            )
        return name


class GitStr(fields.Str):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "pattern": "^git+"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str) and value.startswith("git+"):
            return f"{value}"
        if value is None and not self.required:
            return None
        raise ValidationError(f"Non-string passed to GitStr for {attr}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and value.startswith("git+"):
            return value
        raise ValidationError("In order to specify a git path, please provide the correct path prefixed with 'git+\n")
