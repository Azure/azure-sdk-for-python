# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.paging import ItemPaged


class AnalyzeHealthcareEntitiesResult(ItemPaged):
    def __init__(self, *args, **kwargs):
        self.model_version = kwargs.pop('model_version')
        self.statistics = kwargs.pop('statistics')
        super(AnalyzeHealthcareEntitiesResult, self).__init__(*args, **kwargs)


class AnalyzeResult(ItemPaged):
    def __init__(self, *args, **kwargs):
        self.statistics = kwargs.pop('statistics', None)
        super(AnalyzeResult, self).__init__(*args, **kwargs)
