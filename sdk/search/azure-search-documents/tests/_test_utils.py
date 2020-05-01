# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents import SynonymMap


def build_synonym_map_from_dict(synonym_map):
    sm = SynonymMap(name=synonym_map["name"], synonyms=synonym_map["synonyms"])
    for k, v in synonym_map.items():
        setattr(sm, k, v)
    return sm
