# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from os.path import dirname, join, realpath
from azure.search.documents.indexes.models import SynonymMap

def test_create_synonym_map_from_file():
    CWD = dirname(realpath(__file__))
    path = join(CWD, "synonym_map.txt")
    synonym_map = SynonymMap.create_from_file('test', path)
    assert len(synonym_map.synonyms) == 2
    assert synonym_map.synonyms[0] == 'USA, United States, United States of America'
    assert synonym_map.synonyms[1] == 'Washington, Wash. => WA'