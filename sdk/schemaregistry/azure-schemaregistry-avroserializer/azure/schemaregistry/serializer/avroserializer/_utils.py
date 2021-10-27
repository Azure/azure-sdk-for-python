# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache
import avro

@lru_cache(maxsize=128)
def parse_schema(schema):
    return avro.schema.parse(schema)
