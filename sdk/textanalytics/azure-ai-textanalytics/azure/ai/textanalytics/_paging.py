# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.paging import ItemPaged


class AnalyzeHealthcareResult(ItemPaged):
    def __init__(self, *args, **kwargs):
        self.model_version = kwargs.pop('model_version')
        self.statistics = kwargs.pop('statistics')
        super(AnalyzeHealthcareResult, self).__init__(*args, **kwargs)


class AnalyzeResult(ItemPaged):
    def __init__(self, *args, **kwargs):
        self.statistics = kwargs.pop('statistics')
        super(AnalyzeResult, self).__init__(*args, **kwargs)
