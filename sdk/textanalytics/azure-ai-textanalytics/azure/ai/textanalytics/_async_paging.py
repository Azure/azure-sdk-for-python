# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.async_paging import AsyncItemPaged


class AnalyzeHealthcareResultAsync(AsyncItemPaged):
    def __init__(self, *args, **kwargs):
        self.model_version = kwargs.pop('model_version')
        self.statistics = kwargs.pop('statistics')
        super(AnalyzeHealthcareResultAsync, self).__init__(*args, **kwargs)


class AnalyzeResultAsync(AsyncItemPaged):
    def __init__(self, *args, **kwargs):
        self.statistics = kwargs.pop('statistics')
        super(AnalyzeResultAsync, self).__init__(*args, **kwargs)
