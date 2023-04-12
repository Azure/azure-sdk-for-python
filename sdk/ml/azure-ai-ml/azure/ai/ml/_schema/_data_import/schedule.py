# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import yaml
from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, FileRefField
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml._schema.schedule.trigger import CronTriggerSchema, RecurrenceTriggerSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from ..core.fields import UnionField
from .data_import import DataImportSchema


class ImportDataFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs) -> "DataImport":
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        data_import_dict = yaml.safe_load(data)

        from azure.ai.ml.entities._data_import.data_import import DataImport

        return DataImport._load(  # pylint: disable=no-member
            data=data_import_dict,
            yaml_path=self.context[BASE_PATH_CONTEXT_KEY] / value,
            **kwargs,
        )


@experimental
class ImportDataScheduleSchema(ResourceSchema):
    name = fields.Str(attribute="name", required=True)
    display_name = fields.Str(attribute="display_name")
    trigger = UnionField(
        [
            NestedField(CronTriggerSchema),
            NestedField(RecurrenceTriggerSchema),
        ],
    )
    import_data = UnionField(
        [
            ImportDataFileRefField,
            NestedField(DataImportSchema),
        ]
    )
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    is_enabled = fields.Boolean(dump_only=True)
    provisioning_state = fields.Str(dump_only=True)
    properties = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
