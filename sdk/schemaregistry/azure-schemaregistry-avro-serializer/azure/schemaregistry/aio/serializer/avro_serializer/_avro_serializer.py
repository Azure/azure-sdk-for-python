# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import avro

from azure.schemaregistry.aio import SchemaRegistryClient


class SchemaRegistryAvroSerializer:
    def __init__(self):
        self._schema_dict = {}
