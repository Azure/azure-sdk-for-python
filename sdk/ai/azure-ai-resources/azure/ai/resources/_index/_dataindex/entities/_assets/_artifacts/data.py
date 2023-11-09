# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.entities._assets._artifacts.data import Data


@classmethod
def _resolve_cls_and_type(cls, data, params_override):
    from azure.ai.ml.entities._data_import.data_import import DataImport
    from azure.ai.resources.index._dataindex.entities.data_index import DataIndex
    print("Hellllooo")

    if "index" in data:
        return DataIndex, None

    if "source" in data:
        return DataImport, None
    return cls, None


# Override the _resolve_cls_and_type function in the Data class to support serilization of DataIndex
Data._resolve_cls_and_type = _resolve_cls_and_type
