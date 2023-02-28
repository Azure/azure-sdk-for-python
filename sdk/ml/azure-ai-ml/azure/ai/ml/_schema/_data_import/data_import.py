# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.job.input_output_entry import DatabaseSchema, FileSystemSchema
from azure.ai.ml._utils._experimental import experimental
from ..core.fields import UnionField
from ..assets.data import DataSchema


@experimental
class DataImportSchema(DataSchema):
    source = UnionField([NestedField(DatabaseSchema), NestedField(FileSystemSchema)], required=True, allow_none=False)
