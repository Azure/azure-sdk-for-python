# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.paging import ItemPaged
from azure.core.async_paging import AsyncItemPaged


class HealthcareItemPaged(ItemPaged):
    def __init__(self, *args, **kwargs):
        super(HealthcareItemPaged, self).__init__(*args, **kwargs)
        self.model_version = kwargs.pop('model_version')
        self.statistics = kwargs.pop('statistics')

class AsyncHealthcareItemPaged(AsyncItemPaged):
    def __init__(self, *args, **kwargs):
        super(AsyncHealthcareItemPaged, self).__init__(*args, **kwargs)
        self.model_version = kwargs.pop('model_version')
        self.statistics = kwargs.pop('statistics')

class AnalyzeItemPaged(ItemPaged):
    def __init__(self, *args, **kwargs):
        super(AnalyzeItemPaged, self).__init__(*args, **kwargs)
        self.statistics = kwargs.pop('statistics')

class AsyncAnalyzeItemPaged(AsyncItemPaged):
    def __init__(self, *args, **kwargs):
        super(AsyncAnalyzeItemPaged, self).__init__(*args, **kwargs)
        self.statistics = kwargs.pop('statistics')
