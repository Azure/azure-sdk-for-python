# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access,no-member

from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_load, validates, ValidationError

from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.component.input_output import InputPortSchema
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import FileRefField, StringTransformedEnum, NestedField
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from azure.ai.ml.constants._component import (
    ComponentSource,
    NodeType,
    DataTransferTaskType,
    DataCopyMode,
    ExternalDataType,
)


class DataTransferComponentSchemaMixin(ComponentSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.DATA_TRANSFER])


class DataTransferCopyComponentSchema(DataTransferComponentSchemaMixin):
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.COPY_DATA], required=True)
    data_copy_mode = StringTransformedEnum(
        allowed_values=[DataCopyMode.MERGE_WITH_OVERWRITE, DataCopyMode.FAIL_IF_CONFLICT]
    )
    inputs = fields.Dict(
        keys=fields.Str(),
        values=NestedField(InputPortSchema),
    )

    @validates("outputs")
    def outputs_key(self, value):
        outputs_count = len(value)
        if outputs_count != 1:
            msg = "Only support single output in {}, but there're {} outputs."
            raise ValidationError(
                message=msg.format(DataTransferTaskType.COPY_DATA, outputs_count), field_name="outputs"
            )


class SinkSourceSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[ExternalDataType.FILE_SYSTEM, ExternalDataType.DATABASE], required=True
    )


class SourceInputsSchema(metaclass=PatchedSchemaMeta):
    """
    For export task in DataTransfer, inputs type only support uri_file for database and uri_folder for filesystem.
    """

    type = StringTransformedEnum(allowed_values=[AssetTypes.URI_FOLDER, AssetTypes.URI_FILE], required=True)


class SinkOutputsSchema(metaclass=PatchedSchemaMeta):
    """
    For import task in DataTransfer, outputs type only support mltable for database and uri_folder for filesystem;
    """

    type = StringTransformedEnum(allowed_values=[AssetTypes.MLTABLE, AssetTypes.URI_FOLDER], required=True)


class DataTransferImportComponentSchema(DataTransferComponentSchemaMixin):
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.IMPORT_DATA], required=True)
    source = NestedField(SinkSourceSchema, required=True)
    outputs = fields.Dict(
        keys=fields.Str(),
        values=NestedField(SinkOutputsSchema),
    )

    @validates("inputs")
    def inputs_key(self, value):
        raise ValidationError(f"inputs field is not a valid filed in task type " f"{DataTransferTaskType.IMPORT_DATA}.")

    @validates("outputs")
    def outputs_key(self, value):
        if len(value) != 1 or value and list(value.keys())[0] != "sink":
            raise ValidationError(
                f"outputs field only support one output called sink in task type "
                f"{DataTransferTaskType.IMPORT_DATA}."
            )


class DataTransferExportComponentSchema(DataTransferComponentSchemaMixin):
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.EXPORT_DATA], required=True)
    inputs = fields.Dict(
        keys=fields.Str(),
        values=NestedField(SourceInputsSchema),
    )
    sink = NestedField(SinkSourceSchema(), required=True)

    @validates("inputs")
    def inputs_key(self, value):
        if len(value) != 1 or value and list(value.keys())[0] != "source":
            raise ValidationError(
                f"inputs field only support one input called source in task type "
                f"{DataTransferTaskType.EXPORT_DATA}."
            )

    @validates("outputs")
    def outputs_key(self, value):
        raise ValidationError(
            f"outputs field is not a valid filed in task type " f"{DataTransferTaskType.EXPORT_DATA}."
        )


class RestDataTransferCopyComponentSchema(DataTransferCopyComponentSchema):
    """When component load from rest, won't validate on name since there might
    be existing component with invalid name."""

    name = fields.Str(required=True)


class RestDataTransferImportComponentSchema(DataTransferImportComponentSchema):
    """When component load from rest, won't validate on name since there might
    be existing component with invalid name."""

    name = fields.Str(required=True)


class RestDataTransferExportComponentSchema(DataTransferExportComponentSchema):
    """When component load from rest, won't validate on name since there might
    be existing component with invalid name."""

    name = fields.Str(required=True)


class AnonymousDataTransferCopyComponentSchema(AnonymousAssetSchema, DataTransferCopyComponentSchema):
    """Anonymous data transfer copy component schema.

    Note inheritance follows order: AnonymousAssetSchema,
    AnonymousDataTransferCopyComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution
    order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._component.datatransfer_component import DataTransferCopyComponent

        # Inline component will have source=YAML.JOB
        # As we only regard full separate component file as YAML.COMPONENT
        return DataTransferCopyComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            _source=kwargs.pop("_source", ComponentSource.YAML_JOB),
            **data,
        )


# pylint: disable-next=name-too-long
class AnonymousDataTransferImportComponentSchema(AnonymousAssetSchema, DataTransferImportComponentSchema):
    """Anonymous data transfer import component schema.

    Note inheritance follows order: AnonymousAssetSchema,
    DataTransferImportComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution
    order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._component.datatransfer_component import DataTransferImportComponent

        # Inline component will have source=YAML.JOB
        # As we only regard full separate component file as YAML.COMPONENT
        return DataTransferImportComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            _source=kwargs.pop("_source", ComponentSource.YAML_JOB),
            **data,
        )


# pylint: disable-next=name-too-long
class AnonymousDataTransferExportComponentSchema(AnonymousAssetSchema, DataTransferExportComponentSchema):
    """Anonymous data transfer export component schema.

    Note inheritance follows order: AnonymousAssetSchema,
    DataTransferExportComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution
    order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._component.datatransfer_component import DataTransferExportComponent

        # Inline component will have source=YAML.JOB
        # As we only regard full separate component file as YAML.COMPONENT
        return DataTransferExportComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            _source=kwargs.pop("_source", ComponentSource.YAML_JOB),
            **data,
        )


class DataTransferCopyComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        component = AnonymousDataTransferCopyComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component


class DataTransferImportComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        component = AnonymousDataTransferImportComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component


class DataTransferExportComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        component = AnonymousDataTransferExportComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component
