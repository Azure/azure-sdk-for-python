# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields

from azure.ai.ml._schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmStr
from azure.ai.ml.constants import AzureMLResourceType

module_logger = logging.getLogger(__name__)


class JobOutputSchema(metaclass=PatchedSchemaMeta):
    datastore_id = ArmStr(azureml_type=AzureMLResourceType.DATASTORE)
    path = fields.Str()
